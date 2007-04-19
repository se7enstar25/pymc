"""
The trans-dimensional example

"""
from numpy.testing import *
from pylab import *
PLOT=True

class test_Sampler(NumpyTestCase):
    def check(self):
        from PyMC2 import Sampler
        from PyMC2.examples import trans_dimensional
        M = Sampler(trans_dimensional)
        M.sample(5000,0,10,verbose=False)
        if PLOT:
            # It would be nicer to write plot(M.trace(switchpoint)), since switchpoint is local to M.
            clf()
            plot(M.K.trace())
            title('K')
            
            figure()
            plot(M.A.trace()[:,0])
            title('A')
            
            show()
            

if __name__ == '__main__':
    NumpyTest().run()
    
