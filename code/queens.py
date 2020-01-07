#!/usr/bin/env python3
#-----------------------------------------------------------------------------
#                         
#=============================================================================

#%---------------------------------------------------------------------------
#                                IMPORTS
#-----------------------------------------------------------------------------
#%%

import numpy as np
import numba
from   numba import njit,prange

from timeit    import timeit
from functools import partial
from multiprocessing import Pool as Pool_proc

from util import addToFile
from math import sqrt
#%%---------------------------------------------------------------------------
#                            SEQUENTIAL          
#-----------------------------------------------------------------------------

def allQueensRec(n):   
    # Arrays used to flag available columns and diagonals
    col = np.ones(n,dtype=bool)
    dg1 = np.ones(2*n,dtype=bool)
    dg2 = np.ones(2*n,dtype=bool)
    
    return allQueensAux(n,0,col,dg1,dg2)
    
def allQueensAux(n,i,col,dg1,dg2):
    # All rows are filled. Stop the recursion.
    if n == i : 
        return 1
    # Try putting a queen in each cell of row i 
    nsol = 0
    for j in range(n):
        if (col[j] and dg1[i+j] and dg2[i-j+n]): 
            
            col[j]     = False  # Mark column j as occupied
            dg1[i+j]   = False  # Mark diagonal i+j as occupied
            dg2[i-j+n] = False  # Mark diagonal i-j as occupied

            nsol+=allQueensAux(n,i+1,col,dg1,dg2)
            
            col[j]     = True   # Unmark column j
            dg1[i+j]   = True   # Unmark diagonal i+j
            dg2[i-j+n] = True   # Unmark diagonal i-j
            
    return nsol

if __name__ == "__main__":
    ns = allQueensRec(8)
    print('Simple :',ns)
#%%
@njit(nogil=True) #Numba decorator
def allQueensNmb(n,i=0,col=None,dg1=None,dg2=None):
    # The array types must be numba compatible
    col = np.ones(n,dtype=numba.boolean)
    dg1 = np.ones(2*n,dtype=numba.boolean)
    dg2 = np.ones(2*n,dtype=numba.boolean)
    
    return allQueensNumba(n,0,col,dg1,dg2)
    
@njit(nogil=True) #Numba decorator
def allQueensNumba(n,i,col,dg1,dg2):
    # All rows are filled. Stop the recursion
    if n == i :
        return 1
    # Try putting a queen in each cell of row i
    nsol=0
    for j in range(n):
        if (col[j] and dg1[i+j] and dg2[i-j+n]): 

            col[j]     = False  # Mark column j as occupied
            dg1[i+j]   = False  # Mark diagonal i+j as occupied
            dg2[i-j+n] = False  # Mark diagonal i-j as occupied

            nsol+=allQueensNumba(n,i+1,col,dg1,dg2)
            
            col[j]     = True   # Unmark column j
            dg1[i+j]   = True   # Unmark diagonal i+j
            dg2[i-j+n] = True   # Unmark diagonal i-j
            
    return nsol

if __name__ == "__main__":
    ns = allQueensNmb(8)
    print('Numba  :',ns)
#%%---------------------------------------------------------------------------
#                            PARALLEL         
#-----------------------------------------------------------------------------
#%%
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
    return allQueensNumba(n,1,col,dg1,dg2)

    
if __name__ == "__main__":
    nsol = 0
    for j in range(8):
        nsol += allQueensCol(8,j)
    print('Par    :',nsol)
#%%
@njit(nogil=True,parallel=True)
def allQueensPara(n):
    nsol = 0
    for j in prange(n):
        nsol+=allQueensCol(n,j)
    return nsol

#@njit()
def poolWorker(n,j):
    return allQueensCol(n,j)

def allQueensPool(n,np=None):
    if(np is None):
        with Pool_proc() as pool:
            nsols= pool.map(partial(poolWorker,n),prange(n))
            return (sum(nsols))
    else:
        with Pool_proc(processes=np) as pool:
            nsols= pool.map(partial(poolWorker,n),prange(n))
            return (sum(nsols))
    
if __name__ == "__main__":
    print('Seq    :' ,allQueensPara(8))
    print('Pool   :',allQueensPool(8,None))
