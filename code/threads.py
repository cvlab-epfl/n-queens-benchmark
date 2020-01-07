#!/usr/bin/env python3
#-----------------------------------------------------------------------------
#                         
#=============================================================================

#%---------------------------------------------------------------------------
#                                IMPORTS
#-----------------------------------------------------------------------------
#%

import numpy as np
import numba
from   numba import njit,prange

from timeit    import timeit
from functools import partial

from multiprocessing.dummy import Pool as Pool_thread

#%%---------------------------------------------------------------------------
#                                
#-----------------------------------------------------------------------------
#%%
@njit(nogil=True)   
def allQueensCol(n,j):
    
    nsol = 0
    
    col = np.ones(n,dtype=numba.boolean)
    dg1 = np.ones(2*n,dtype=numba.boolean)
    dg2 = np.ones(2*n,dtype=numba.boolean)
    # Put a queen in cell j of the first row
    col[j] = False
    dg1[j] = False
    dg2[n-j] = False
    # Fills the rest of the board
    nsol   = allQueensAux(n,1,col,dg1,dg2,0)
    
    return(nsol)
    
@njit(nogil=True) #Numba decorator
def allQueensAux(n,i,col,dg1,dg2,nsol):
    # All rows are filled. Increment the counter and stop the recursion
    if n == i :
        return nsol+1
    # Try putting a queen in each cell of row i
    for j in range(n):
        if (col[j] and dg1[i+j] and dg2[i-j+n]): 

            col[j]     = False  # Mark column j as occupied
            dg1[i+j]   = False  # Mark diagonal i+j as occupied
            dg2[i-j+n] = False  # Mark diagonal i-j as occupied

            nsol=allQueensAux(n,i+1,col,dg1,dg2,nsol)
            
            col[j]     = True   # Unmark column j
            dg1[i+j]   = True   # Unmark diagonal i+j
            dg2[i-j+n] = True   # Unmark diagonal i-j
            
    return nsol
    
if __name__ == "__main__":
    nsol = 0
    for j in range(8):
        nsol += allQueensCol(8,j)
    print('Par    :',nsol)
#%%
def poolWorker(n,j):
    return allQueensCol(n,j)

def allQueensThread(n,np=None):
    if(np is None):
        with Pool_thread() as pool:
            nsols= pool.map(partial(poolWorker,n),prange(n))
            return (sum(nsols))
    else:
        with Pool_thread(processes=np) as pool:
            nsols= pool.map(partial(poolWorker,n),prange(n))
            return (sum(nsols))
        
if __name__ == "__main__":
    print('Thread :',allQueensThread(8,None))
#%%---------------------------------------------------------------------------
#                            TEST
#-----------------------------------------------------------------------------
#%%
def timeit_and_print(statement, number=10, name=''):
    time_elapsed = timeit(statement,number=number)
    
    time_per_iter = time_elapsed/number
    
    print('{ti:04f} s/iter | {tt:04f} s total | {name}'.format(
        ti = time_per_iter,
        tt = time_elapsed,
        name = name,
    ))
#%%
print('----------------------------------------------------------')
rpt = 5
if(rpt>0):
    for n in range(12,16):
        for nproc in [2,4,8,None]:
            timeit_and_print(partial(allQueensThread,n,nproc),  name='Parallel   thread {:2d}({})'.format(n,nproc),number=rpt)
        print('----------------------------------------------------------')