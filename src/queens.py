#!/usr/bin/env python3

import numpy as np

from pathlib import Path
from timeit import timeit
from functools import partial
from multiprocessing import Pool as Pool_proc
import click

import matplotlib
import numba
from numba import njit, prange

def allQueensAux_python(n, i, col, dg1, dg2):
    # All rows are filled. Increment the counter and stop the recursion
    if n == i : 
        return 1
    # Try putting a queen in each cell of row i    

    nsol = 0
    for j in range(n):
        if (col[j] and dg1[i+j] and dg2[i-j+n]): 
            
            col[j]     = False  # Mark column j as occupied
            dg1[i+j]   = False  # Mark diagonal i+j as occupied
            dg2[i-j+n] = False  # Mark diagonal i-j as occupied

            nsol += allQueensAux_python(n, i+1, col, dg1, dg2)
            
            col[j]     = True   # Unmark column j
            dg1[i+j]   = True   # Unmark diagonal i+j
            dg2[i-j+n] = True   # Unmark diagonal i-j
            
    return nsol


def allQueens_python(n):   
    # Arrays used to flag available columns and diagonals
    col = np.ones(n, dtype=bool)
    dg1 = np.ones(2*n, dtype=bool)
    dg2 = np.ones(2*n, dtype=bool)
    
    return allQueensAux_python(n,0,col,dg1,dg2)


@njit(nogil=True) #Numba decorator
def allQueensAux_numba(n, i, col, dg1, dg2):
    # All rows are filled. Increment the counter and stop the recursion
    if n == i :
        return 1

    # Try putting a queen in each cell of row i
    nsol = 0

    for j in range(n):
        if (col[j] and dg1[i+j] and dg2[i-j+n]): 

            col[j]     = False  # Mark column j as occupied
            dg1[i+j]   = False  # Mark diagonal i+j as occupied
            dg2[i-j+n] = False  # Mark diagonal i-j as occupied

            nsol += allQueensAux_numba(n,i+1,col,dg1,dg2)
            
            col[j]     = True   # Unmark column j
            dg1[i+j]   = True   # Unmark diagonal i+j
            dg2[i-j+n] = True   # Unmark diagonal i-j
            
    return nsol


@njit(nogil=True) #Numba decorator
def allQueens_numba(n, i=0, col=None, dg1=None, dg2=None):
    # The array types must be numba compatible
    col = np.ones(n,dtype=numba.boolean)
    dg1 = np.ones(2*n,dtype=numba.boolean)
    dg2 = np.ones(2*n,dtype=numba.boolean)
    
    return allQueensAux_numba(n,0,col,dg1,dg2)


@njit(nogil=True)   
def allQueensCol(n,j):
    col = np.ones(n,dtype=numba.boolean)
    dg1 = np.ones(2*n,dtype=numba.boolean)
    dg2 = np.ones(2*n,dtype=numba.boolean)
    # Put a queen in cell j of the first row
    col[j] = False
    dg1[j] = False
    dg2[n-j] = False
    # Fills the rest of the board starting with the second row
    return allQueensAux_numba(n,1,col,dg1,dg2)


@njit(nogil=True, parallel=True)
def allQueensPara(n):
    nsol = 0
    for j in prange(n):
        nsol += allQueensCol(n,j)
    return nsol


def poolWorker(n,j):
    return allQueensCol(n,j)

def allQueensPool(n, pool):
    nsols = pool.map(partial(poolWorker,n), range(n))
    return (sum(nsols))
    


def timeit_and_print(statement, number=10, name=''):
    time_elapsed = timeit(statement,number=number)
    
    time_per_iter = time_elapsed/number
    
    print('{ti:04f} s/iter | {tt:04f} s total | {name}'.format(
        ti = time_per_iter,
        tt = time_elapsed,
        name = name,
    ))
    return time_per_iter


def timeit_and_var(statement, number=10, name=''):
    
    if(number<1):
        return 0.0,0.0
    
    mean = 0.0
    var  = 0.0
    
    for i in range(number):
        dt = timeit(statement, number=1)
        mean += dt
        var  += dt*dt
        
    numb = float(number)
    mean = mean / numb
    var  = var  / numb  - mean*mean
    var *= (numb / (numb - 1.0))
    var  = np.sqrt(var)
    
    print('{ti:04f} s/iter | {tt:04f} variance | {name}'.format(
        ti = mean,
        tt = var,
        name = name,
    ))
    return mean, var


VARIANTS = {
    'python': allQueens_python,
    'numba_seq': allQueens_numba,
    'numba_para': allQueensPara,
    'pool': allQueensPool,
}


@click.command()
@click.option('--num_from', type=int, default=8)
@click.option('--num_to', type=int, default=16)
@click.option('--variant', type=click.Choice(VARIANTS.keys()))
@click.option('--output', type=click.Path())
def main(num_from, num_to, variant, output):

    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)

    with output.open('w') as f_out:
        f_out.write('n	mean	var\n')

        # create the pool once and reuse it
        with Pool_proc() as pool:

            func = VARIANTS[variant]
            if variant == 'pool':
                func = partial(func, pool=pool)

            # run once to dp the numba compilation before time is measured
            func(8)

            for num_queens in range(num_from, num_to+1):
                if num_queens <= 10 and variant != 'python':
                    num_iter = 1000
                elif num_queens <= 15:
                    num_iter = 10
                else:
                    num_iter = 5

                mean, var = timeit_and_var(
                    partial(func, num_queens), 
                    number=num_iter, 
                    name=f'{variant} {num_queens} queens (nt {num_iter})',
                )

                f_out.write(f'{num_queens:02d}	{mean:f}	{var:f}\n')
                f_out.flush() #write after every row in case we abort in the middle


if __name__ == '__main__':
    main()
