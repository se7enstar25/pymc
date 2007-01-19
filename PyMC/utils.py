"""Utility functions for PyMC"""


# License: Scipy compatible
# Author: David Huard, 2006
# A bit slow. try to optimize
from numpy import *
from scipy import special
def histogram(a, bins=10, range=None, normed=False, weights=None, axis=None):
    """histogram(a, bins=10, range=None, normed=False, weights=None, axis=None) 
                                                                   -> H, dict
    
    Return the distribution of sample.
    
    Parameters
    ----------
    a:       Array sample.
    bins:    Number of bins, or 
             an array of bin edges, in which case the range is not used.
    range:   Lower and upper bin edges, default: [min, max].
    normed:  Boolean, if False, return the number of samples in each bin,
             if True, return the density.  
    weights: Sample weights. The weights are normed only if normed is True. 
             Should weights.sum() not equal len(a), the total bin count will 
             not be equal to the number of samples.
    axis:    Specifies the dimension along which the histogram is computed. 
             Defaults to None, which aggregates the entire sample array. 
    
    Output
    ------
    H:            The number of samples in each bin. 
                  If normed is True, H is a frequency distribution.
    dict{
    'edges':      The bin edges, including the rightmost edge.
    'upper':      Upper outliers.
    'lower':      Lower outliers.
    'bincenters': Center of bins.
    }
    
    Examples
    --------
    x = random.rand(100,10)
    H, Dict = histogram(x, bins=10, range=[0,1], normed=True)
    H2, Dict = histogram(x, bins=10, range=[0,1], normed=True, axis=0)
    
    See also: histogramnd
    """
    
    a = asarray(a)
    if axis is None:
        a = atleast_1d(a.ravel())
        axis = 0 
        
    # Bin edges.   
    if not iterable(bins):
        if range is None:
            range = (a.min(), a.max())
        mn, mx = [mi+0.0 for mi in range]
        if mn == mx:
            mn -= 0.5
            mx += 0.5
        edges = linspace(mn, mx, bins+1, endpoint=True)
    else:
        edges = asarray(bins, float)

    dedges = diff(edges)
    decimal = int(-log10(dedges.min())+6)
    bincenters = edges[:-1] + dedges/2.

    # apply_along_axis accepts only one array input, but we need to pass the 
    # weights along with the sample. The strategy here is to concatenate the 
    # weights array along axis, so the passed array contains [sample, weights]. 
    # The array is then split back in  __hist1d.
    if weights is not None:
        aw = concatenate((a, weights), axis)
        weighted = True
    else:
        aw = a
        weighted = False
        
    count = apply_along_axis(hist1d, axis, aw, edges, decimal, weighted, normed)
    
    # Outlier count
    upper = count.take(array([-1]), axis)
    lower = count.take(array([0]), axis)
    
    # Non-outlier count
    core = a.ndim*[slice(None)]
    core[axis] = slice(1, -1)
    hist = count[core]
    
    if normed:
        normalize = lambda x: atleast_1d(x/(x*dedges).sum())
        hist = apply_along_axis(normalize, axis, hist)

    return hist, {'edges':edges, 'lower':lower, 'upper':upper, \
        'bincenters':bincenters}
        
         
def hist1d(aw, edges, decimal, weighted, normed):
    """Internal routine to compute the 1d histogram.
    aw: sample, [weights]
    edges: bin edges
    decimal: approximation to put values lying on the rightmost edge in the last
             bin.
    weighted: Means that the weights are appended to array a. 
    Return the bin count or frequency if normed.
    """
    nbin = edges.shape[0]+1
    if weighted:
        count = zeros(nbin, dtype=float)
        a,w = hsplit(aw,2)
        if normed:
            w = w/w.mean()
    else:
        a = aw
        count = zeros(nbin, dtype=int)
        w = None
        
    
    binindex = digitize(a, edges)
    
    # Values that fall on an edge are put in the right bin.
    # For the rightmost bin, we want values equal to the right 
    # edge to be counted in the last bin, and not as an outlier. 
    on_edge = where(around(a,decimal) == around(edges[-1], decimal))[0]
    binindex[on_edge] -= 1
    
    # Count the number of identical indices.
    flatcount = bincount(binindex, w)
    
    # Place the count in the histogram array.
    i = arange(len(flatcount))
    count[i] = flatcount
       
    return count
    

from numpy.testing import *
class test_histogram(NumpyTestCase):
    def check_simple(self):
        n=100
        v=rand(n)
        (a,b)=histogram(v)
        #check if the sum of the bins equals the number of samples
        assert(sum(a,axis=0)==n)
        #check that the bin counts are evenly spaced when the data is from a linear function
        (a,b)=histogram(linspace(0,10,100))
        assert(all(a==10))
        #Check the construction of the bin array
        a, b = histogram(v, bins=4, range=[.2,.8])
        assert(all(b['edges']==linspace(.2, .8, 5)))
        #Check the number of outliers
        assert((v<.2).sum() == b['lower'])
        assert((v>.8).sum() == b['upper'])
        #Check the normalization
        bins = [0,.5,.75,1]
        a,b = histogram(v, bins, normed=True)
        assert_almost_equal((a*diff(bins)).sum(), 1)
        
    def check_axis(self):
        n,m = 100,20
        v = rand(n,m)
        a,b = histogram(v, bins=5)
        # Check dimension is reduced (axis=None).
        assert(a.ndim == 1)
        #Check total number of count is equal to the number of samples.
        assert(a.sum() == n*m)
        a,b = histogram(v, bins = 7, axis=0)
        # Check shape of new array is ok.
        assert(a.ndim == 2)
        assert_array_equal(a.shape,[7, m])
        # Check normalization is consistent 
        a,b = histogram(v, bins = 7, axis=0, normed=True)
        assert_array_almost_equal((a.T*diff(b['edges'])).sum(1), ones((m)))
        a,b = histogram(v, bins = 7, axis=1, normed=True)
        assert_array_equal(a.shape, [n,7])
        assert_array_almost_equal((a*diff(b['edges'])).sum(1), ones((n)))
        # Check results are consistent with 1d estimate
        a1, b1 = histogram(v[0,:], bins=b['edges'], normed=True)
        assert_array_equal(a1, a[0,:])
            
    def check_weights(self):
        # Check weights = constant gives the same answer as no weights.
        v = rand(100)
        w = ones(100)*5
        a,b = histogram(v)
        na,nb = histogram(v, normed=True)
        wa,wb = histogram(v, weights=w)
        nwa,nwb = histogram(v, weights=w, normed=True)
        assert_array_equal(a*5, wa)
        assert_array_equal(na, nwa)
        # Check weights are properly applied.
        v = linspace(0,10,10)
        w = concatenate((zeros(5), ones(5)))
        wa,wb = histogram(v, bins=arange(11),weights=w)
        assert_array_almost_equal(wa, w)
        
        
        
# Some python densities for comparison
def cauchy(x, x0, gamma):
    return 1/pi * gamma/((x-x0)**2 + gamma**2)
    
def gamma(x, alpha, beta):
    return x**(alpha-1) * exp(-x/beta)/(special.gamma(alpha) * beta**alpha)
    
if __name__ == "__main__":
    NumpyTest().run()
