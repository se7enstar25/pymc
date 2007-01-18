"""Test the distributions from flib and their random generators to check
they are consistent with one another.
For each distribution:
1. Select parameters (params = {'alpha':.., 'beta'=...}).
2. Generate N random samples.
3. Compute likelihood for a vector of x values.
4. Compute histogram of samples.
5. Compare histogram with likelihood.
6. Assert if they fit or not.

David- constrain() in flib is giving me bus errors, try for instance
uncommenting the constrain lines in poisson().
-A
Well, you're not calling it correctly, and g77 doesn't understand INFINITY.
At first, I wanted to constrain everything from fortran, but g77 doesn't
really handle exceptions. I finally wrapped the fortran constrain and called
it from python. We'll need a brainstorm on this. One idea is to use f2py for this.
There is some checking that can be done using the check argument. Maybe we can
insert C code to do  a loop on each argument and check the constraints.
With pure fortran, the only way I see out of it is to return a very large
negative number to approximate -inf. For the time being, let's leave the
constraining to python.
-D
"""

# TODO: Add plots to show the fit between histograms and flib probability.
# TODO: Improve the assertion of consistency.
#       Maybe compare the relative error (hist-like)/like
# TODO: Add a normalization test.

from decorators import *
import unittest
import flib

from numpy.testing import *
import numpy as np
from numpy import exp

def consistency(random, like, params, nbins=10, nrandom=1000, nintegration=15, range=None):
    """Check the random generator is consistent with the likelihood.

    Arguments:
      - random: function: Random generator.
      - like: function: Log probability.
      - params: dict:  Parameters for the distribution.
      - nbins: int: Number of bins in histogram.
      - nrandom: int: Number of random samples.
      - nintegration: int: Number of divisions in each bin.
      - range: (float,float): Range of histogram.

    Return: (hist, like)
      - hist: Histogram of random samples from random(**params).
      - like: integrated likelihood over histogram bins.
    """
    # Samples values and compute histogram.
    samples = []
    for i in np.arange(nrandom):
        samples.append(random(**params))
    samples = np.array(samples)
    hist,bins = np.histogram(samples, range=range, bins=nbins, normed=True)

    # Compute likelihood along x axis.
    if range is None:
        range = samples.min(), samples.max()
    X = np.linspace(range[0], range[1], nbins*nintegration)
    l = []
    for x in X:
        l.append(like(x, **params))
    L = exp(np.array(l))
    L = L.reshape(nbins, nintegration)
    like = L.mean(1)
    return hist, like


class test_bernoulli(NumpyTestCase):
    def check_consistency(self):
        N = 5000
        params = {'p':.6}
        samples = []
        for i in range(N):
            samples.append(rbernoulli(**params))
        H = np.bincount(samples)*1./N
        l0 = exp(flib.bernoulli(0, **params))
        l1 = exp(flib.bernoulli(1, **params))
        assert_array_almost_equal(H, [l0,l1], 2)

    def test_calling(self):
        a = flib.bernoulli([0,1,1,0], .4)
        b = flib.bernoulli([0,1,1,0], [.4, .4, .4, .4])
        assert_array_equal(b,a)


class test_beta(NumpyTestCase):
    def check_consistency(self):
        params ={'alpha':3, 'beta':5}
        hist, like = consistency(rbeta, flib.beta_like, params, nrandom=5000, range=[0,1])
        assert_array_almost_equal((hist-like)/sqrt(like),0,1)

    def test_calling(self):
        a = flib.beta_like([.3,.4,.5], 2,3)
        b = flib.beta_like([.3,.4,.5], [2,2,2],[3,3,3])
        assert_array_equal(a,b)

class test_binomial(NumpyTestCase):
	def check_consistency(self):
		params={'n':7, 'p':.7}
		hist, like = consistency(rbinomial, flib.binomial, params, nrandom=5000, nbins=7, range=[0,7])
		assert_array_almost_equal(hist, like,1)

	def test_calling(self):
		a = flib.binomial([3,4,5], 7, .7)
		b = flib.binomial([3,4,5], [7,7,7], .7)
		c = flib.binomial([3,4,5], [7,7,7], [.7,.7,.7])
		assert_equal(a,b)
		assert_equal(a,c)

"""
Weird bug on this one.
class test_cauchy(NumpyTestCase):
	def check_consistency(self):
		params={'alpha':5, 'beta':4}
		hist, like = consistency(rcauchy, flib.cauchy, params, nrandom=5000)
		assert_array_almost_equal(hist, like,1)

	def test_calling(self):
		a = flib.cauchy([3,4], 2, 6)
		b = flib.cauchy([3,.4], [2,2], [6,6])
		assert_equal(a,b)
"""
class test_poisson(NumpyTestCase):
    def check_consistency(self):
        #from np.random import poisson
        params = {'mu':2.}
        hist,like = consistency(rpoisson, flib.poisson, params, nrandom=5000, range=[0,10])
        assert_array_almost_equal(hist, like,1)
"""
Weibull is parametrized differently in flib than in numpy.random
numpy.random: alpha (you need to multiply by beta)
flib: alpha, beta
Use the wrapped up random generators. DH.
"""
class test_weibull(NumpyTestCase):
    def check_consistency(self):
        params = {'alpha': 2., 'beta': 3.}
        hist,like = consistency(rweibull, flib.weibull, params, nrandom=5000, range=[0,10])
        assert_array_almost_equal(hist, like,1)

"""
Hyperg is parametrized differently in flib than is hypergeometric in numpy.random.
numpy.random: good, bad, sample
flib: red (=bad), d (=sample), total (=good+bad)

What to do about this?
Either change the argument names in flib or in distributions.
-D

class test_hyperg(NumpyTestCase):
    def __init__(self):
        from np.random import poisson
        params = {'ngood':2, 'nbad':5, 'nsample':3}
        hist,like = consistency(poisson, flib.poisson, params, nrandom=5000, range=[0,10])
"""



if __name__ == '__main__':
    NumpyTest().run()
