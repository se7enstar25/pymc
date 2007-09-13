from PyMC2 import NormalApproximation, msqrt
from PyMC2.examples import gelman_bioassay
from pylab import *
from numpy import *
from numpy.testing import * 
from numpy.linalg import cholesky

model = gelman_bioassay
N = NormalApproximation(model)

class test_norm_approx(NumpyTestCase):
    def check_fmin(self):
        N = NormalApproximation(model)
        N.fit('fmin')
    def check_fmin_l_bfgs_b(self):
        N = NormalApproximation(model)
        N.fit('fmin_l_bfgs_b')
    def check_fmin_ncg(self):
        N = NormalApproximation(model)
        N.fit('fmin_ncg')
    def check_fmin_cg(self):
        N = NormalApproximation(model)
        N.fit('fmin_cg')
    def check_fmin_powell(self):
        N = NormalApproximation(model)
        N.fit('fmin_powell')
    def check_newton(self):
        N = NormalApproximation(model)
        N.fit('newton')
    def check_sig(self):
        N = NormalApproximation(model)
        N.fit('fmin')
        assert((abs(N._sig * N._sig.T - N._C) < 1.0e-14).all())        
    def check_draws(self):
        N = NormalApproximation(model)
        N.fit('fmin')
        draws = []
        for i in range(1000):
            N.draw()
            draws.append(hstack((N.alpha.value, N.beta.value)))
        draws = array(draws)
        plot(draws[:,0],draws[:,1],'k.')
        xlabel(r'$\alpha$')
        ylabel(r'$\beta$')
        
if __name__=='__main__':
    NumpyTest().run()