#%%---------------------------------------------------------------------------
#                            TEST
#-----------------------------------------------------------------------------
#%%
def timeit_and_print(statement,number=10, name=''):
    time_elapsed = timeit(statement,number=number)
    
    time_per_iter = time_elapsed/number
    
    print('{ti:04f} s/iter | {tt:04f} s total | {name}'.format(
        ti = time_per_iter,
        tt = time_elapsed,
        name = name,
    ))
    return time_per_iter

def timeit_and_var(statement,number=10, name=''):
    
    if(number<1):
        return 0.0,0.0
    
    mean = 0.0
    var  = 0.0
    
    for i in range(number):
        dt = timeit(statement,number=1)
        mean += dt
        var  += dt*dt
        
    numb = float(number)
    mean = mean / numb
    var  = var  / numb  - mean*mean
    var *= (numb / (numb - 1.0))
    var  = sqrt(var)
        
    
    print('{ti:04f} s/iter | {tt:04f} variance | {name}'.format(
        ti = mean,
        tt = var,
        name = name,
    ))
    return mean,var
#%%
print('----------------------------------------------------------')
for n in range(8,19):
    rpt1=0
    rpt2=0
    rpt3=0
    rpt4=0
    if(n<15):
        rpt1=20
        rpt2=20
        rpt3=20
        rpt4=20
    elif(n<17):
        rpt2=10
        rpt3=10
        rpt4=10
    else:
        rpt3=3
        rpt4=3
        
    rpt1 = 0
    
    m1,v1=timeit_and_var(partial(allQueensRec,n),  name='Sequential python {:2d}'.format(n),number=rpt1) 
    m2,v2=timeit_and_var(partial(allQueensNmb,n),  name='Sequential numba  {:2d}'.format(n),number=rpt2)
    m3,v3=timeit_and_var(partial(allQueensPara,n), name='Parallel  para    {:2d}'.format(n),number=rpt3)
    m4,v4=timeit_and_var(partial(allQueensPool,n), name='Parallel  pool    {:2d}'.format(n),number=rpt4)
    addToFile('/Users/fua/tmp/python.var','{:2d} {:f} {:f} {:f} {:f} {:f} {:f} {:f} {:f}\n'.format(n,m1,v1,m2,v2,m3,v3,m4,v4),newP=(8==n))
    print('----------------------------------------------------------')
#%%
print('----------------------------------------------------------')
rpt = 0
if(rpt>0):
    for n in range(15,19):
        m1,v1=0.0
        m2.v2=0.0
        m3,v3=timeit_and_var(partial(allQueensPara,n), name='Parallel  para    {:2d}'.format(n),number=rpt)
        m4,v4=timeit_and_var(partial(allQueensPool,n), name='Parallel  pool    {:2d}'.format(n),number=rpt)
        addToFile('/Users/fua/tmp/python.var','{:2d} {:f} {:f} {:f} {:f} {:f} {:f} {:f} {:f}\n'.format(n,m1,v1,m2,v2,m3,v3,m4,v4),newP=False)
#%%
print('----------------------------------------------------------')
rpt = 0
if(rpt>0):
    for n in range(15,19):
        dt1=0.0
        dt2=0.0
        dt3=0.0
        dt4=timeit_and_print(partial(allQueensPool,n), name='Parallel  pool    {:2d}'.format(n),number=rpt)
        addToFile('/Users/fua/tmp/python.dat','{:2d} {:f} {:f} {:f} {:f}\n'.format(n,dt1,dt2,dt3,dt4),newP=False)
        print('----------------------------------------------------------')
#%%
print('----------------------------------------------------------')
rpt = 0
if(rpt>0):
    for n in range(8,14):
        dt1=0.0
        dt2=0.0
        dt3=timeit_and_print(partial(allQueensPara,n), name='Parallel  para    {:2d}'.format(n),number=rpt)
        dt4=0.0
        addToFile('/Users/fua/tmp/python.dat','{:2d} {:f} {:f} {:f} {:f}\n'.format(n,dt1,dt2,dt3,dt4),newP=False)
        print('----------------------------------------------------------')
#%%
#number  = 5
#mean = 0.0
#var  = 0.0
#ar = np.random.randn(number)
#for dt in ar:
#    mean += dt
#    var  += dt*dt
#    
#numb = float(number)
#mean = mean / numb
#var  = var  / numb  - mean*mean
#var *= (numb / (numb - 1.0))
#var  = sqrt(var)
#print(mean,var)