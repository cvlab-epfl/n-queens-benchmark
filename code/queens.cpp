#include <iostream>
#include <time.h>
#include <pthread.h>
#include <stdio.h>
#include <chrono>
#include <unistd.h>
#include <math.h>
#include <vector>
#include <array>
#include <functional>
#include <future>
#include <fstream>
#include <memory>

#include <cstring>
#include <cassert>
typedef std::chrono::high_resolution_clock Clock;
using namespace std;

#define INTRODUCE_BUG 0
#define ALLOC_ON_HEAP (0 && !INTRODUCE_BUG)
#define MALLOC_OLD    (0 && !ALLOC_ON_HEAP)
#define USE_UINT      1
#define MAX_N_QUEENS  32

#if ALLOC_ON_HEAP
	typedef array<bool,2*MAX_N_QUEENS> BoolArray;
#elif MALLOC_OLD
	typedef bool *BoolArray;
#elif USE_UINT
	typedef uint8_t *BoolArray;
#else
	typedef vector<uint8_t> BoolArray;
#endif

//-------------------------------------------------------------------
//                          SEQUENTIAL
//-------------------------------------------------------------------

#if USE_UINT
int allQueensAux(int n,int i,uint8_t *col,uint8_t *dg1,uint8_t *dg2)
#else
int allQueensAux(int n,int i,BoolArray& col,BoolArray& dg1,BoolArray& dg2)
#endif
{
	if (n == i) {
		return 1;
	}
	int nsol = 0;
	for (int j = 0; j < n; j++) {
		if (col[j] && dg1[i+j] && dg2[i-j+n]) {
			col[j] = false;
			dg1[i+j] = false;
			dg2[i-j+n] = false;

			nsol += allQueensAux(n, i+1, col, dg1, dg2);

			col[j] = true;
			dg1[i+j] = true;
			dg2[i-j+n] = true;
		}
	}
	return nsol;
}

int allQueensRec(int n)
{
#if INTRODUCE_BUG
	// dg1 and dg2 are deliberately too small. The program runs but the results are meaningless.
	bool *col = new bool[n];
	bool *dg1 = new bool[n];
	bool *dg2 = new bool[n];
	memset((void *)col,1,n*sizeof(bool));
	memset((void *)dg1,1,n*sizeof(bool));
	memset((void *)dg2,1,n*sizeof(bool));
#elif ALLOC_ON_HEAP
	//fprintf(stderr,"h\n");
	BoolArray col,dg1,dg2;
	col.fill(true);
	dg1.fill(true);
	dg2.fill(true);
#elif MALLOC_OLD
	//fprintf(stderr,"m\n");
	bool *col = new bool[n];
	bool *dg1 = new bool[2*n];
	bool *dg2 = new bool[2*n];
	memset((void *)col,1,n*sizeof(bool));
	memset((void *)dg1,1,2*n*sizeof(bool));
	memset((void *)dg2,1,2*n*sizeof(bool));
#elif USE_UINT
	vector<uint8_t> col(n,   true);
	vector<uint8_t> dg1(2*n, true);
	vector<uint8_t> dg2(2*n, true);
#else
	BoolArray col(n,   true);
	BoolArray dg1(2*n, true);
	BoolArray dg2(2*n, true);
#endif


#if USE_UINT
	int nsol = allQueensAux(n,0,col.data(),dg1.data(),dg2.data());
#else
	int nsol = allQueensAux(n,0,col,dg1,dg2);
#endif

#if MALLOC_OLD
	free (col);
	free (dg1);
	free (dg2);
#endif
	return nsol;
}

//-------------------------------------------------------------------
//                       PARALLEL
//-------------------------------------------------------------------

int allQueensCol(int n,int j) {

#if INTRODUCE_BUG
	bool *col = new bool[n];
	bool *dg1 = new bool[n];
	bool *dg2 = new bool[n];
	memset((void *)col,1,n*sizeof(bool));
	memset((void *)dg1,1,n*sizeof(bool));
	memset((void *)dg2,1,n*sizeof(bool));
#elif ALLOC_ON_HEAP
	BoolArray col,dg1,dg2;
	col.fill(true);
	dg1.fill(true);
	dg2.fill(true);
#elif MALLOC_OLD
	bool *col = new bool[n];
	bool *dg1 = new bool[2*n];
	bool *dg2 = new bool[2*n];
	memset((void *)col,1,n*sizeof(bool));
	memset((void *)dg1,1,2*n*sizeof(bool));
	memset((void *)dg2,1,2*n*sizeof(bool));
#elif USE_UINT
	vector<uint8_t> col(n,   true);
	vector<uint8_t> dg1(2*n, true);
	vector<uint8_t> dg2(2*n, true);
#else
	BoolArray col(n,  true);
	BoolArray dg1(2*n,true);
	BoolArray dg2(2*n,true);
#endif
	col[j]   = false;
	dg1[j]   = false;
	dg2[n-j] = false;

#if USE_UINT
	int ncol = allQueensAux(n,1,col.data(),dg1.data(),dg2.data());
#else
	int ncol = allQueensAux(n,1,col, dg1, dg2);
#endif

	// Is the destructor called automatically?
#if MALLOC_OLD
	free(col);
	free(dg1);
	free(dg2);
#endif
	return ncol;
}

