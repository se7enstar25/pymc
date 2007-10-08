###
# Basic trace module
# Simply store the trace in memory
###

import PyMC2
from numpy import zeros,shape,concatenate
import base

class Trace(base.Trace):
    """RAM trace 
    
    Store the samples in memory. 
    """
    def __init__(self, value=None, obj=None):
        """Assign an initial value and an internal PyMC object."""
        if value is None:
            self._trace = []
        else:
            self._trace = value
        
        if obj is not None:
            if isinstance(obj, PyMC2.Variable):
                self._obj = obj
            else:
                raise AttributeError, 'Not PyMC object', obj

    def _initialize(self, length):
        """Create an array of zeros with shape (length, shape(obj)), where 
        obj is the internal PyMC Stochastic or Deterministic.
        """
        try:
            self._trace.append( zeros ((length,) + shape(self._obj.value), self._obj.value.dtype) )
        except AttributeError:
            self._trace.append( zeros ((length,) + shape(self._obj.value), dtype=object) )           
        
    def tally(self, index, chain=-1):
        """Store current value."""
        try:
            self._trace[chain][index] = self._obj.value.copy()
        except AttributeError:
            self._trace[chain][index] = self._obj.value

    def truncate(self, index):
        """
        When model receives a keyboard interrupt, it tells the traces
        to truncate their values.
        """
        self._trace[-1] = self._trace[-1][:index]

    def gettrace(self, burn=0, thin=1, chain=-1, slicing=None):
        """Return the trace (last by default).

        :Stochastics:
          - burn (int): The number of transient steps to skip.
          - thin (int): Keep one in thin.
          - chain (int): The index of the chain to fetch. If None, return all chains.
          - slicing: A slice, overriding burn and thin assignement.
        """
        if slicing is None:
            slicing = slice(burn, None, thin)
        if chain is not None:
            return self._trace[chain][slicing]
        else:
            return concatenate(self._trace)[slicing]

    __call__ = gettrace

    def length(self, chain=-1):
        """Return the sample length of given chain. If chain is None,
        return the total length of all chains."""
        return len(self.gettrace(chain=chain))

class Database(base.Database):
    """RAM database. 
    
    Store the samples in memory.
    """
    def __init__(self):
        """Get the Trace from the local scope."""
        self.Trace = Trace
    
