"""
Class MCMC, which fits probability models using Markov Chain Monte Carlo, is defined here.
"""

from Model import Sampler
from StepMethods import StepMethodRegistry, assign_method

GuiInterrupt = 'Computation halt'
Paused = 'Computation paused'


class MCMC(Sampler):
    """
    This class fits probability models using Markov Chain Monte Carlo. Each stochastic variable
    is assigned a StepMethod object, which makes it take a single MCMC step conditional on the
    rest of the model. These step methods are called in turn.

      >>> A = MCMC(input, db, output_path=None, verbose=0)

      :Parameters:
        - input : module, list, tuple, dictionary, set, object or nothing.
            Model definition, in terms of Stochastics, Deterministics, Potentials and Containers.
            If nothing, all nodes are collected from the base namespace.
        - db : string
            The name of the database backend that will store the values
            of the stochastics and deterministics sampled during the MCMC loop.            
        - output_path : string
            The place where any output files should be put.
        - verbose : integer
            Level of output verbosity: 0=none, 1=low, 2=medium, 3=high

    Inherits all methods and attributes from Model. Subclasses must define the _loop method:

        - _loop(self, *args, **kwargs): Can be called after a sampling run is interrupted 
            (by pausing, halting or a KeyboardInterrupt) to continue the sampling run.
            _loop must be able to handle KeyboardInterrupts gracefully, and should monitor
            the sampler's status periodically. Available status values are:
            - 'ready': Ready to sample.
            - 'paused': A pause has been requested, or the sampler is paused. _loop should return control
                as soon as it is safe to do so.
            - 'halt': A halt has been requested, or the sampler is stopped. _loop should call halt as soon
                as it is safe to do so.
            - 'running': Sampling is in progress.
    
    :SeeAlso: Model, Sampler, StepMethod.
    """
    def __init__(self, input=None, db='ram', output_path=None, **kwds):
        """Initialize an MCMC instance.

        :Parameters:
          - input : module, list, tuple, dictionary, set, object or nothing.
              Model definition, in terms of Stochastics, Deterministics, Potentials and Containers.
              If nothing, all nodes are collected from the base namespace.
          - db : string
              The name of the database backend that will store the values
              of the stochastics and deterministics sampled during the MCMC loop.
          - output_path : string
              The place where any output files should be put.
          - verbose : integer
              Level of output verbosity: 0=none, 1=low, 2=medium, 3=high
          - **kwds : 
              Keywords arguments to be passed to the database instantiation method.
        """
        Sampler.__init__(self, input, db, output_path, **kwds)

        self.step_method_dict = {}
        for s in self.stochastics:
            self.step_method_dict[s] = []
        
        self._state = ['status', '_current_iter', '_iter', '_tune_interval', '_burn', '_thin']
    
    def use_step_method(self, step_method_class, *args, **kwds):
        """
        M.use_step_method(step_method_class, *args, **kwds)
        
        Example of usage: To handle stochastic A with a Metropolis instance,
        
            M.use_step_method(Metropolis, A, sig=.1)
            
        To subsequently get a reference to the new step method,
        
            S = M.step_method_dict[A][0]
        """

        new_method = step_method_class(*args, **kwds)
        if self.verbose > 1:
            print 'Using step method %s. Stochastics: ' % step_method_class.__name__        
        for s in new_method.stochastics:
            self.step_method_dict[s].append(new_method)
            if self.verbose > 1:
                print '\t'+s.__name__
            
        setattr(new_method, '_model', self)
    
    def _assign_step_methods(self):
        """
        Make sure every stochastic variable has a step method. If not, 
        assign a step method from the registry.
        """

        for s in self.stochastics:
            # If not handled by any step method, make it a new step method using the registry
            if len(self.step_method_dict[s])==0:
                new_method = assign_method(s)
                setattr(new_method, '_model', self)
                self.step_method_dict[s].append(new_method)
                if self.verbose > 1:
                    print 'Assigning step method %s to stochastic %s' % (new_method.__class__.__name__, s.__name__)
                
        self.step_methods = set()
        for s in self.stochastics:
            self.step_methods |= set(self.step_method_dict[s])

    def sample(self, iter, burn=0, thin=1, tune_interval=1000, verbose=0):
        """
        sample(iter, burn, thin, tune_interval)

        Initialize traces, run sampling loop, clean up afterward. Calls _loop.
        """
        
        self._assign_step_methods()

        self._iter = int(iter)
        self._burn = int(burn)
        self._thin = int(thin)
        self._tune_interval = int(tune_interval)

        length = (iter-burn)/thin
        self.max_trace_length = length

        # Flags for tuning
        self._tuning = True
        self._tuned_count = 0

        Sampler.sample(self, iter, length, verbose)
    
    def _loop(self):
        # Set status flag
        self.status='running'


        try:
            while self._current_iter < self._iter and not self.status == 'halt':
                if self.status == 'paused':
                    break

                i = self._current_iter

                if i == self._burn and self.verbose>0: 
                    print 'Burn-in interval complete'

                # Tune at interval
                if i and not (i % self._tune_interval) and self._tuning:
                    self.tune()

                # Tell all the step methods to take a step
                for step_method in self.step_methods:
                    if self.verbose > 2:
                        print 'Step method %s stepping.' % step_method._id
                    # Step the step method
                    step_method.step()

                if not i % self._thin and i >= self._burn:
                    self.tally()

                if not i % 10000 and self.verbose > 0:
                    print 'Iteration ', i, ' of ', self._iter

                self._current_iter += 1

        except KeyboardInterrupt:
            self.status='halt'

        if self.status == 'halt':
            self.halt()
    
    def tune(self):
        """
        Tell all step methods to tune themselves.
        """

        # Only tune during burn-in
        if self._current_iter > self._burn:
            self._tuning = False
            return

        if self.verbose > 0:
            print '\tTuning at iteration', self._current_iter

        # Initialize counter for number of tuning stochastics
        tuning_count = 0

        for step_method in self.step_methods:
            # Tune step methods
            tuning_count += step_method.tune(verbose=self.verbose)
            if self.verbose > 1:
                print 'Tuning step method %s, returned %i' %(step_method._id, tuning_count)

        if not tuning_count:
            # If no step methods needed tuning, increment count
            self._tuned_count += 1
        else:
            # Otherwise re-initialize count
            self._tuned_count = 0

        # 5 consecutive clean intervals removed tuning
        if self._tuned_count == 5:
            if self.verbose > 0: print 'Finished tuning'
            self._tuning = False    


    def get_state(self):
        """
        Return the sampler and step methods current state in order to
        restart sampling at a later time.
        """
        
        self.step_methods = set()
        for s in self.stochastics:
            self.step_methods |= set(self.step_method_dict[s])
        
        state = Sampler.get_state(self)
        state['step_methods'] = {}
        
        # The state of each StepMethod.
        for sm in self.step_methods:
            state['step_methods'][sm._id] = sm.current_state().copy()

        return state
    
    def restore_state(self):
        
        state = Sampler.restore_state(self)
        
        self.step_methods = set()
        for s in self.stochastics:
            self.step_methods |= set(self.step_method_dict[s])        
        
        # Restore stepping methods state
        sm_state = state.get('step_methods', {})
        for sm in self.step_methods:
            sm.__dict__.update(sm_state.get(sm._id, {}))
            
        return state
        
    def goodness(self, iterations, loss='squared', plot=True, color='b', filename='gof'):
        """
        Calculates Goodness-Of-Fit according to Brooks et al. 1998
        
        :Arguments:
            - iterations : integer
                Number of samples to draw from the model for GOF evaluation.
            - loss (optional) : string
                Loss function; valid entries include 'squared', 'absolute' and
                'chi-square'.
            - plot (optional) : booleam
                Flag for printing GOF plots.
            - color (optional) : string
                Color of plot; see matplotlib docs for valid entries (usually
                the first letter of the desired color).
            - filename (optional) : string
                File name for output statistics.
        """
        
        if self.verbose > 0:
            print
            print "Goodness-of-fit"
            print '='*50
            print 'Generating %s goodness-of-fit simulations' % iterations
        
        
        # Specify loss function
        if loss=='squared':
            self.loss = squared_loss
        elif loss=='absolute':
            self.loss = absolute_loss
        elif loss=='chi-square':
            self.loss = chi_square_loss
        else:
            print 'Invalid loss function specified.'
            return
            
        # Open file for GOF output
        outfile = open(filename + '.csv', 'w')
        outfile.write('Goodness of Fit based on %s iterations\n' % iterations)
        
        # Empty list of GOF plot points
        D_points = []
        
        # Set GOF flag
        self._gof = True
        
        # List of names for conditional likelihoods
        self._like_names = []
        
        # Local variable for the same
        like_names = None
        
        # Generate specified number of points
        for i in range(iterations):
            
            valid_gof_points = False
            
            # Sometimes the likelihood bombs out and doesnt produce
            # GOF points
            while not valid_gof_points:
                
                # Initializealize list of GOF error loss values
                self._gof_loss = []
                
                # Loop over stochastics
                for name in self.stochastics:
                    
                    # Look up stoch
                    s = self.stochastics[name]
                    
                    # Retrieve copy of trace
                    trace = s.get_trace(burn=burn, thin=thin, chain=chain, composite=composite)
                    
                    # Sample value from trace
                    sample = trace[random_integers(len(trace)) - 1]
                    
                    # Set current value to sampled value
                    s.set_value(sample)
                
                # Run calculate likelihood with sampled stochastics
                try:
                    self()
                except (LikelihoodError, OverflowError, ZeroDivisionError):
                    # Posterior dies for some reason
                    pass
                
                try:
                    like_names = self._like_names
                    del(self._like_names)
                except AttributeError:
                    pass
                
                # Conform that length of GOF points is valid
                if len(self._gof_loss) == len(like_names):
                    valid_gof_points = True
            
            # Append points to list
            D_points.append(self._gof_loss)
        
        # Transpose and plot GOF points
        
        D_points = t([[y for y in x if shape(y)] for x in D_points], (1,2,0))
        
        # Keep track of number of simulation deviances that are
        # larger than the corresponding observed deviance
        sim_greater_obs = 0
        n = 0
        
        # Dictionary to hold GOF statistics
        stats = {}
        
        # Dictionary to hold GOF plot data
        plots = {}
        
        # Loop over the sets of points for plotting
        for name,points in zip(like_names,D_points):
            
            if plots.has_key(name):
                # Append points, if already exists
                plots[name] = concatenate((plots[name], points), 1)
            
            else:
                plots[name] = points
            
            count = sum(s>o for o,s in t(points))
            
            try:
                stats[name] += array([count,iterations])
            except KeyError:
                stats[name] = array([1.*count,iterations])
            
            sim_greater_obs += count
            n += iterations
        
        # Generate plots
        if plot:
            for name in plots:
                self.plotter.gof_plot(plots[name], name, color=color)
        
        # Report p(D(sim)>D(obs))
        for name in stats:
            num,denom = stats[name]
            print 'p( D(sim) > D(obs) ) for %s = %s' % (name,num/denom)
            outfile.write('%s,%f\n' % (name,num/denom))
        
        p = 1.*sim_greater_obs/n
        print 'Overall p( D(sim) > D(obs) ) =', p
        print
        outfile.write('overall,%f\n' % p)
        
        stats['overall'] = array([1.*sim_greater_obs,n])
        
        # Unset flag
        self._gof = False
        
        # Close output file
        outfile.close()
        
        return stats
    
        