struct pthread_a {
	int nsol;
    int nd;
    int np;
    int p;
};


int allQueensPara(int nd){

	vector<future<int>> running_tasks;

	for(int col = 0; col < nd; col++){
		running_tasks.push_back(
				async(std::launch::async, [=]() {return allQueensCol(nd,col);}
				));
	}

	// Wait for results
	int nsol_sum = 0;
	for(auto& f : running_tasks) {
		nsol_sum += f.get();
	}

	return nsol_sum;
}

static void *worker1(void *argp){
	struct pthread_a *args = (struct pthread_a *)argp;
	args->nsol = allQueensCol(args->nd,args->p);
	//pthread_exit(NULL);
	return NULL;
}

int allQueensPar1(int nd){

	pthread_t *thrd   = new pthread_t[nd];
	pthread_a *args   = new pthread_a[nd];

	for (int i=0 ; i < nd ; i++){
		pthread_a *argp = args+i;
		pthread_t *thrp = thrd+i;

		argp->nd = nd;
		argp->p  = i;

		pthread_create(thrp,NULL,worker1,argp);
	}
	int nsol = 0;
	for (int p=0 ; p < nd ; p++){
		pthread_join(thrd[p],NULL);
		nsol += args[p].nsol;
	}
	free(thrd);
	free(args);
	return nsol;
}

static void *worker2(void *argp){
	struct pthread_a *args = (struct pthread_a *)argp;
	//fprintf(stderr,"workerF: %d %d %d\n",args->nd,args->np,args->p);
	args->nsol = 0;
	for (int j = args->p ; j < args->nd ; j+= args->np){
		args->nsol += allQueensCol(args->nd,j);
	}

	return NULL;
}

int allQueensPar2(int nd,int np){

	pthread_t *thrd   = new pthread_t[np];
	pthread_a *args   = new pthread_a[np];

	for (int p=0 ; p < np ; p++){
		pthread_a *argp = args+p;
		pthread_t *thrp = thrd+p;

		argp->nd = nd;
		argp->np = np;
		argp->p  = p;

		pthread_create(thrp,NULL,worker2,argp);
	}
	for (int p=0 ; p < np ; p++){
		pthread_join(thrd[p],NULL);
	}
	int nsol = 0;
	for (int p=0 ; p < np ; p++){
		nsol += args[p].nsol;
	}
	free(thrd);
	free(args);
	return nsol;
}

#define MAX_NUM_THREADS 14
int allQueensPar3(int nd,int np){

	pthread_t thrd[MAX_NUM_THREADS];
	pthread_a args[MAX_NUM_THREADS];

	assert(np<=MAX_NUM_THREADS);

	for (int p=0 ; p < np ; p++){
		pthread_a *argp = args+p;
		pthread_t *thrp = thrd+p;

		argp->nd = nd;
		argp->np = np;
		argp->p  = p;

		pthread_create(thrp,NULL,worker2,argp);
	}
	for (int p=0 ; p < np ; p++){
		pthread_join(thrd[p],NULL);
	}
	int nsol = 0;
	for (int p=0 ; p < np ; p++){
		nsol += args[p].nsol;
	}
	return nsol;
}

static void *worker4(void *argp){
	struct pthread_a *args = (struct pthread_a *)argp;
	//fprintf(stderr,"workerF: %d %d %d\n",args->nd,args->np,args->p);
	args->np = 0;   // The thread is busy.
	args->nsol = allQueensCol(args->nd,args->p);
	pthread_exit(NULL);
	return NULL;
}

int allQueensPar4(int nd,int np){

	pthread_t *thrd = new pthread_t[np];
	pthread_a *args = new pthread_a[nd];
	int nsol=0, nthreads = 0;

	for (int p=0 ; p < nd ; p++){
		pthread_a *argp = args+p;
		argp->nd   = nd;
		args->np   = 0;
		argp->p    = p;
		argp->nsol = 0;
	}

	for (nthreads=0 ; nthreads < min(nd,np) ; nthreads++){
		pthread_a *argp = args+nthreads;
		pthread_t *thrp = thrd+nthreads;
		pthread_create(thrp,NULL,worker4,argp);
	}

	if(nthreads==nd){
		for (int p=0 ; p < np ; p++){
			pthread_join(thrd[p],NULL);
			nsol += args[p].nsol;
		}
		return nsol ;
	}

	while(nthreads<nd){
		usleep(1e3);
		for (int p=0 ; p < np ; p++){
			pthread_a *argp = args+p;
			pthread_t *thrp = thrd+p;
			if(argp->nsol>0){ // The thread has completed.
				nsol +=  argp->nsol;
				argp->nsol = 0;
				argp->p = nthreads;
				pthread_create(thrp,NULL,worker4,argp);
				nthreads++;
				if(nthreads==nd)
					break;
			}
		}
	}

	for (int p=0 ; p < np ; p++){
		pthread_join(thrd[p],NULL);
		nsol += args[p].nsol;
	}
	free(args);
	free(thrd);

	return nsol;
}


