"""
Markov Chain methods in Python.

A toolkit of stochastic methods for biometric analysis. Features
a Metropolis-Hastings MCMC sampler and both linear and unscented
(non-linear) Kalman filters.

Pre-requisite modules: numpy, matplotlib
Required external components: TclTk

"""

__version__ = '2.2grad'

try:
    import numpy
except ImportError:
    raise ImportError, 'NumPy does not seem to be installed. Please see the user guide.'

# Core modules
from threadpool import *
try:
    import Container_values
    del Container_values
except ImportError:
    raise ImportError, 'You seem to be importing PyMC from inside its source tree. Please change to another directory and try again.'
from Node import *
from Container import *
from PyMCObjects import *
from InstantiationDecorators import *
from CommonDeterministics import *
from NumpyDeterministics import *
from distributions import *
from Model import *
from StepMethods import *
from MCMC import *
from NormalApproximation import *



from tests import test

# Utilities modules
import utils
import CommonDeterministics
import NumpyDeterministics
from CircularStochastic import *
import distributions
import gp

# Optional modules
try:
    from diagnostics import *
except ImportError:
    pass

try:
    import ScipyDistributions
except ImportError:
    pass

try:
    import parallel
except ImportError:
    pass

try:
    import sandbox
except ImportError:
    pass

try:
    import graph
except ImportError:
    pass

try:
    import Matplot
except:
    pass

