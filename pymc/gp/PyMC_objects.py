# Copyright (c) Anand Patil, 2007

__docformat__ = 'reStructuredText'

__all__ = ['GP_array_logp', 'GP_array_random', 'GP', 'GPMetropolis', 'GPNormal', 'GPParentMetropolis']

import pymc as pm
import linalg_utils
import copy
import types
import numpy as np

from Realization import Realization
from Mean import Mean
from Covariance import Covariance
from GPutils import observe, regularize_array


def GP_array_logp(value, M, U):
    return pm.flib.chol_mvnorm(value,M,U.T)

def GP_array_random(M, U, scale=1.):
    b = np.random.normal(size=len(M.ravel()))
    linalg_utils.dtrmm_wrap(a=U,b=b,uplo='U',transa='T')
    return M+b*scale

class GP(pm.Stochastic):
    """
    f = GP(M, C, [mesh, doc, name, init_mesh_vals, mesh_eval_isdata, trace, cache_depth, verbose])
    
    A stochastic variable valued as a Realization object.
    
    :Arguments:
    
        - M: A Mean instance or pm.deterministic variable valued as a Mean instance.
        
        - C: A Covariance instance or pm.deterministic variable valued as a Covariance instance.
        
        - mesh: The mesh on which self's log-probability will be computed. See documentation.
        
        - init_mesh_vals: Initial values for self over mesh.
        
        - mesh_eval_isdata: Whether self's evaluation over mesh is known with no uncertainty.
        
        - trace: Whether self should be traced. See pymc documentation.
        
        - cache_depth: See pymc documentation.
        
        - verbose: An integer from 0 to 3.
        
    :SeeAlso: Realization, pymc.pm.Stochastic, pymc.pm.Deterministic, GPMetropolis, GPNormal
    """
    def __init__(self,
                 M,
                 C,
                 mesh=None,
                 doc="A GP realization-valued stochastic variable",
                 name="GP",                 
                 init_mesh_vals = None,
                 mesh_eval_isdata = False,
                 trace=True,
                 cache_depth=2,
                 verbose=False):

        self.conjugate=True
        
        if not isinstance(mesh, np.ndarray) and mesh is not None:
            raise ValueError, name + ": __init__ argument 'mesh' must be ndarray."
            
        self.mesh = regularize_array(mesh)
            
        # Safety
        if isinstance(M, pm.Deterministic):
            if not isinstance(M.value, Mean):
                raise ValueError,   'GP' + self.__name__ + ': Argument M must be Mean instance '+\
                                    'or pm.Deterministic valued as Mean instance, got pm.Deterministic valued as ' + M.__class__.__name__
        elif not isinstance(M, Mean):
            raise ValueError,   'GP' + self.__name__ + ': Argument M must be Mean instance '+\
                                'or pm.Deterministic valued as Mean instance, got ' + M.__class__.__name__

        if isinstance(C, pm.Deterministic):
            if not isinstance(C.value, Covariance):
                raise ValueError,   'GP' + self.__name__ + ': Argument C must be Covariance instance '+\
                                    'or pm.Deterministic valued as Covariance instance, got pm.Deterministic valued as ' + C.__class__.__name__
        elif not isinstance(C, Covariance):
            raise ValueError,   'GP' + self.__name__ + ': Argument C must be Covariance instance '+\
                                'or pm.Deterministic valued as Covariance instance, got ' + C.__class__.__name__        
                                
        # This function will be used to draw values for self conditional on self's parents.
        
        def random_fun(M,C):
            return Realization(M,C)
        self._random = random_fun
                
        if self.mesh is not None:
        
            @pm.deterministic(verbose=verbose-1, cache_depth=cache_depth, trace=False)
            def M_mesh(M=M, mesh=mesh):
                """
                The mean function evaluated on the mesh,
                cached for speed.
                """
                return M(mesh, regularize=False)
            M_mesh.__name__ = name + '_M_mesh'
        
            @pm.deterministic(verbose=verbose-1, cache_depth=cache_depth, trace=False)
            def U_mesh(C=C, mesh=mesh):
                """
                The upper-triangular Cholesky factor of the
                covariance function evaluated on the mesh,
                cached for speed.
                """
                # TODO: Will need to change this when sparse covariances
                # are available. dpotrf doesn't know about sparse covariances.
                
                # Putting this here to short-circuit evaluation of the
                # covariance prevents the seg fault...
                # return np.eye(mesh.shape[0])
                
                U = C(mesh,mesh, regularize=False)
                info = linalg_utils.dpotrf_wrap(U)
    
                if info>0:
                    return np.linalg.LinAlgError
                return U
            U_mesh.__name__ = name + '_U_mesh'
        
            self.M_mesh = M_mesh
            self.U_mesh = U_mesh
            
        def logp_fun(value, M, C):
            if self.mesh is None:
                if self.verbose > 1:
                    print '\t%s: No mesh, returning 0.' % self.__name__
                return 0.
            elif self.U_mesh.value is np.linalg.LinAlgError:
                if self.verbose > 1:
                    print '\t%s: Covariance not positive definite on mesh, returning -infinity.' % self.__name__
                return -np.Inf
            else:                
                if self.verbose > 1:
                    print '\t%s: Computing log-probability.' % self.__name__
                return GP_array_logp(value(self.mesh), self.M_mesh.value, self.U_mesh.value)
                
                    
        @pm.deterministic(verbose=verbose-1, cache_depth=cache_depth, trace=False)
        def init_val(M=M, C=C, init_mesh = self.mesh, init_mesh_vals = init_mesh_vals):
            if init_mesh_vals is not None:
                return Realization(M, C, init_mesh, init_mesh_vals.ravel(), regularize=False)
            else:
                return Realization(M, C)
        init_val.__name__ = name + '_init_val'
                    
        pm.Stochastic.__init__( self, 
                            logp=logp_fun, 
                            doc=doc, 
                            name=name, 
                            parents={'M': M, 'C': C}, 
                            random = random_fun, 
                            trace=trace, 
                            value=init_val.value, 
                            isdata=False,
                            cache_depth=cache_depth,
                            verbose = verbose)

    def random_off_mesh(self):
        if self.mesh is not None:
            self.value = Realization(M, C, init_mesh = self.mesh, init_mesh_vals = self.value(self.mesh).ravel(), regularize=False)
        else:
            self.random()

