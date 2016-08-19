import numpy as np
import scipy.linalg as la
from scipy.misc import factorial
"""
A module for finding the eigenvalues and wavefunctions
of an N-dimensional (N<=3) potential using spectral
methods.

"""
__all__ = ['eigensolver']

def _d1(N,h):
    """First-order Fourier spectral differentiation matrix.
    
    Parameters
    ----------
    N : int
        Dimension of matrix to build.
    h : float
        Spacing between sample points.
    
    Returns
    -------
    d1 : ndarray
        Spectral approximation to second-derivative.
    
    """
    i = np.arange(1,N)
    col = np.hstack(([0], 0.5*(-1)**i/np.tan(i*h/2.0)))
    row = np.hstack(([0], col[N-1:0:-1]))
    return la.toeplitz(col,row)


def _d2(N,h):
    """Second-order Fourier spectral differentiation matrix.
    
    Parameters
    ----------
    N : int
        Dimension of matrix to build.
    h : float
        Spacing between sample points.
    
    Returns
    -------
    d2 : ndarray
        Spectral approximation to second-derivative.
    
    """
    i = np.arange(1,N)
    col = np.hstack(([-np.pi**2/(3*h**2)-1.0/6.0,-0.5*(-1)**i/np.sin(h*i/2.0)**2]))
    return la.toeplitz(col)


def eigensolver(U, N=[], domain=[], k_diag=[], k_cross=[], vals_only=False, sparse=False):
    """Eigensolver for eigenvalues and wavefunctions corresponding to a N-dimensional 
    potentional U(x1,x2,,...).  Here N should be <=3.
    
    Parameters
    ----------
    U : func
        Function defining the potential U(x1,x2,...).
    N : list
        Number of points to sample in the ith-spatial direction. 
    domain : list
        Nested list of [x_i_min,x_i_max] for each spatial dimension.
    k_diag : list, optional
        Numerical values for diagonal kinetic terms d^2/(dx_i)^2, -hbar^2/2m.
        Default value is minus one if not given explicitly.
    k_cross : list, optional
        Numerical values for cross kinetic terms d^2/(dx_i*dx_j) [k01,k02,..,k12,k13,..].
        Default value is zero if not given explicitly.
    vals_only : bool {False, True}
        Tells solver to return only eigenvalues.
    
    """
    if isinstance(N,int):
        N = np.array([N],dtype=int)
    else:
        N = np.asarray(N,dtype=int)
    n = len(N)
    if n > 3:
        raise ValueError('Eigensolver currently works for D <= 3 dimensions.')
    if n > 1:
        n_cross = int(factorial(n)/factorial(n-2)/2)
    else:
        n_cross = 0
    #check if number of domains matches dimensionality
    if n != len(domain):
        raise Exception('Number of domains (%s) does not match dimensionality (%s).' % (len(domain),n))
    
    #check that each domain has min and max endpoints, and nothing else
    for d in domain:
        if len(d) < 2:
            raise Exception('Each domain must have both a min and max endpoint.')
        elif len(d) > 2:
            raise Exception('Invalid domain specification.')
    
    #set kinetic terms to default values if not given explicitly.
    if len(k_diag) == 0:
        k_diag = -1*np.ones(n)
    if len(k_cross) == 0:
        k_cross = np.zeros(n_cross)
    
    #Multiply kinetic terms by appropriate scaling factors
    k_diag = np.array([k_diag[ii]*(2*np.pi)**2/(domain[ii][1]- \
                        domain[ii][0])**2 for ii in range(n)])
    #get indices of cross terms
    cb = it.combinations(np.arange(n),2)
    cb = np.fromiter(cb,dtype='i,i',count=-1)
    for ii in range(n_cross):
        if k_cross[ii] != 0:
            k_cross[ii] *= (2*np.pi)**2/(domain[cb[ii][0]][1]- \
                            domain[cb[ii][0]][0])/(domain[cb[ii][1]][1]- \
                            domain[cb[ii][1]][0])
    
    #set up sample points
    h = 2*np.pi/N
    x = np.array([h[ii]*np.arange(1,N[ii]+1) for ii in range(n)])
    x = np.array([x[ii]/(2*np.pi)*(domain[ii][1]-domain[ii][0])+ \
            domain[ii][0] for ii in range(n)])
    
    mesh = np.meshgrid(*x)
    mesh = np.array([ii.ravel('F') for ii in mesh])
    
    #Get diagonal potential elements at sample points
    U = np.diag(U(*mesh),k=0)
    H = U
    
    #Simple 1D case
    if n == 1:
        H += k_diag[0]*_d2(N[0],h[0])
    #2D
    elif n == 2:
        H += k_diag[0]*np.kron(_d2(N[0],h[0]),np.eye(N[1]))
        H += k_diag[1]*np.kron(np.eye(N[0]),_d2(N[1],h[1]))
        if k_cross[0]!=0:
            H += k_cross[0]*np.kron(_d1(N[0],h[0]),_d1(N[1],h[1]))  
    #3D
    elif n == 3:
        H += k_diag[0]*np.kron(np.kron(_d2(N[0],h[0]),np.eye(N[1])),np.eye(N[2]))
        H += k_diag[1]*np.kron(np.kron(np.eye(N[0]),_d2(N[1],h[1])),np.eye(N[2]))
        H += k_diag[2]*np.kron(np.kron(np.eye(N[0]),np.eye(N[1]),_d2(N[2],h[2])))
        if k_cross[0]!=0:
            H += k_cross[0]*np.kron(np.kron(_d1(N[0],h[0]),_d1(N[1],h[1])), np.eye(N[2]))  
        if k_cross[1]!=0:
            H += k_cross[1]*np.kron(np.kron(_d1(N[0],h[0]),np.eye(N[1])), _d1(N[2],h[2]))
        if k_cross[2]!=0:
            H += k_cross[2]*np.kron(np.kron(np.eye(N[0]),_d1(N[1],h[1])), _d1(N[2],h[2]))
    
    if vals_only == True:
        evals = la.eigvalsh(H)
        idx = evals.argsort()
        evals = evals[idx]
        return evals
    else:
        evals, evecs = la.eigh(H)
        idx = evals.argsort()
        evals = evals[idx]
        evecs = evecs[idx]
        if n == 1:
            return evals, evecs, x[0]
        else:
            return evals, evecs, x