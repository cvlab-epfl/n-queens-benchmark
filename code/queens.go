package main

import (
	"flag"
	"fmt"
	"math"
	"os"
	"runtime"
	"sync"
	"time"
)

//-----------------------------------------------------
//                   SEQUENTIAL
//=====================================================

func allQueensRec(n int) int {

//	col := make([]bool, n, n)
//	dg1 := make([]bool, 2*n, 2*n)
//	dg2 := make([]bool, 2*n, 2*n)
	
	var col[32]bool
	var dg1[64]bool
	var dg2[64]bool

	for i := 0; i < n; i++ {
		col[i] = true
	}
	for i := 0; i < 2*n; i++ {
		dg1[i] = true
		dg2[i] = true
	}

	return allQueensAux(n, 0, col, dg1, dg2)
}

func allQueensAux(n int, i int, col [32]bool, dg1 [64]bool, dg2 [64]bool) int {

	if n == i {
		return 1
	}
	nsol := 0
	for j := 0; j < n; j++ {
		if col[j] && dg1[i+j] && dg2[i-j+n] {

			col[j] = false
			dg1[i+j] = false
			dg2[i-j+n] = false

			nsol += allQueensAux(n, i+1, col, dg1, dg2)

			col[j] = true
			dg1[i+j] = true
			dg2[i-j+n] = true
		}
	}
	return nsol
}

//-----------------------------------------------------
//                   PARALLEL
//=====================================================

// One worker per column
func allQueensPar1(nd int) int {

	var wg sync.WaitGroup
	wg.Add(nd)
    // Allow go to run on multiple cores
	runtime.GOMAXPROCS(8)

	sols := make([]int, nd)
    
	f := func(wg *sync.WaitGroup, n int, j int) {
		sols[j] = allQueensCol(n, j)
		wg.Done()
	}
	for j := 0; j < nd; j++ {
		go f(&wg, nd, j)
	}
	wg.Wait()

	nsol := sols[0]
	for j := 1; j < nd; j++ {
		nsol += sols[j]
	}
	return nsol
}

// Fixed number of workers per column
func allQueensPar2(nd int, np int) int {

	var wg sync.WaitGroup
	wg.Add(np)

	runtime.GOMAXPROCS(8)

	sols := make([]int, nd)

	f := func(wg *sync.WaitGroup, n int, k int) {
		for j := k; j < nd; j += np {
			sols[j] = allQueensCol(n, j)
		}
		wg.Done()
	}
	for k := 0; k < np; k++ {
		go f(&wg, nd, k)
	}
	wg.Wait()

	nsol := sols[0]
	for j := 1; j < nd; j++ {
		nsol += sols[j]
	}
	return nsol
}

func allQueensPar4(nd int, np int) int {

	if nd <= np {
		return allQueensPar1(nd)
	}

	runtime.GOMAXPROCS(8)

	nthreads := 0
	sols := make([]int,  nd,nd)
	done := make([]bool, nd,nd)
	nsol := 0

	f := func(n int, j int, t int) {
		//fmt.Println(n,j,t)
		sols[t] = 0
		sols[t] = allQueensCol(n,j)
		done[j] = true
		//fmt.Println(n,j,t,sols[t])
	}

	// np < nd
	for nthreads = 0; nthreads < np; nthreads++ {
		go f(nd,nthreads,nthreads)
	}

	for nthreads < nd {
		time.Sleep(1 * time.Millisecond)
		for p := 0; p < np; p++ {
			if sols[p] > 0 { // The thread has completed.
				nsol += sols[p]
				sols[p] = 0
				go f(nd,nthreads,p)
				nthreads++
				if nthreads == nd {
					break
				}
			}
		}
	}
	

	flag := true
	for flag {
		time.Sleep(1 * time.Millisecond)
		flag = false
		for j := 0; j < nd; j++ {
			if !done[j]{
				flag = true
		}
		}
	}
	for j := 0; j < nd; j++{
		nsol += sols[j]
	}
	
	//fmt.Println(sols)

	return nsol
}

func allQueensCol(n int, j int) int {

//	col := make([]bool, n, n)
//	dg1 := make([]bool, 2*n, 2*n)
//	dg2 := make([]bool, 2*n, 2*n)
	
	var col[32]bool
	var dg1[64]bool
	var dg2[64]bool

	for i := 0; i < n; i++ {
		col[i] = true
	}
	for i := 0; i < 2*n; i++ {
		dg1[i] = true
		dg2[i] = true
	}
	col[j] = false
	dg1[j] = false
	dg2[n-j] = false

	return allQueensAux(n, 1, col, dg1, dg2)
}

//---------------------------------
//
//---------------------------------

func allQueensTst(nd int, np int, nt int) (float64,float64) {
	nsol := 0
	mean := 0.0
	vari := 0.0
	
	if(nt==0){
		return 0.0,0.0
	}
	
	for it := 0; it < nt; it++ {
		t0 := time.Now()
		if np == 0 {
			nsol = allQueensRec(nd)
		} else if np == 1 {
			nsol = allQueensPar1(nd)
		} else {
			nsol = allQueensPar4(nd, np)
		}
		t1 := time.Now()
		dt := t1.Sub(t0).Seconds()
		
		mean += dt
		vari += dt * dt
	}
	
	numb := float64(nt)
	mean = mean / numb
	if(nt>1){
		vari  = vari  / numb  - mean*mean
		vari *= (numb / (numb - 1.0))
		vari  = math.Sqrt(vari);
	} else{
		vari = 0.0
	}
	
	fmt.Printf("Found %4d solutions to the %2d queens problem in %f seconds (var %f,np = %d).\n", nsol, nd, mean,vari,np)
	return mean,vari

}

func main() {

	n0Ptr := flag.Int("n0", 10, "Min chessboard dimension")
	n1Ptr := flag.Int("n1", 12, "Max chessboard dimension")
	// ntPtr := flag.Int("nt", 10, "Number of attempts for timing purposes")
	//	npPtr := flag.Int("np", 4,  "Max number of parallel processes")

	flag.Parse()

	n0 := *n0Ptr
	n1 := *n1Ptr
	//  nt := *ntPtr
	//	Np := *npPtr

//	n0 = 17
//	n1 = 18
//	nt = 2

	fo, err := os.Create(fmt.Sprintf("/Users/fua/tmp/golang.%d.%d.var",n0,n1))
	nps := []int{0,1}
	row := make([]float64, 3*len(nps)+1, 3*len(nps)+1)
	if err != nil {
		panic(err)
	}

	for nd := n0; nd <= n1; nd++ {
		nt := 0
		row[0] = float64(nd)
		for i := range nps {
			np := nps[i]
			
			if(np<1){
				if nd<15 {
					nt = 20
				} else if nd<18 {
					nt = 10
				} else if(nd<19){
					nt = 0
				}
			} else if np<2 {
				if nd<15 {
					nt = 20
				} else if nd<18 {
					nt = 10
				} else if(nd<19){
					nt = 5
				}
			}
			
			mean,vari := allQueensTst(nd,np,nt)
			row[3*i+1] = float64(np)
			row[3*i+2] = mean
			row[3*i+3] = vari
		}
		fmt.Fprintln(fo, row)
	}
}
