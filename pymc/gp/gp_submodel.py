# Copyright (c) Anand Patil, 2007

__docformat__ = 'reStructuredText'

__all__ = ['GaussianProcess','GPEvaluation','GPSubmodel']

import pymc as pm
import copy
import numpy as np
from Realization import Realization


__all__ = ['GaussianProcess', 'GPEvaluation', 'GPSubmodel']

def gp_logp(x, M, C, mesh, f_eval, M_obs, C_obs):
    raise TypeError, 'GP objects have no logp function'

def gp_rand(M, C, mesh, f_eval, M_obs, C_obs, size=None):
    # M and C are input pre-observed, so no need to 
    out = pm.gp.Realization(M_obs, C_obs)
    out.x_sofar = mesh
    out.f_sofar = f_eval
    out.M = M
    out.C = C
    return out

class GaussianProcess(pm.Stochastic):
    """
    FIXME: docstring
    """
    
    def __init__(self,name,submodel,trace=True,value=None,rseed=False,
                    observed=False,cache_depth=2,plot=None,verbose=None,isdata=None):
                
        self.submodel = submodel
        
        pm.Stochastic.__init__(self,gp_logp,GaussianProcess.__doc__,name,
                                {'M':submodel.M, 'C':submodel.C,'mesh':submodel.mesh, 'f_eval':submodel.f_eval, 'M_obs':submodel.M_obs, 'C_obs':submodel.C_obs},
                                gp_rand,trace,value,np.dtype('object'),rseed,observed,cache_depth,plot,verbose,isdata,False)
        
        self.rand()
        
    def gen_lazy_function(self):
        pass
        
    def get_logp(self):
        raise TypeError, 'Gaussian process %s has no logp.'%self.__name__
        
    def set_logp(self, new_logp):
        raise TypeError, 'Gaussian process %s has no logp.'%self.__name__
        
    logp = property(fget = get_logp, fset = set_logp)


class GPEvaluation(pm.MvNormalChol):
    pass
    
class GPSubmodel(pm.ObjectContainer):
    """
    FIXME: docstring
    """
    
    def __init__(self, name, M, C, mesh, init_vals=None, obs_on_mesh=False, tally_all=False):
        
        mesh = pm.Lambda('%s_mesh'%name, lambda mesh=mesh: pm.gp.regularize_array(mesh))
        name = name
        
        @pm.deterministic(trace=tally_all, name='%s_covariance_bits'%name)
        def covariance_bits(C=C,mesh=mesh):
            """
            Both the realization 'f' and the on-mesh evaluation 'f_eval' need the 
            Cholesky factor of the covariance evaluation. The Gibbs step method 
            also needs the full covariance evaluation. 
            
            Both these things can be got as byproducts of Covariance.observe. Keeping the
            observed covariance and using it as the parent of f means the computations only
            get done once.
            """
            C_obs = copy.copy(C)
            try:
                U, C_eval = C_obs.observe(mesh, np.zeros(mesh.shape[0]), output_type='s')
                return U.T.copy('F'), C_eval, C_obs
            except np.linalg.LinAlgError:
                return None

        S_eval = covariance_bits[0]
        C_eval = covariance_bits[1]
        C_obs = covariance_bits[2]
        
        M_eval = pm.Lambda('%s_M_eval'%name, lambda M=M, mesh=mesh: M(mesh), trace=tally_all)
                
        @pm.potential(name = '%s_fr_check'%name)
        def fr_check(cb=covariance_bits):
            """
            Forbids non-positive-definite C_evals.
            """
            if cb is None:
                return -np.inf
            else:
                return 0
        fr_check=fr_check
        f_eval = GPEvaluation('%s_f_eval'%name, mu=M_eval, sig=S_eval, value=init_vals, trace=True, observed=obs_on_mesh)
        
        @pm.deterministic(trace=tally_all, name='%s_covariance_bits'%name)
        def M_obs(M=M, f_eval=f_eval, C_obs=C_obs, mesh=mesh):
            """
            Creates an observed mean object to match C_obs.
            """
            M_obs = copy.copy(M)
            M_obs.observe(C_obs,mesh,f_eval)
            return M_obs
        M_obs = M_obs
        f_eval = f_eval
        self.mesh = mesh
        
        self.M = M
        self.C = C
        self.M_obs = M_obs
        self.C_obs = C_obs
        self.f_eval = f_eval
        f = GaussianProcess('%s_f'%name, self, trace=tally_all)
        f.rand()
        l = locals()
        lk = filter(lambda k:isinstance(l[k],pm.Node), l.keys())
        l = dict([(k,l[k]) for k in lk])
        pm.ObjectContainer.__init__(self, l)
        
    def getobjects(self):
        names = ['M_eval','C_eval','S_eval','f_eval','f','fr_check']
        return dict(zip(['%s_%s'%(self.name, name) for name in names], [getattr(self, name) for name in names]))