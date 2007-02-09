###
# no_trace database backend
# No memory whatsoever of the samples.
###

from numpy import zeros,shape

class Trace(object):
    """The no-trace backend provides a minimalistic backend where absolutely no
    trace of the values sampled is kept. This may be useful for testing 
    purposes.
    """ 
    
    def __init__(self, pymc_object, db):
        """Initialize the instance.
        :Parameters:
          obj : PyMC object
            Node or Parameter instance.
          db : database instance
        """
        self.obj = pymc_object
        self.db = db
        self._trace = []
        
    def _initialize(self, length):
        """Initialize the trace."""
        pass
            
    def tally(self, index):
        """Dummy method. This does abolutely nothing."""
        pass

    def gettrace(self, burn=0, thin=1, chain=-1, slicing=None):
        """
        This doesn't return anything.
        
        Input:
          - burn (int): The number of transient steps to skip.
          - thin (int): Keep one in thin.
          - chain (int): The index of the chain to fetch. If None, return all chains. 
          - slicing: A slice, overriding burn and thin assignement. 
        """
        raise AttributeError, self.obj.__name__ + " has no trace"

    def _finalize(self, *args, **kwds):
        pass
    
class Database(object):
    """The no-trace database is empty."""
    def __init__(self, model):
        self.model = model
        
    def _initialize(self, *args, **kwds):
        """Initialize database."""
        pass
    def _finalize(self, *args, **kwds):
        """Close database."""
        pass
