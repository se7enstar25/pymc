__docformat__='reStructuredText'

__author__ = 'Anand Patil, anand.prabhakar.patil@gmail.com'

import os

class ZeroProbability(ValueError):
    "Log-likelihood is invalid or negative informationnite"
    pass


class Node(object):
    """
    The base class from which Stochastic, Deterministic and Potential inherit.
    Shouldn't need to be instantiated directly.
    
    :Parameters:
          -doc : string
              The docstring for this dtrm.

          -name : string
              The name of this dtrm.

          -parents : dictionary
              A dictionary containing the parents of this dtrm.

          -trace : boolean
              A boolean indicating whether this dtrm's value 
              should be traced (in MCMC).

          -cache_depth : integer   
              An integer indicating how many of this dtrm's
              value computations should be 'memorized'.
              
          - verbose (optional) : integer
              Level of output verbosity: 0=none, 1=low, 2=medium, 3=high
    
    :SeeAlso: Stochastic, Deterministic
    """
    def __init__(self, doc, name, parents, cache_depth, trace, verbose=0):

        # Initialize parents and children

        # _parents has to be assigned in each subclass.
        self.children = set()
        
        # Name and docstrings
        self.__doc__ = doc
        self.__name__ = name
        
        # Adopt passed trace
        self.trace = trace
        
        # Flag for feedback verbosity
        self.verbose = verbose

        self._cache_depth = cache_depth
        
        # Add self as child of parents
        for object in self._parents.itervalues():
            if isinstance(object, Node):
                object.children.add(self)
        
        # New lazy function
        self.gen_lazy_function()
                
    def _get_parents(self):
        # Get parents of this object
        return self._parents
        
    def _set_parents(self, new_parents):
        # Define parents of this object
        
        # Iterate over items in ParentDict
        for parent in self._parents.itervalues():
            if isinstance(parent, Node):
                # Remove self as child
                parent.children.discard(self)
                
        # Specify new parents
        self._parents = ParentDict(regular_dict = new_parents, owner = self)
        
        # Get new lazy function
        self.gen_lazy_function()
        
    def _del_parents(self):
        # Deletes all parents of current object
        
        # Remove as child from parents
        for parent in self._parents.itervalues():
            if isinstance(parent, Node):
                parent.children.discard(self)
                
        # Delete parents
        del self._parents
        
    parents = property(fget=_get_parents, fset=_set_parents, fdel=_del_parents)
    
    def __str__(self):
        return self.__repr__()
        
    def __repr__(self):
        return object.__repr__(self).replace('object', self.__name__)
                
    def gen_lazy_function(self):
        pass                

class Variable(Node):
    """
    The base class for Stochastics and Deterministics.
    """
    pass

class ContainerBase(object):
    """
    The base class from which containers inherit.
    """
    __name__ = 'container'
    
    def __init__(self, input):
        if hasattr(input, '__file__'):
            _filename = os.path.split(input.__file__)[-1]
            self.__name__ = os.path.splitext(_filename)[0]
        elif hasattr(input, '__name__'):
            self.__name__ = input.__name__
        else:
            try:
                self.__name__ = input['__name__']
            except: 
                self.__name__ = 'container'
    
    def _get_logp(self):
        return sum(obj.logp for obj in self.stochs | self.potentials | self.data)
    logp = property(_get_logp)
        
class StochasticBase(Variable):
    """
    Abstract base class.
    """
    pass
    
class DeterministicBase(Variable):
    """
    Abstract base class.
    """
    pass
    
class PotentialBase(Node):
    """
    Abstract base class.
    """
    pass
    
class StepMethodBase(object):
    """
    Abstract base class.
    """
    pass    