"""
Markov Chain methods in Python.

A toolkit of stochastic methods for biometric analysis. Features
a Metropolis-Hastings MCMC sampler and both linear and unscented 
(non-linear) Kalman filters.

Pre-requisite modules: numpy, matplotlib
Required external components: TclTk

"""
__modules__ = [ 'PyMCBase',
                'distributions',
                'utils',
                'PyMCObjects',
                'SamplingMethods',
                'Container',
                'Model',
                'MultiModelInference',
                'InstantiationDecorators',
                'testsuite',
                'NormalApproximation']
                
__optmodules__ = []
#ClosedCapture, OpenCapture   

for mod in __optmodules__:
    try:
      exec "import %s" % mod
    except ImportError:
        print 'Error importing module ', mod

for mod in __modules__:
    exec "from %s import *" % mod

##try:
##   import parallel
##except ImportError:
##   print 'For parallel-processing functionality install IPython1.'

del mod



    
