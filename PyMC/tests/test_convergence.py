###
#
# Test of convergence diagnostics
#
###


from numpy.testing import *
import pymc
import pymc.examples.maximum_rainfall as mr

S = pymc.MCMC(mr.Gumbelfit, 'ram')
S.sample(1000)
sigma = S.sigma.trace()

class test_geweke(NumpyTestCase):
    def check_simple(self):
        
        scores = pymc.geweke(sigma)
        print scores
        
class test_raftery_lewis(NumpyTestCase):
    def check_simple(self):
        print pymc.raftery_lewis(sigma, 0.5, .05)


if __name__ == "__main__":
    NumpyTest().run()