class GPParentMetropolis(pm.Metropolis):

    """
    M = GPParentMetropolis(stochastic, scale[, verbose, metro_method])
    
    
    Wraps a pm.Metropolis instance to make it work well when one of its
    children is a GP.
    
    
    :Arguments:
    
        -   `stochastic`: The parent stochastic variable.
    
        -   `scale`: A float.
    
        -   `verbose`: A boolean indicating whether verbose mode should be on.
    
        -   `metro_method`: The pm.Metropolis subclass instance to be wrapped.
        
        
    :SeeAlso: GPMetropolis, GPNormal
    """
    def __init__(self, stochastic=None, scale=1., verbose=False, metro_method = None):
        
        if (stochastic is None and metro_method is None) or (stochastic is not None and metro_method is not None):
            raise ValueError, 'Either stochastic OR metro_method should be provided, not both.'
        
        if stochastic is not None:
            stochastics = [stochastic]
            stochastic = stochastic

            # Pick the best step method to wrap if none is provided.
            if metro_method is None:                
                pm.StepMethodRegistry.remove(GPParentMetropolis)
                self.metro_method = pm.assign_method(stochastic, scale)
                self.metro_class = self.metro_method.__class__
                self.scale = scale
                pm.StepMethodRegistry.append(GPParentMetropolis)

        # If the user provides a step method, wrap it.
        if metro_method is not None:
            self.metro_method = metro_method
            self.metro_class = metro_method.__class__
            stochastics = metro_method.stochastics
        
        # Call to pm.StepMethod's init method.
        pm.StepMethod.__init__(self, stochastics, verbose=verbose)


        # Extend self's children through the GP-valued stochastics
        # and add them to the wrapped method's children.
        fs = set([])
        for child in self.children:
            if isinstance(child, GP):
                fs.add(child)
                break

        self.fs = fs
        for f in self.fs:
            self.children |= f.extended_children

        self.metro_method.children |= self.children
        self.verbose = verbose

        # Record all the meshes of self's GP-valued children.
        
        self._id = 'GPParent_'+ self.metro_method._id
        
        self.C = {}
        self.M = {}
        
        for f in self.fs:
            
            @pm.deterministic
            def C(C=f.parents['C']):
                return C

            @pm.deterministic
            def M(M=f.parents['M']):
                return M     
                   
            self.C[f] = C
            self.M[f] = M


        # Wrapped method's reject() method will be replaced with this.
        def reject_with_realization(metro_method):
            """
            Reject the proposed values for f and stochastic.
            """
            if self.verbose:
                print self._id + ' rejecting'
            self.metro_class.reject(metro_method)
            for f in self.fs:
                # f.value = f.last_value
                f.revert()

        setattr(self.metro_method, 'reject', types.MethodType(reject_with_realization, self.metro_method, self.metro_class))                


        # Wrapped method's propose() method will be replaced with this.
        def propose_with_realization(metro_method):
            """
            Propose a new value for f and stochastic.
            """

            if self.verbose:
                print self._id + ' proposing'
            self.metro_class.propose(metro_method)

            # Don't attempt to generate a realization if the parent jump was to an
            # illegal value
            try:
                for stochastic in self.metro_method.stochastics:
                    stochastic.logp
            except pm.ZeroProbability:
                self.metro_class.reject(metro_method)
                return

            try:
                for f in self.fs:    
                    if f.mesh is not None:
                        f.value = Realization(self.M[f].value,self.C[f].value,init_mesh=f.mesh,
                                    init_vals=f.value(f.mesh, regularize=False).ravel(), regularize=False)
                    else:
                        f.value = Realization(self.M[f].value,self.C[f].value)
            except np.linalg.LinAlgError:
                self.metro_class.reject(metro_method)
        
        setattr(self.metro_method, 'propose', types.MethodType(propose_with_realization, self.metro_method, self.metro_class))
    
    @staticmethod
    def competence(stochastic):
        """
        Competence function for GPParentMetropolis
        """

        if any([isinstance(child, GP) for child in stochastic.extended_children]):
            return 3
        else:
            return 0
    
    # _model, _accepted, _rejected and _scale have to be properties that pass 
    # set-values on to the wrapped method.
    def _get_model(self):
        return self.model
    def _set_model(self, model):  
        self.model = model
        self.metro_method._model = model
    _model = property(_get_model, _set_model)
    
    def _get_accepted(self):
        return self.metro_method._accepted
    def _set_accepted(self, number):
        self.metro_method._accepted = number
    _accepted = property(_get_accepted, _set_accepted)

    def _get_rejected(self):
        return self.metro_method._rejected
    def _set_rejected(self, number):
        self.metro_method._rejected = number
    _rejected = property(_get_rejected, _set_rejected)

    def _get_scale(self):
        return self.metro_method.scale
    def _set_scale(self, number):
        self.metro_method.scale = number
    scale = property(_get_scale, _set_scale)
    
    def _get_verbose(self):
        return self._verbose
    def _set_verbose(self, verbose):
        self._verbose = verbose
        self.metro_method.verbose = verbose
    verbose = property(_get_verbose, _set_verbose)
    
    # Step method just passes the call on to the wrapped method.
    # Remember that the wrapped method's reject() and propose()
    # methods have been overridden.
    def step(self):
        if self.verbose:
            print 
            print self._id + ' stepping.'
        self.metro_method.step()
            
            
