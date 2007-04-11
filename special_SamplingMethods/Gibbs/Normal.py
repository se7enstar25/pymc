from PyMC2 import SamplingMethod, Parameter, Node, Container
from PyMC2.utils import msqrt
from numpy import asarray
from numpy.random import normal

class NormalGibbs(SamplingMethod):
    """
    Applies to m in following submodel, where i indexes Parameter/ Node objects:
    
    d_i ~ind N(A_i m + b_i, d_tau_i)
    m ~ N(mu, tau)
    
    S = NormalGibbs(m, mu, tau, d, A, b, d_tau)
    
    The argument m must be a Parameter.
    
    The arguments mu and tau may be:
    - Arrays
    - Scalars
    - Parameters
    - Nodes
    
    The argument may be:
    - A Parameter
    - A Container or other iterable containing Parameters.
    
    The arguments A, b, and d_tau may be:
    - Arrays
    - Parameters
    - Nodes
    - Containers or other iterables
    
    """
    def __init__(self, m, mu, tau, d, A, b, d_tau):
        SamplingMethod.__init(self, [m])
        
        self.mu = mu
        self.tau = tau
        
        length = len(self.m.value.ravel())
        self.length = length
        
        variable_length_params = {'d': d, 'A': A, 'b': b, 'd_tau': d_tau}
        
        for p in variable_length_params:
            if len(p[1]) > 1:
                self.__dict__[p[0]] = Container(p[1])
            else:
                self.__dict__[p[0]] = p[1]
                
        @node
        def M_and_sig(  base_mean = self.mu, 
                        base_tau = self.tau, 
                        obs_vals = self.d,
                        lintrans = A,
                        const_part = self.b,
                        obs_taus = self.d_tau,):
            
            # ... get M and C
            
            sig = asarray(msqrt(C))
            
            return {'M':M, 'sig': sig}
        
        self.M_and_sig = M_and_sig
        
    def step(self):
        M = self.M_and_sig.value['M']
        sig = self.M_and_sig.value['sig']
        self.m.value =  (M + dot(normal(size=self.length), sig)).reshape(self.m.value.shape)