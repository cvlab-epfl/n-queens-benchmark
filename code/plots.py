#!/usr/bin/env python3
#-----------------------------------------------------------------------------
#                         
#=============================================================================

#%---------------------------------------------------------------------------
#                                IMPORTS
#-----------------------------------------------------------------------------
#%

import numpy as np
import matplotlib.pyplot as plt

from  util import setAxes,colorN,scanf
#%%

def plotTimes(times,fromN,toN,label="times",color=0):
    plt.plot(range(fromN,toN),times[fromN:toN],label=label,color=colorN(color))
    
def savePlot(baseName):
    
    fig = plt.gcf()
    ax  = plt.gca()
    
    plt.legend()
    ax.set_xlabel('Number of queens')
    ax.set_ylabel('time [s]')
    fig.tight_layout()

	# Save plot
    for ext in ['pdf', 'svg', 'png']:
        fig.savefig('{}.{}'.format(baseName,ext))
        
    
def loadPythFile(fileName):
    pythoTimes = np.zeros([19,4],dtype=float)
    with open(fileName, 'r') as f:
        lines = f.readlines()
        for line in lines[1:]:  # Ignore first line
            ls = scanf("%d %f %f %f %f %f %f %f %f",line)
            if(ls is None):
                print("Couldn't read.\n")
                break
            n  = int(ls[0])
            for j in range(1,8,2):
                
                pythoTimes[n,(j-1)//2]=ls[j]
    return pythoTimes

def loadClusFile(fileName):
    cplusTimes = np.zeros([19,2],dtype=float)
    with open(fileName, 'r') as f:
        lines = f.readlines()
        for line in lines[1:]:  # Ignore first line
            ls = scanf("%d %f %f %f %f",line)
            if(ls is None):
                print("Couldn't read.\n")
                break
            n  = int(ls[0])
            for j in range(1,4,2):
                cplusTimes[n,(j-1)//2]=ls[j]
    return cplusTimes

def loadJuliFile(fileName):
    cplusTimes = np.zeros([19,2],dtype=float)
    with open(fileName, 'r') as f:
        lines = f.readlines()
        for line in lines[1:]:  # Ignore first line
            ls = scanf("%d %f %f",line)
            if(ls is None):
                print("Couldn't read.\n")
                break
            n  = int(ls[0])
            for j in range(1,2,2):
                cplusTimes[n,(j-1)//2]=ls[j]
    return cplusTimes
#%%
pythoTimes=loadPythFile("/Users/fua/papers/20/misc/queens/code/python.dat")
cplusTimes=loadClusFile("/Users/fua/papers/20/misc/queens/code/cplus.dat")
golanTimes=loadClusFile("/Users/fua/papers/20/misc/queens/code/golang.dat")
juliaTimes=loadJuliFile("/Users/fua/papers/20/misc/queens/code/julia.dat")
#%%
lispTimes = np.zeros([19,1],dtype=float)
lispTimes[8,0]= 0.0003562
lispTimes[9,0]= 0.0014842
lispTimes[10,0]=0.0057682
lispTimes[11,0]=0.027113
lispTimes[12,0]=0.1334559
lispTimes[13,0]=0.7280822
lispTimes[14,0]=4.438823
lispTimes[15,0]=29.124266
#%%---------------------------------------------------------------------------
#                                
#-----------------------------------------------------------------------------
#%%
logP = False
#logP = True
plt.clf()
plotTimes(pythoTimes[:,0],8,15,label="Python",color=0)
plotTimes(pythoTimes[:,1],8,15,label="Numba" ,color=1)
plotTimes(golanTimes[:,0],8,15,label="Go"    ,color=3)
plotTimes(cplusTimes[:,0],8,15,label="C++"   ,color=4)
plotTimes(lispTimes[:,0],8,15,label="Lisp"        ,color=5)
plotTimes(juliaTimes[:,0],8,15,label="Julia"      ,color=6)
ax=plt.gca()
setAxes(8,0,14,3.0)
if(logP):
    ax.set_yscale('log')
    setAxes(8,1e-4,14,1e2)
plt.legend()
#%%
if(logP):
    savePlot("/Users/fua/papers/20/misc/queens/fig/logseq")
else:
    savePlot("/Users/fua/papers/20/misc/queens/fig/seq")
#%%
logP = False
logP = True
plt.clf()
plotTimes(pythoTimes[:,1],12,19,label="Numba" ,color=1)
plotTimes(pythoTimes[:,2],12,19,label="Para"  ,color=0)
plotTimes(pythoTimes[:,3],12,19,label="Pool"  ,color=2)
plotTimes(golanTimes[:,1],12,19,label="Go"    ,color=3)
plotTimes(cplusTimes[:,1],12,19,label="C++"   ,color=4)
ax=plt.gca()
setAxes(12,0,18,1000.0)
if(logP):
    ax.set_yscale('log')
    setAxes(12,1e-2,18,1e3)
plt.legend()
#%%
if(logP):
    savePlot("/Users/fua/papers/20/misc/queens/fig/logpar")
else:
    savePlot("/Users/fua/papers/20/misc/queens/fig/par")
#%%
print(np.mean(pythoTimes[8:15,0] / pythoTimes[8:15,1]))
print(np.mean(pythoTimes[8:15,1] / golanTimes[8:15,0]))
print(np.mean(pythoTimes[8:15,1] / cplusTimes[8:15,0]))
#%%
allocTimes=loadClusFile("/Users/fua/papers/20/misc/queens/code/cplus.alloc.dat")
vectrTimes=loadClusFile("/Users/fua/papers/20/misc/queens/code/cplus.vect.dat")
uint8Times=loadClusFile("/Users/fua/papers/20/misc/queens/code/cplus.uint.dat")
cstatTimes=loadClusFile("/Users/fua/papers/20/misc/queens/code/cplus.stat.dat")
gheapTimes=loadClusFile("/Users/fua/papers/20/misc/queens/code/golang.heap.dat")
#%%
plt.clf()
plotTimes(cplusTimes[:,1],8,15,label="C++"       ,color=4)
plotTimes(vectrTimes[:,1],8,15,label="C++ Vector" ,color=5)
#plotTimes(allocTimes[:,1],8,15,label="C++ Alloc" ,color=0)
plotTimes(uint8Times[:,1],8,15,label="C++ Uint"  ,color=1)
plotTimes(cstatTimes[:,1],8,15,label="C++ Static"  ,color=2)
#plotTimes(golanTimes[:,1],8,15,label="Go"        ,color=3)
#plotTimes(gheapTimes[:,1],8,15,label="Go Heap"   ,color=1)
ax=plt.gca()
setAxes(8,0,14,0.4)
if(0>0):
    ax.set_yscale('log')
    setAxes(8,1e-4,14,1e2)
plt.legend()
#%%
plt.clf()
plotTimes(cplusTimes[:,1],12,19,label="C++"       ,color=4)
plotTimes(vectrTimes[:,1],12,19,label="C++ Vector" ,color=5)
#plotTimes(allocTimes[:,1],12,19,label="C++ Alloc" ,color=0)
plotTimes(uint8Times[:,1],12,19,label="C++ Uint"  ,color=1)
plotTimes(cstatTimes[:,1],12,19,label="C++ Static"  ,color=2)
#plotTimes(golanTimes[:,1],12,19,label="Go"        ,color=3)
#plotTimes(gheapTimes[:,1],12,19,label="Go Heap"   ,color=1)
ax=plt.gca()
setAxes(12,0,18,150.0)
if(0>0):
    ax.set_yscale('log')
    setAxes(12,1e-2,18,1e3)
plt.legend()
#%%
print(np.mean(pythoTimes[8:15,1] / gheapTimes[8:15,0]))
print(np.mean(pythoTimes[8:15,1] / cheapTimes[8:15,0]))
#%%---------------------------------------------------------------------------
#                          LATEX
# ----------------------------------------------------------------------------
#%%
def printCol(langTimes,colIndex,n0,n1,label):
    
    line = ""
    line = line + label
    
    col = langTimes[:,colIndex]
    for i in range(n0,n1):
        if (col[i] > 0.0):
            line = "{} & {:f}".format(line,col[i])
        else:
            line = "{} & -".format(line)
    line = line + " \\\\"
    print(line)
#%%
print('\hline')
printCol(pythoTimes,0,8,19,"Python")
print('\hline')
printCol(pythoTimes,1,8,19,"Numba")
print('\hline')
printCol(golanTimes,0,8,19,"Go")
print('\hline')
printCol(cplusTimes,0,8,19,"C++")
print('\hline')
#%%
print('\hline')
printCol(pythoTimes,2,8,19,"Para")
print('\hline')
printCol(pythoTimes,3,8,19,"Pool")
print('\hline')
printCol(golanTimes,1,8,19,"Go")
print('\hline')
printCol(cplusTimes,1,8,19,"C++")
print('\hline')
#%%
printCol(lispTimes,0,8,19,"Lisp")
print('\hline')
printCol(juliaTimes,0,8,19,"Julia")
print('\hline')
#%%

  