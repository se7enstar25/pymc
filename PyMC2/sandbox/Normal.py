#from GibbsSampler import Gibbs
from PyMC2.SamplingMethods import SamplingMethod

class MVNormalChildren(SamplingMethod):
    """
    If a parameter p's children are all normally distributed:
    
    child.ravel() ~ N(F * parameter + a, tau)
    
    where F is a matrix (which can be different for each child), 
    a is an array, and tau is a matrix, then this sampling method 
    can be used to sample p.
    
    If parameter's prior is itself normal, cNormalWithNormalChildren
    is preferable.

    NormalWithNormalChildren(parameter, F_dict, a_dict, tau_dict)

    :Arguments:
    parameter: p
    F_dict: a child-keyed dictionary. F_dict[child], where child is
        a normally-distributed parameter, is a node whose value is the Fbda
        matrix associated with that parameter.
    a_dict: a child-keyed dictionary. a_dict[child], where child is
            a normally-distributed parameter, is a node whose value is the a
            array associated with that parameter.

    :SeeAlso: cMVNormalWithMVNormalChildren, for fully conjugate sampling,
        Normal.tex for more detailed documentation.
    """
    def __init__(self, parameter, F_dict, a_dict, tau_dict):
        
        self.parameter = parameter
        self.F_dict = F_dict
        self.a_dict = a_dict
        self.tau_dict = tau_dict
        
        for F in self.F_dict.values() + self.tau_dict.values():
            if not isinstance(F, Node) or not isinstance(F.value, matrix):
                raise taualueError, 'All elements of F_dict and tau_dict must be matrix-valued nodes'
                
        for a in self.a_dict.values():
            if not isinstance(a, Node) or not isinstance(a.value, ndarray):
                raise taualueError, 'All elements of a_dict must be array-valued nodes'
        

        SamplingMethod.__init__(self,[parameter] + F_dict.values() + a_dict.values())

        #Mallocs
        if not shape(self.parameter.value):
            self.N=1
            self.shape=()
        else:
            self.N = len(self.parameter.value.ravel())
            self.shape = self.parameter.value.shape
            
        self.tau = asmatrix(zeros((self.N,self.N)),dtype=float)
        self.mu = zeros(self.N,dtype=float)         
        
        self.default = OneAtATimeMetropolis([parameter])

    def step(self):

        logp = self.parameter.logp

        self.tau *= 0.
        self.mu *= 0.
        for child in self.children:
            self.tau += self.F_dict[child].value.T * self.tau_dict[child].value * self.F_dict[child].value
            self.mu =   self.mu + self.F_dict[child].value.T * self.tau_dict[child].value * \
                        (child.value - self.a_dict[child].value).ravel()

        V = self.tau.I
        self.mu = V*self.mu
    
        sig = msqrt(V)

        self.parameter.value = asarray(self.mu + (normal(size=self.N) * sig).T).reshape(self.shape)

        try:    
            logp_p = self.parameter.logp
        except LikelihoodError:
            self.parameter.revert()
            self._rejected += 1
            return

        if log(random()) > logp_p - logp:
            self._rejected += 1
            self.parameter.revert()
            self._rejected += 1
            return

        self._accepted += 1

class cMVNormalChildren(MVNormalChildren):
    """
    If a parameter p's children are all normally distributed:
    
    child.ravel() ~ N(F * parameter + a, tau)
    
    where F is a matrix (which can be different for each child), 
    a is an array, and tau is a matrix, and p has a
    normal prior, then this sampling method can be used to sample p.

    NormalWithNormalChildren(parameter, F_dict, a_dict, tau_dict)

    :Arguments:
    parameter: p
    F_dict: a child-keyed dictionary. F_dict[child], where child is
        a normally-distributed parameter, is a node whose value is the F
        matrix associated with that parameter.
    a_dict: a child-keyed dictionary. a_dict[child], is a node whose value 
        is the a array associated with that parameter.
    tau_dict: a child-keyed dictionary. tau_dict[child] is a node
        whose value is the tau matrix associated with that parameter.
    prior_mu, prior_tau: nodes whose values are the prior mean and
        precision of p.

    :SeeAlso: MVNormalWithMVNormalChildren, for nonconjugate sampling,
        Normal.tex for more detailed documentation.
    """ 
    def __init__(self, parameter, F_dict, a_dict, tau_dict, prior_mu, prior_tau):
        self.prior_mu = prior_mu
        self.prior_tau = prior_tau
        MVNormalWithNormalChildren.__init__(self, parameter, F_dict, a_dict, tau_dict)
    def step(self):

        logp = self.parameter.logp

        self.tau = self.prior_tau.value
        self.mu = self.prior_tau.value * self.prior_mu.value
        
        for child in self.children:
            self.tau += self.F_dict[child].value.T * self.tau_dict[child].value * self.F_dict[child].value
            self.mu =   self.mu + self.F_dict[child].value.T * self.tau_dict[child].value * \
                        (child.value - self.a_dict[child].value).ravel()

        V = self.tau.I
        self.mu = V*self.mu
    
        sig = msqrt(V)

        self.parameter.value = asarray(self.mu + (normal(size=self.N) * sig).T).reshape(self.shape)

        self._accepted += 1
