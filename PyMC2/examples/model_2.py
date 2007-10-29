"""
A model for the disasters data with no changepoint:

global_rate ~ Exp(3.)
disasters[t] ~ Po(global_rate)
"""

from PyMC2 import stoch, data, Metropolis, discrete_stoch
from numpy import array, log, sum
from PyMC2 import exponential_like, poisson_like
from PyMC2 import rexponential, constrain

__all__ = ['global_rate', 'disasters', 'disasters_array']
disasters_array =   array([ 4, 5, 4, 0, 1, 4, 3, 4, 0, 6, 3, 3, 4, 0, 2, 6,
                            3, 3, 5, 4, 5, 3, 1, 4, 4, 1, 5, 5, 3, 4, 2, 5,
                            2, 2, 3, 4, 2, 1, 3, 2, 2, 1, 1, 1, 1, 3, 0, 0,
                            1, 0, 1, 1, 0, 0, 3, 1, 0, 3, 2, 2, 0, 1, 1, 1,
                            0, 1, 0, 1, 0, 0, 0, 2, 1, 0, 0, 0, 1, 1, 0, 2,
                            3, 3, 1, 1, 2, 1, 1, 1, 1, 2, 4, 2, 0, 0, 1, 4,
                            0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 1])

# Define the data and stochs

@stoch
def global_rate(value=1., rate=3.):
    """Rate stoch of poisson distribution."""
    
    def logp(value, rate):
        return exponential_like(value, rate)
        
    def random(rate):
        return rexponential(rate)
        
    rseed = 3.
    

@data
@discrete_stoch
def disasters(value = disasters_array, rate = global_rate):
    """Annual occurences of coal mining disasters."""
    return poisson_like(value, rate)


