from PyMC2 import *

def disaster_no_r():
    @discrete_parameter
    def s(value=50, length=110):
        """Change time for rate parameter."""
        return 0.

    @parameter
    def e(value=1., rate=1.):
        """Rate parameter of poisson distribution."""
        return 0.

    @parameter
    def l(value=.1, rate = 1.):
        """Rate parameter of poisson distribution."""
        return 0.
        
    @data(discrete=True)
    def D(  value = 0.,
            switchpoint = s,
            early_rate = e,
            late_rate = l):
        """Annual occurences of coal mining disasters."""
        return 0.
        
    return locals()
        
M = Model(disaster_no_r())
M.DAG(consts=False, path='DisasterModel.dot', format='raw', legend=False)

def disaster_yes_r():
    @discrete_parameter
    def s(value=50, length=110):
        """Change time for rate parameter."""
        return 0.

    @parameter
    def e(value=1., rate=1.):
        """Rate parameter of poisson distribution."""
        return 0.

    @parameter
    def l(value=.1, rate = 1.):
        """Rate parameter of poisson distribution."""
        return 0.
    
    @node
    def r(switchpoint = s,
        early_rate = e,
        late_rate = l):
        return 0.
    
    
    @data(discrete=True)
    def D(  value = 0.,
            rate = r):
        """Annual occurences of coal mining disasters."""
        return 0.
        
    return locals()
        
M = Model(disaster_yes_r())
M.DAG(consts=False, path='DisasterModel2.dot', format='raw', legend=False)

def node_pre():
    @parameter
    def A(value=0):
        return 0.
        
    @parameter
    def B(value=0):
        return 0.
        
    @node
    def C(p1=A, p2=B):
        return 0.
        
    @parameter
    def D(value=0, C = C):
        return 0.
        
    @parameter
    def E(value=0, C=C):
        return 0.
        
    return locals()
    
M = Model(node_pre())
M.DAG(consts=False, path='NodePreInheritance.dot', format='raw', legend=False)    
    
def node_post():
    @parameter
    def A(value=0):
        return 0.
        
    @parameter
    def B(value=0):
        return 0.
        
    @parameter
    def D(value=0, C_p1 = A, C_p2=B):
        return 0.
        
    @parameter
    def E(value=0, C_p1=A, C_p2 = B):
        return 0.
        
    return locals()
    
M = Model(node_post())
M.DAG(consts=False, path='NodePostInheritance.dot', format='raw', legend=False)    
    
    
def survival():
    @parameter
    def beta(value=0):
        return 0.
        
    @data
    @parameter
    def x(value=0):
        return 0.
        
    @node
    def S(covariates = x, coefs = beta):
        return 0.
        
    @data
    @parameter
    def t(value=0, survival = S):
        return 0.
        
    @parameter
    def a(value=0):
        return 0.
        
    @parameter
    def b(value=0):
        return 0.
    
    @potential
    def gamma(survival = S, param1=a, param2=b):
        return 0.
    
    return locals()
    
M = Model(survival())
M.DAG(consts=False, path='SurvivalModel.dot', format='raw', legend=False)    
    
M = Model(survival())
M.DAG(consts=False, path='SurvivalModelCollapsed.dot', format='raw', legend=False, collapse_potentials=True)