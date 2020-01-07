#include <iostream>
#include <pthread.h>
#include <time.h>

int fib(int n){
  if(n<3)
    return 1;
  else
      return fib(n -1) + fib (n -2);
}

void *workerF(void *ptr){

  int ns[] = {30,31,32,33,34,35,36,37,38,39};
  int sum = 0;
  for (int it=0;it<10;it++){
        int n = ns[rand()%10];
        int f = fib(n);
      
        if(n<0)
            printf("Fib %d: %d\n",n,f);
      sum += f;
    }
    printf("Sum %d\n",sum);
    return NULL;
}

#define N_WORKERS   8
int main()
{
    
    
    pthread_t       workers[N_WORKERS];
    int                 args[N_WORKERS];
    int         i;
    
    clock_t startTime = clock();
    for (int i = 0; i < N_WORKERS ; ++i) {
        (*workerF)(NULL);
    }
    float dt = (float)(clock()-startTime)/(float)(CLOCKS_PER_SEC);
    printf("Sequential %f\n",dt);
    
    startTime = clock();
    for (i = 0; i < N_WORKERS; ++i)
    {
        args[i] = i;
        pthread_create(&workers[i], NULL, workerF, args + i);
    }
    for (i = 0; i < N_WORKERS; ++i)
    {
        pthread_join(workers[i], NULL);
    }
    dt = (float)(clock()-startTime)/(float)(CLOCKS_PER_SEC);
    printf("Parallel  %f\n",dt);
    
    return 0;
}
