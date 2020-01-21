#   Copyright 2020 The PyMC Developers
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

"""Text file trace backend

Store sampling values as CSV files.

File format
-----------

Sampling values for each chain are saved in a separate file (under a
directory specified by the `name` argument).  The rows correspond to
sampling iterations.  The column names consist of variable names and
index labels.  For example, the heading

  x,y__0_0,y__0_1,y__1_0,y__1_1,y__2_0,y__2_1

represents two variables, x and y, where x is a scalar and y has a
shape of (3, 2).
"""
from glob import glob
import os
import re
import pandas as pd

from ..backends import base, ndarray
from . import tracetab as ttab
from ..theanof import floatX
from ..model import modelcontext


class Text(base.BaseTrace):
    """Text trace object

    Parameters
    ----------
    name : str
        Name of directory to store text files
    model : Model
        If None, the model is taken from the `with` context.
    vars : list of variables
        Sampling values will be stored for these variables. If None,
        `model.unobserved_RVs` is used.
    test_point : dict
        use different test point that might be with changed variables shapes
    """

    def __init__(self, name, model=None, vars=None, test_point=None):
        if not os.path.exists(name):
            os.mkdir(name)
        super().__init__(name, model, vars, test_point)

        self.flat_names = {v: ttab.create_flat_names(v, shape)
                           for v, shape in self.var_shapes.items()}

        self.filename = None
        self._fh = None
        self.df = None

    # Sampling methods

    def setup(self, draws, chain):
        """Perform chain-specific setup.

        Parameters
        ----------
        draws : int
            Expected number of draws
        chain : int
            Chain number
        """
        if self._fh is not None:
            self._fh.close()

        self.chain = chain
        self.filename = os.path.join(self.name, 'chain-{}.csv'.format(chain))

        cnames = [fv for v in self.varnames for fv in self.flat_names[v]]

        if os.path.exists(self.filename):
            with open(self.filename) as fh:
                prev_cnames = next(fh).strip().split(',')
            if prev_cnames != cnames:
                raise base.BackendError(
                    "Previous file '{}' has different variables names "
                    "than current model.".format(self.filename))
            self._fh = open(self.filename, 'a')
        else:
            self._fh = open(self.filename, 'w')
            self._fh.write(','.join(cnames) + '\n')

    def record(self, point):
        """Record results of a sampling iteration.

        Parameters
        ----------
        point : dict
            Values mapped to variable names
        """
        vals = {}
        for varname, value in zip(self.varnames, self.fn(point)):
            vals[varname] = value.ravel()
        columns = [str(val) for var in self.varnames for val in vals[var]]
        self._fh.write(','.join(columns) + '\n')

    def close(self):
        if self._fh is not None:
            self._fh.close()
            self._fh = None  # Avoid serialization issue.

    # Selection methods

    def _load_df(self):
        if self.df is None:
            self.df = pd.read_csv(self.filename)
            for key, dtype in self.df.dtypes.iteritems():
                if "float" in str(dtype):
                    self.df[key] = floatX(self.df[key])

    def __len__(self):
        if self.filename is None:
            return 0
        self._load_df()
        return self.df.shape[0]

    def get_values(self, varname, burn=0, thin=1):
        """Get values from trace.

        Parameters
        ----------
        varname : str
        burn : int
        thin : int

        Returns
        -------
        A NumPy array
        """
        self._load_df()
        var_df = self.df[self.flat_names[varname]]
        shape = (self.df.shape[0],) + self.var_shapes[varname]
        vals = var_df.values.ravel().reshape(shape)
        return vals[burn::thin]

    def _slice(self, idx):
        if idx.stop is not None:
            raise ValueError('Stop value in slice not supported.')
        return ndarray._slice_as_ndarray(self, idx)

    def point(self, idx):
        """Return dictionary of point values at `idx` for current chain
        with variables names as keys.
        """
        idx = int(idx)
        self._load_df()
        pt = {}
        for varname in self.varnames:
            vals = self.df[self.flat_names[varname]].iloc[idx].values
            pt[varname] = vals.reshape(self.var_shapes[varname])
        return pt


def load(name, model=None):
    """Load Text database.

    Parameters
    ----------
    name : str
        Name of directory with files (one per chain)
    model : Model
        If None, the model is taken from the `with` context.

    Returns
    -------
    A MultiTrace instance
    """
    files = glob(os.path.join(name, 'chain-*.csv'))

    if len(files) == 0:
        raise ValueError('No files present in directory {}'.format(name))

    straces = []
    for f in files:
        chain = int(os.path.splitext(f)[0].rsplit('-', 1)[1])
        model_vars_in_chain = _parse_chain_vars(f, model)
        strace = Text(name, model=model, vars=model_vars_in_chain)
        strace.chain = chain
        strace.filename = f
        straces.append(strace)
    return base.MultiTrace(straces)


def _parse_chain_vars(filepath, model):
    with open(filepath) as f:
        header = f.readline().split("\n", 1)[0]
    shape_pattern = re.compile(r"__\d+_\d+")
    chain_vars = [shape_pattern.split(v)[0] for v in header.split(",")]
    chain_vars = list(set(chain_vars))
    m = modelcontext(model)
    model_vars_in_chain = [v for v in m.unobserved_RVs if v.name in chain_vars]
    return model_vars_in_chain


def dump(name, trace, chains=None):
    """Store values from NDArray trace as CSV files.

    Parameters
    ----------
    name : str
        Name of directory to store CSV files in
    trace : MultiTrace of NDArray traces
        Result of MCMC run with default NDArray backend
    chains : list
        Chains to dump. If None, all chains are dumped.
    """
    if not os.path.exists(name):
        os.mkdir(name)
    if chains is None:
        chains = trace.chains

    for chain in chains:
        filename = os.path.join(name, 'chain-{}.csv'.format(chain))
        df = ttab.trace_to_dataframe(
            trace, chains=chain, include_transformed=True)
        df.to_csv(filename, index=False)
