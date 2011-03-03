import subprocess
from IPython.kernel import client
import os, time
from pymc import Sampler
import numpy as np
"""
It seems to work, but the real challenge is to get the results back.
One solution may be to create a parallel database backend. The backend
is instantiated in Parallel, communicates with each process, and serves
as a middle man with the real backend. Each time the tally method is called,
it calls the real backend tally with the correct chain. This requires setting
an optional argument for tally to each backend.
def tally(self, index, chain=-1):

The sample method is Parallel must initialize the chains
"""


class Parallel(Sampler):
    """
    Parallel manages multiple MCMC loops. It is initialized with:

    A = Parallel(prob_def, dbase=None, chains=1, proc=1)

    Arguments

        prob_def: class, module or dictionary containing nodes and
        StepMethods)

        dbase: Database backend used to tally the samples.
        Implemented backends: None, hdf5.

        chains: Number of processes (generally the number of available CPUs.)

    Externally-accessible attributes:

        dtrms:          All extant Deterministics.

        stochs:         All extant Stochastics with observed = False.

        data:               All extant Stochastics with observed = True.

        nodes:               All extant Stochastics and Deterministics.

        step_methods:   All extant StepMethods.

    Externally-accessible methods:

        sample(iter,burn,thin): At each MCMC iteration, calls each step_method's step() method.
                                Tallies Stochastics and Deterministics as appropriate.

        trace(stoch, burn, thin, slice): Return the trace of stoch,
        sliced according to slice or burn and thin arguments.

        remember(trace_index): Return the entire model to the tallied state indexed by trace_index.

        DAG: Draw the model as a directed acyclic graph.

        All the plotting functions can probably go on the base namespace and take Stochastics as
        arguments.

    See also StepMethod, OneAtATimeMetropolis, Node, Stochastic, Deterministic, and weight.
    """
    def __init__(self, input, db='ram', chains=2):
        try:
            mec = client.MultiEngineClient()
        except:
            p = subprocess.Popen('ipcluster -n %d'%proc, shell=True)
            p.wait()
            mec = client.MultiEngineClient()

        # Check everything is alright.
        nproc = len(mec.get_ids())
        assert chains <= nproc


        Sampler.__init__(self, input, db=db)

        # Import the individual models in each process
        #mec.pushModule(input)

        proc = range(chains)

        try:
            mec.execute('import %s as input'%input.__name__, proc)
        except:
            mec.execute( 'import site' , proc)
            mec.execute( 'site.addsitedir( ' + `os.getcwd()` + ' )' , proc)
            mec.execute( 'import %s as input; reload(input)'%input.__name__, proc)

        # Instantiate Sampler instances in each process
        mec.execute('from pymc import MCMC', proc)
        #mec.execute('from pymc.database.parallel import Database')
        #for i in range(nproc):
        #    mec.execute(i, 'db = Database(%d)'%i)
        mec.execute("S = MCMC(input, db='txt')", proc)

        self.mec = mec
        self.proc = proc

    def sample(self, iter, burn=0, thin=1, tune_interval=100):
        proc = self.proc
        # Set the random initial seeds
        self.mec.execute('S.seed()', proc)
        self.mec.execute('nugget = {}')
        length = int(np.ceil((1.0*iter-burn)/thin))

        for i in proc:
            self.db._initialize(length=length)

        # Run the chains on each process
        self.result = self.mec.execute('S.sample(%(iter)i, %(burn)i, %(thin)i, %(tune_interval)i)'%vars(), proc, block=True)

        self.mec.execute("print 'Sampling terminated successfully on process %d.'%id", proc)

        # Launch a subprocess that will tally the traces of each sampler.
        #self.tally()

    def fetch_samples(self):
        """Read in the traces dumped by the samplers."""
        mec = self.mec
        data = {}
        for obj in self._variables_to_tally:
            name = obj.__name__
            print 'getting ', name
            mec.execute('x = S.%s.trace(chain=-1)'%name, self.proc)
            data[name] = mec.pull('x', self.proc)

        for obj in self._variables_to_tally:
            name = obj.__name__
            traces = data[name]
            for chain, trace in enumerate(traces):
                for index, v in enumerate(trace):
                    obj.value = v
                    obj.trace.tally(index, chain)




if __name__ == '__main__':
    from pymc.examples import disaster_model
    P = Parallel(disaster_model, 'ram')
    P.sample(1000,500,1)
    #P.mec.killAll(controller=True)