class GPMetropolis(pm.Metropolis):
    """
    M = GPMetropolis(stochastic, scale=.01, verbose=False)
    
    Makes a parent of a Realization-valued stochastic take an MCMC step.
    
    :Arguments:
    
        - `stochastic`: The GP instance.
        
        - `scale`: A float.
        
        - `verbose`: A flag.

    :SeeAlso: GPParentMetropolis, GPNormal
    """
    def __init__(self, stochastic, scale=.1, verbose=False):

        f = stochastic
        self.f = stochastic
        pm.StepMethod.__init__(self, [f], verbose)
        self._id = 'GPMetropolis_'+self.f.__name__        

        self.scale = scale
        self.verbose = verbose

        @pm.deterministic
        def C(C=f.parents['C']):
            return C
        
        @pm.deterministic
        def M(M=f.parents['M']):
            return M    

        self.M = M
        self.C = C    
    
    @staticmethod
    def competence(stochastic):
        if isinstance(stochastic,GP):
            return 3
        else:
            return 0
    
    def propose(self):
        """
        Propose a new value for f.
        """
        if self.verbose:
            print self._id + ' proposing.'
        
        if self.f.mesh is not None:
            
            # Generate values for self's value on the mesh.
            new_mesh_value = GP_array_random(M=self.f.value(self.f.mesh, regularize=False), U=self.f.U_mesh.value, scale=self.scale)
            
            last_value = self.f.value(self.f.mesh, regularize = False)
            
            # Generate self's value using those values.
            self.f.value = Realization( self.M.value, 
                                        self.C.value, 
                                        init_mesh=self.f.mesh, 
                                        init_vals=new_mesh_value,
                                        regularize=False)

        else:
            self.f.value = Realization(self.M.value, self.C.value)
            
    def reject(self):
        """
        Reject proposed value for f.
        """
        if self.verbose:
            print self._id + 'rejecting.'
        # self.f.value = self.f.last_value
        self.f.revert()
    
    def step(self):
        if self.verbose:
            print 
            print self._id + ' getting initial prior.'
            try:
                clf()                
                plot(self.f.mesh, self.f.value(self.f.mesh),'b.',markersize=8)
            except:
                pass
         
        logp = self.f.logp


        if self.verbose:
            print self._id + ' getting initial likelihood.'

        loglike = self.loglike
        if self.verbose:
            try:
                title('logp: %i loglike: %i' %(logp, loglike))
                sleep(1.)                
            except:
                pass

        # Sample a candidate value
        self.propose()
        
        if self.verbose:
            try:
                plot(self.f.mesh, self.f.value(self.f.mesh),'r.',markersize=8)
            except:
                pass
            
        # Probability and likelihood for stochastic's proposed value:
        try:
            logp_p = self.f.logp
            loglike_p = self.loglike
            if self.verbose:
                try:
                    title('logp: %i loglike: %i logp_p: %i loglike_p: %i difference: %i' %(logp,loglike,logp_p,loglike_p,logp_p-logp + loglike_p - loglike))
                    sleep(5.)
                except:
                    pass
                
        # Reject right away if jump was to a value forbidden by self's children.
        except pm.ZeroProbability:

            self.reject()
            self._rejected += 1
            if self.verbose:
                print self._id + ' returning.'
                try:
                    title('logp: %i loglike: %i jump forbidden' %(logp, loglike))
                except:
                    pass
                sleep(5.)
            return
            
        if self.verbose:
            print 'logp_p - logp: ', logp_p - logp
            print 'loglike_p - loglike: ', loglike_p - loglike

        # Test
        if np.log(np.random.random()) > logp_p + loglike_p - logp - loglike:
            self.reject()
            self._rejected += 1

        else:
            self._accepted += 1
            if self.verbose:
                print self._id + ' accepting'

        if self.verbose:
            print self._id + ' returning.'



