"""
A model for the disasters data with a changepoint

changepoint ~ U(0,111)
early_mean ~ Exp(1.)
late_mean ~ Exp(1.)
disasters[t] ~ Po(early_mean if t <= switchpoint, late_mean otherwise)

"""

from PyMC2 import stoch, data, discrete_stoch
from numpy import array, log, sum, random
from numpy.random import randint
from PyMC2 import uniform_like, exponential_like, poisson_like
from PyMC2 import rexponential

__all__ = ['disasters_array', 'switchpoint', 'early_mean', 'late_mean', 'disasters']

disasters_array =   array([ 4, 5, 4, 0, 1, 4, 3, 4, 0, 6, 3, 3, 4, 0, 2, 6,
                            3, 3, 5, 4, 5, 3, 1, 4, 4, 1, 5, 5, 3, 4, 2, 5,
                            2, 2, 3, 4, 2, 1, 3, 2, 2, 1, 1, 1, 1, 3, 0, 0,
                            1, 0, 1, 1, 0, 0, 3, 1, 0, 3, 2, 2, 0, 1, 1, 1,
                            0, 1, 0, 1, 0, 0, 0, 2, 1, 0, 0, 0, 1, 1, 0, 2,
                            3, 3, 1, 1, 2, 1, 1, 1, 1, 2, 4, 2, 0, 0, 1, 4,
                            0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 1])

# Define data and stochs

@discrete_stoch
def switchpoint(value=50, length=110):
    """Change time for rate stoch."""

    def logp(value, length):
        return uniform_like(value, 0, length)
        
    def random(length):
        return randint(length)
        
    rseed = 1.


@stoch
def early_mean(value=1., rate=1.):
    """Rate stoch of poisson distribution."""

    def logp(value, rate):
        return exponential_like(value, rate)
        
    def random(rate):
        return rexponential(rate)
        
    rseed = 1.


@stoch
def late_mean(value=.1, rate = 1.):
    """Rate stoch of poisson distribution."""

    def logp(value, rate):
        return exponential_like(value, rate)
        
    def random(rate):
        return rexponential(rate)
        
    rseed = 1.

    
@data
@discrete_stoch
def disasters(  value = disasters_array, 
                early_mean = early_mean, 
                late_mean = late_mean, 
                switchpoint = switchpoint):
    """Annual occurences of coal mining disasters."""
    return poisson_like(value[:switchpoint],early_mean) + poisson_like(value[switchpoint+1:],late_mean)