//-------------------------------------------------------------------
//                       BENCHMARK
//-------------------------------------------------------------------

void allQueensTst(double *perf,int nd,int np, int nt)
{
	int nsol;
	double mean = 0.0, var = 0.0;

	if(0==nt){
		perf[0]=0.0;
		perf[1]=0.0;
		return ;
	}

	for (int t=0;t<nt;t++){
		auto t1 = Clock::now();
		if(np>1)
			nsol=allQueensPar4(nd,np);
		else if(1==np)
			nsol=allQueensPara(nd);
		else
			nsol=allQueensRec(nd);
		auto   t2 = Clock::now();
		double dt = (double)(t2-t1).count()/1e9;

		mean += dt;
		var  += dt * dt;
	}

	double numb = (double)nt;
	mean = mean / numb;
	if(nt>1){
		var  = var  / numb  - mean*mean;
		var *= (numb / (numb - 1.0));
		var  = sqrt(var);
	}
	else
		var = 0.0;

	printf("Found %5d solutions to the %2d queen problem in %f s per attempt. (var %f, np %d, nt %d)\n",nsol,nd,mean,var,np,nt);
	perf[0]=mean;
	perf[1]=var;
}

//-------------------------------------------------------------------
//                        OPTIONS
//-------------------------------------------------------------------

#define ReadOptionInt(Nom,Val)       ReadOptionInt_i(Nom, Val,&argc,argv)

void RemoveOption(int NumeroOption,int *pargc,char **argv)
{
  int i;

  for (i = NumeroOption; i < *pargc - 1; i++)
    argv[i] = argv[i + 1];
  *pargc=(*pargc)-1;
}

int ReadOptionString_i(const char *Nom, char *String,int  *pargc,char **argv)
{
  int i;

  if(pargc&&argv){
    for (i = 1; i < *pargc; i++)
      if (strcmp(argv[i], Nom) == 0) {
        RemoveOption(i,pargc,argv);
        if (i < *pargc) {
          strcpy(String, argv[i]);
          RemoveOption(i,pargc,argv);
          return (1);
        }
      }
  }
  return (0);
}

int ReadOptionInt_i(const char *Nom,int *Val,int *pargc,char **argv)
{
  char Xarg[256];

  if (ReadOptionString_i(Nom, Xarg,pargc,argv))
    if (sscanf(Xarg, "%d", Val))
        return (1);
  return (0);
}

//-------------------------------------------------------------------
//                        MAIN
//-------------------------------------------------------------------

//void foo(vector<uint8_t>& x)
//{
//	x[0]=2;
//	x[1]=3;
//	for (int i=0; i<1e9;i++)
//		x[i-1]=7;
//}

int main(int argc,char **argv) {

	char fileName[80];
	double perf[2];
	int n0=8,n1=19;

	ReadOptionInt("-n0",&n0);
	ReadOptionInt("-n1",&n1);

//	{
//		vector<uint8_t> col(8,1);
//		fprintf(stderr,"%d %d\n",col[0],col[1]);
//		foo(col);
//		fprintf(stderr,"%d %d\n",col[0],col[1]);
//		fprintf(stderr,"Done\n");
//		exit(0);
//	}

//	int nt=5;
//	allQueensTst(perf,n0,1,nt);
//	nt=10;
//	allQueensTst(perf,n0,1,nt);
//	nt=20;
//	allQueensTst(perf,n0,1,nt);
//	exit(0);

	sprintf(fileName,"/Users/fua/tmp/cplus.%d.%d.var",n0,n1);
	FILE *fp = fopen(fileName, "w");

	fprintf(stderr,"Find all solutions from %d to %d\n",n0,n1);

	for (int nd = n0; nd < n1 ; nd++){

		fprintf(fp,"%d ",nd);
		int nt = 0;
		for (int np = 0 ; np < 2 ; np+=1){
			if(np<1){
				if(nd<15)
					nt = 20;
				else if (nd<17)
					nt = 10;
				else if(nd<19)
					nt = 0;
			}
			else if (np<2){
				if(nd<15)
					nt = 20;
				else if (nd<17)
					nt = 10;
				else if(nd<19)
					nt = 5;
			}
#if 0
			auto t1 = Clock::now();
			allQueensTst(perf,nd,np,nt);
			auto   t2 = Clock::now();
			double dt = (double)(t2-t1).count()/1e9;
			if(nt>1)
				dt = dt / nt;
			fprintf(fp," %f %f %f",perf[0],perf[1],dt);
#else
			allQueensTst(perf,nd,np,nt);
			fprintf(fp," %f %f ",perf[0],perf[1]);
#endif
		}
		fprintf(fp,"\n");
	}

	fclose(fp);
	return(0);
}