class GPNormal(pm.Gibbs):
    """
    S = GPNormal(f, obs_mesh, obs_V, obs_vals)
    
    
    Causes GP f and its mesh_eval attribute
    to take a pm.Gibbs step. Applies to f in the following submodel:
    
    
    obs_vals ~ N(f(obs_mesh)+offset, obs_V)
    f ~ GP(M,C)
    
    
    :SeeAlso: GPMetropolis, GPParentMetropolis
    """
    
    def __init__(self, f, obs_mesh, obs_V, obs_vals, offset=None):

        if not isinstance(f, GP):
            raise ValueError, 'GPNormal can only handle GPs, cannot handle '+f.__name__
        
        pm.StepMethod.__init__(self, variables=[f])
        self.f = f
        self._id = 'GPNormal_'+self.f.__name__
        
        
        @pm.deterministic
        def obs_mesh(obs_mesh=obs_mesh):
            return regularize_array(obs_mesh)
            
        @pm.deterministic
        def obs_V(obs_V=obs_V, obs_mesh = obs_mesh):
            return np.resize(obs_V, obs_mesh.shape[0])
        
        @pm.deterministic
        def obs_vals(obs_vals=obs_vals):
            return obs_vals
        
        # M_local and C_local's values are copies of f's M and C parents,
        # observed according to obs_mesh and obs_V.
        @pm.deterministic
        def C_local(C = f.parents['C'], obs_mesh = obs_mesh, obs_V = obs_V):
            """
            The covariance, observed according to the children,
            with supporting information.
            """
            C_local = copy.copy(C)
            relevant_slice, obs_vals_new, junk = C_local.observe(obs_mesh, obs_V)
            return (C_local, relevant_slice, obs_vals_new)
            
        @pm.deterministic
        def M_local(C_local = C_local, obs_vals = obs_vals, M = f.parents['M'], offset=offset):
            """
            The mean function, observed according to the children.
            """
            relevant_slice = C_local[1]
            obs_mesh_new = C_local[2]
            
            obs_vals = obs_vals.ravel()[relevant_slice]
            if offset is not None:
                obs_vals = obs_vals - offset.ravel()[relevant_slice]

            M_local = copy.copy(M)
            M_local.observe(C_local[0], obs_mesh_new, obs_vals)
            return M_local
        
        
        self.M_local = M_local
        self.C_local = C_local

    def step(self):
        """
        Samples self.f's value from its conditional distribution.
        """
        try:
            self.f.value = Realization(self.M_local.value, self.C_local.value[0])
        except np.linalg.LinAlgError:
            print 'Covariance was numerically singular when stepping f, trying again.'
            self.step()