"""
Markov Chain methods in Python.

A toolkit of stochastic methods for biometric analysis. Features
a Metropolis-Hastings MCMC sampler and both linear and unscented 
(non-linear) Kalman filters.

Pre-requisite modules: numpy, matplotlib
Required external components: TclTk

"""
__modules__ = [ 'distributions',
                'SamplingMethods',
                'Model',
                'MultiModelInference']
                
__optmodules__ = []#['MultiModelInference',]
                    
#ClosedCapture, OpenCapture   

#Uncomment one or the other.
try:
    C_modules = ['PyMCObjects', 'PyMCObjectDecorators']
    for mod in C_modules:
        exec "from %s import *" % mod
except:
    from pure_PyMCObjects import *
          
for mod in __modules__:
    exec "from %s import *" % mod

for mod in __optmodules__:
    try:
      exec "import %s" % mod
    except ImportError:
        print 'Error importing module ', mod

try:
    import parallel
except ImportError:
    print 'For parallel-processing functionality install IPython1.'

del mod
