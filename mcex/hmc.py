'''
Created on Mar 7, 2011

@author: johnsalvatier
'''
import multi 
import numpy as np

class HMCStep(multi.MultiStep):
    def __init__(self,model, step_size_scaling = .25, trajectory_length = 2., covariance = None, find_mode = True):
        multi.MultiStep(self, model)
        
        self.zero = np.zeros(self.dimensions)
        
        if find_mode:
            find_mode(self.chain_state, self.evaluation)

        if covariance is None:
            self.inv_covariance = #approx hessian
        else :
            self.covariance = covariance
            self.inv_covariance = np.linalg.inv(covariance)
        
        
        step_size = step_size_scaling * self.dimensions**(1/4.)
      
        if np.size(step_size) > 1:
            self.step_size_max, self.step_size_min = step_size
        else :
            self.step_size_max = self.step_size_min = step_size 
        self.trajectory_length = trajectory_length   
        
    def step(self, chain_state):
        #randomize step size
        step_size = np.random.uniform(self.step_size_min, self.step_size_max)
        step_count = int(np.floor(self.trajectory_length / step_size))
        
        
        q = self.var_mapping.apply_to_dict(chain_stat.values)
        start_logp, gradient = self.evaluator.evaluate_as_vector(self.var_mapping, chain_state)
        current_logp = start_logp
        
        # momentum scale proportional to inverse of parameter scale (basically sqrt(covariance))
        p = np.random.multivariate_normal(mean = self.zero ,cov = self.inv_covariance) 
        start_p = p
        
        #use the leapfrog method
        p = p - (step_size/2) * -gradient # half momentum update
        
        for i in range(step_count): 
            #alternate full variable and momentum updates
            q = q + step_size * np.dot(self.covariance, p)
            
            chain_state.consider(self.var_mapping, q)
            current_logp, gradient = self.evaluator.evaluate_as_vector(self.var_mapping, chain_state)
            
            if i != step_count - 1:
                p = p - step_size * -gradient
             
        p = p - (step_size/2) * -gradient  # do a half step momentum update to finish off
        
        p = -p 
            
        log_metrop_ratio = (-start_logp) - (-current_logp) + self.kenergy(start_p) - self.kenergy(p)
        
        self.acceptr = np.minimum(np.exp(log_metrop_ratio), 1.)
        
        
        if (np.isfinite(log_metrop_ratio) and 
            np.log(np.random.uniform()) < log_metrop_ratio):
            
            chain_state.accept()
        else: 
            chain_state.reject() 
                
    
    def kenergy (self, x):
        return .5 * np.dot(x,np.dot(self.covariance, x))
