'''
Created on Mar 7, 2011

@author: johnsalvatier
'''
import theano
from theano.tensor import sum, grad, TensorType, TensorVariable
import theano.tensor as tt
import theano.tensor as t 
from theano import function
import numpy as np 
from __builtin__ import sum as builtin_sum
import time 

def FreeVariable( name, shape, dtype = 'float64'):
    """creates a TensorVariable of the given shape and type"""
    shape = np.atleast_1d(shape)
    var = TensorType(str(dtype), shape == 1)(name)
    var.dshape = tuple(shape)
    var.dsize = int(np.prod(shape))
    return var

class Model(object):
    """encapsulates the variables and the likelihood factors"""
    def __init__(self):
       self.vars = []
       self.factors = [] 

"""
these functions add random variables
"""

def AddData(model, data, distribution):
    model.factors.append(distribution(t.constant(data)))

def AddVar(model, name, distribution, shape = 1, dtype = 'float64', test = None):
    var = FreeVariable(name, shape, dtype)
    model.vars.append(var)
    if test is not None: 
        var.tag.test_value = test 
    model.factors.append(distribution(var))
    return var
    
def AddVarIndirectElemewise(model, name,proximate_calc, distribution, shape = 1):
    var = FreeVariable(name, shape)
    model.vars.append(var)
    prox_var = proximate_calc(var)
    
    model.factors.append(distribution(prox_var) + log_jacobian_determinant(prox_var, var))
    return var
    
def log_jacobian_determinant(var1, var2):
    # need to find a way to calculate the log of the jacobian determinant easily, 
    raise NotImplementedError()
    # in the case of elemwise operations we can just sum the gradients
    # so we might just test if var1 is elemwise wrt to var2 and then calculate the gradients, summing their logs
    # otherwise throw an error
    return
    
def continuous_vars(model):
    return [ var for var in model.vars if var.dtype in continuous_types] 


"""
these functions compile log-posterior functions (and derivatives)
"""
def model_func(model, calcs, mode = None):
    f = function(model.vars, 
             calcs,
             allow_input_downcast = True, mode = mode)
    def fn(state):
        return f(**state)
    return fn

def model_logp(model, mode = None):
    return model_func(model, logp_calc(model), mode)

def model_dlogp(model, dvars = None, mode = None ):    
    return model_func(model, dlogp_calc(model, dvars), mode)
    
def model_logp_dlogp(model, dvars = None, mode = None ):    
    return model_func(model, [logp_calc(model), dlogp_calc(model, dvars)], mode)


"""
The functions build graphs from other graphs
"""
def flatgrad(f, v):
    return tt.flatten(grad(f, v))

def gradient(f, dvars):
    return tt.concatenate([flatgrad(f, v) for v in dvars])

def jacobian(f, dvars):
    def jac(v):
        def grad_i (i, f1, v): 
            return flatgrad(f1[i], v)
        
        return theano.scan(grad_i, sequences = tt.arange(f.shape[0]), non_sequences = [f,v])[0]

    return tt.concatenate(map(jac, dvars))

def hessian(f, dvars):
    return jacobian(gradient(f, dvars), dvars)



def hessian_diag(f, dvars):
    def hess(v):
        df = tt.flatten(grad(f, v))
        def grad_i (i, df1, v): 
            return flatgrad(df1[i], v)[i]
        
        return theano.scan(grad_i, sequences = tt.arange(f.shape[0]), non_sequences = [df,v])[0]

    return tt.concatenate(map(hess, dvars))

"""
These functions build log-posterior graphs (and derivatives)
   """ 
def logp_calc(model):  
    return t.add(*map(sum,model.factors))

def dercalc(d_calc):
    def der_calc(model, dvars = None):
        if dvars is None:
            dvars = continuous_vars(model)
        
        return d_calc(logp_calc(model), dvars)
    return der_calc

dlogp_calc = dercalc(gradient)
hess_calc = dercalc(jacobian)
hess_diag_calc = dercalc(hessian_diag)

    
class DASpaceMap(object):
    """ encapsulates a mapping of 
        dict space <-> array space"""
    def __init__(self,free_vars):
        self.dimensions = 0
        
        self.slices = {}
        self.vars = {}
        for var in free_vars:       
            self.vars[str(var)] = var 
            self.slices[str(var)] = slice(self.dimensions, self.dimensions + var.dsize)
            self.dimensions += var.dsize
            
    def project(self, d, a = None):
        """project dict space -> array space"""
        if a is None:
            a = np.empty(self.dimensions)
        else:
            a = np.copy(a)
        
        for varname, value in d.iteritems():
            try:    
                a[self.slices[varname]] = np.ravel(value)
            except KeyError:
                pass
        return a
    
    def rproject(self, a, d = {}):
        """project array space -> dict space"""
        d = d.copy()
            
        for var, slice in self.slices.iteritems():
            d[var] = np.reshape(a[slice], self.vars[var].dshape)
            
        return d

def sample(draws, step, chain, sample_history, state = None):
    """draw a number of samples using the given step method. Multiple step methods supported via compound step method
    returns the amount of time taken"""
    start = time.time()
    for i in xrange(int(draws)):
        state, chain = step(state, chain)
        sample_history.record(chain)
        
    return state, (time.time() - start)


bool_types = set(['int8'])
   
int_types = set(['int8',
            'int16' ,   
            'int32',
            'int64',
            'uint8',
            'uint16',
            'uint32',
            'uint64'])
float_types = set(['float32',
              'float64'])
complex_types = set(['complex64',
                'complex128'])
continuous_types = float_types | complex_types
discrete_types = bool_types | int_types

#theano stuff 
theano.config.warn.sum_div_dimshuffle_bug = False
