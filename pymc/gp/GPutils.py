# Copyright (c) Anand Patil, 2007

__docformat__='reStructuredText'
__all__ = ['observe', 'plot_envelope', 'predictive_check', 'regularize_array', 'trimult', 'trisolve', 'vecs_to_datmesh']


# TODO: Implement lintrans, allow obs_V to be a huge matrix or an ndarray in observe().

from numpy import *
from numpy.linalg import solve, cholesky, eigh
from numpy.linalg.linalg import LinAlgError
from pylab import fill, plot, clf, axis
from linalg_utils import *

try:
    from PyMC2 import ZeroProbability
except ImportError:
    class ZeroProbability(ValueError):
        pass

half_log_2pi = .5 * log(2. * pi)

def vecs_to_datmesh(x, y):
    """
    Converts input arguments x and y to a 2d meshgrid,
    suitable for calling Means, Covariances and Realizations.
    """
    x,y = meshgrid(x,y)
    out = zeros(x.shape + (2,), dtype=float)
    out[:,:,0] = x
    out[:,:,1] = y
    return out

def trimult(U,x,uplo='U',transa='N',alpha=1.,inplace=False):
    """
    b = trimult(U,x, uplo='U')

    
    Multiplies U x, where U is upper triangular if uplo='U'
    or lower triangular if uplo = 'L'.
    """
    if inplace:
        b=x
    else:
        b = x.copy()
    dtrmm_wrap(a=U,b=b,uplo=uplo,transa=transa,alpha=alpha)
    return b

        
def trisolve(U,b,uplo='U',transa='N',alpha=1.,inplace=False):
    """
    x = trisolve(U,b, uplo='U')

    
    Solves U x = b, where U is upper triangular if uplo='U'
    or lower triangular if uplo = 'L'.

    
    If a degenerate column is found, an error is raised.
    """
    if inplace:
        x=b
    else:
        x = b.copy()
    if U.shape[0] == 0:
        raise ValueError, 'Attempted to solve zero-rank triangular system'
    dtrsm_wrap(a=U,b=x,uplo=uplo,transa=transa,alpha=alpha)
    return x
        

def regularize_array(A):
    """
    Takes an ndarray as an input.

    
    -   If the array is one-dimensional, it's assumed to be an array of input values.

    -   If the array is more than one-dimensional, its last index is assumed to curse
        over spatial dimension.

    
    Either way, the return value is at least two dimensional. A.shape[-1] gives the
    number of spatial dimensions.
    """
    # Make sure A is an array.
    if not isinstance(A,ndarray):
        A = array(A, dtype=float)
    else:
        A = asarray(A, dtype=float)
    
    # If A is one-dimensional, interpret it as an array of points on the line.
    if len(A.shape) <= 1:
        return A.reshape(-1,1)
        
    # Otherwise, interpret it as an array of n-dimensional points, where n
    # is the size of A along its last index.
    elif A.shape[-1]>1:
        return A.reshape(-1, A.shape[-1])
    
    else:
        return A


def plot_envelope(M,C,mesh):
    """
    plot_envelope(M,C,mesh)
    
    
    plots the pointwise mean +/- sd envelope defined by M and C
    along their base mesh.
    
    
    :Arguments:
    
        -   `M`: A Gaussian process mean.
    
        -   `C`: A Gaussian process covariance
    
        -   `mesh`: The mesh on which to evaluate the mean and cov.
    """
    x=concatenate((mesh, mesh[::-1]))
    sig = sqrt(abs(C(mesh)))
    mean = M(mesh)
    y=concatenate((mean-sig, (mean+sig)[::-1]))
    # clf()
    fill(x,y,facecolor='.8',edgecolor='1.')
    plot(mesh, mean, 'k-.')    


def observe(M, C, obs_mesh, obs_vals, obs_V = 0, lintrans = None, cross_validate = True):
    """
    (M, C, obs_mesh, obs_vals[, obs_V = 0, lintrans = None, cross_validate = True])
    
    
    Imposes observation of the value of obs_vals on M and C, where

    obs_vals ~ N(lintrans * f(obs_mesh), V)
    f ~ GP(M,C)
    
    
    :Arguments:

        -   `M`: The mean function

        -   `C`: The covariance function

        -   `obs_mesh`: The places where f has been evaluated.

        -   `obs_vals`: The values of f that were observed there.

        -   `obs_V`: The observation variance. If None, assumed to be infinite 
            (observations made with no error).

        -   `lintrans`: A linear transformation. If None, assumed to be the 
            identity transformation (pretend it doesn't exist).

        -   `cross_validate`: A flag indicating whether a check should be done to 
            see if the data could have arisen from M and C with positive probability.
        
    """
    obs_mesh = regularize_array(obs_mesh)
    # print obs_mesh
    obs_V = resize(obs_V, obs_mesh.shape[0])   
    obs_vals = resize(obs_vals, obs_mesh.shape[0])
    
    # First observe C.
    relevant_slice, obs_mesh_new, junk = C.observe(obs_mesh, obs_V)    
    
    # Then observe M from C.
    M.observe(C, obs_mesh_new, obs_vals.ravel()[relevant_slice])
    
    # Cross-validate if not asked not to.
    if obs_mesh_new.shape[0] < obs_mesh.shape[0]:
        if cross_validate:
            if not predictive_check(obs_vals, obs_mesh, M, C.obs_piv, sqrt(C.relative_precision)):
                raise ValueError, "These data seem extremely improbable given your GP prior. \n Suggestions: decrease observation precision, or adjust the covariance to \n allow the function to be less smooth."

            
def predictive_check(obs_vals, obs_mesh, M, posdef_indices, tolerance):
    """
    OK = predictive_check(obs_vals, obs_mesh, M, posdef_indices, tolerance)

    
    If an internal covariance is low-rank, make sure the observations
    are consistent. Returns True if good, False if bad.

    
    :Arguments:

        -   `obs_vals`: The observed values.

        -   `obs_mesh`: The mesh on which the observed values were observed.

        -   `M`: The mean function, observed at obs_vals[posdef_indices].

        -   `tolerance`: The maximum allowable deviation at M(obs_mesh[non_posdef_indices]).
    """

    non_posdef_indices = array(list(set(range(len(obs_vals))) - set(posdef_indices)),dtype=int)
    if len(non_posdef_indices)>0:
        M_under = M(obs_mesh[non_posdef_indices,:]).ravel()
        dev = abs((M_under - obs_vals[non_posdef_indices]))
        if dev.max()>tolerance:
            return False
    
    return True