'''
Created on Mar 12, 2011

@author: johnsalvatier
'''
import numdifftools as nd
import numpy as np 
from core import *

def approx_cov(model,chain_state):
    """
    returns an approximation of the hessian at the current chain location 
    """
    vars = model.vars
    dlogp = model_dlogp(model, vars)
    mapping = DASpaceMap(vars)
    
    def grad_logp(x): 
        return np.nan_to_num(-dlogp(mapping.rproject(x, chain_state)))
    
    #find the jacobian of the gradient function at the current position
    #this should be the hessian; invert it to find the approximate covariance matrix
    return np.linalg.inv(nd.Jacobian(grad_logp)(mapping.project(chain_state)))