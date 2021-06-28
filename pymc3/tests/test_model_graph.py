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
import aesara
import numpy as np
import pytest

from aesara.compile.sharedvalue import SharedVariable

import pymc3 as pm

from pymc3.model_graph import ModelGraph, model_to_graphviz
from pymc3.tests.helpers import SeededTest


def radon_model():
    """Similar in shape to the Radon model"""
    n_homes = 919
    counties = 85
    uranium = np.random.normal(-0.1, 0.4, size=n_homes)
    xbar = np.random.normal(1, 0.1, size=n_homes)
    floor_measure = np.random.randint(0, 2, size=n_homes)

    d, r = divmod(919, 85)
    county = np.hstack((np.tile(np.arange(counties, dtype=int), d), np.arange(r)))
    with pm.Model() as model:
        sigma_a = pm.HalfCauchy("sigma_a", 5)
        gamma = pm.Normal("gamma", mu=0.0, sigma=1e5, shape=3)
        mu_a = pm.Deterministic("mu_a", gamma[0] + gamma[1] * uranium + gamma[2] * xbar)
        eps_a = pm.Normal("eps_a", mu=0, sigma=sigma_a, shape=counties)
        a = pm.Deterministic("a", mu_a + eps_a[county])
        b = pm.Normal("b", mu=0.0, sigma=1e15)
        sigma_y = pm.Uniform("sigma_y", lower=0, upper=100)

        # Anonymous SharedVariables don't show up
        floor_measure = aesara.shared(floor_measure)
        floor_measure_offset = pm.Data("floor_measure_offset", 1)
        y_hat = a + b * floor_measure + floor_measure_offset
        log_radon = pm.Data("log_radon", np.random.normal(1, 1, size=n_homes))
        y_like = pm.Normal("y_like", mu=y_hat, sigma=sigma_y, observed=log_radon)

    compute_graph = {
        # variable_name : set of named parents in the graph
        "sigma_a": set(),
        "gamma": set(),
        "mu_a": {"gamma"},
        "eps_a": {"sigma_a"},
        "a": {"mu_a", "eps_a"},
        "b": set(),
        "sigma_y": set(),
        "y_like": {"a", "b", "sigma_y", "floor_measure_offset"},
        "floor_measure_offset": set(),
        # observed data don't have parents in the model graph, but are shown as decendants
        # of the model variables that the observations belong to:
        "log_radon": {"y_like"},
    }
    plates = {
        (): {"b", "sigma_a", "sigma_y", "floor_measure_offset"},
        (3,): {"gamma"},
        (85,): {"eps_a"},
        (919,): {"a", "mu_a", "y_like", "log_radon"},
    }
    return model, compute_graph, plates


class BaseModelGraphTest(SeededTest):
    model_func = None

    @classmethod
    def setup_class(cls):
        cls.model, cls.compute_graph, cls.plates = cls.model_func()
        cls.model_graph = ModelGraph(cls.model)

    def test_inputs(self):
        for child, parents_in_plot in self.compute_graph.items():
            var = self.model[child]
            parents_in_graph = self.model_graph.get_parents(var)
            if isinstance(var, SharedVariable):
                # observed data also doesn't have parents in the compute graph!
                # But for the visualization we like them to become decendants of the
                # RVs that these observations belong to.
                assert not parents_in_graph
            else:
                assert parents_in_plot == parents_in_graph

    def test_compute_graph(self):
        expected = self.compute_graph
        actual = self.model_graph.make_compute_graph()
        assert actual == expected

    def test_plates(self):
        assert self.plates == self.model_graph.get_plates()

    def test_graphviz(self):
        # just make sure everything runs without error

        g = self.model_graph.make_graph()
        for key in self.compute_graph:
            assert key in g.source
        g = model_to_graphviz(self.model)
        for key in self.compute_graph:
            assert key in g.source


class TestRadonModel(BaseModelGraphTest):
    model_func = radon_model

    def test_checks_formatting(self):
        with pytest.warns(None):
            model_to_graphviz(self.model, formatting="plain")
        with pytest.raises(ValueError, match="Unsupported formatting"):
            model_to_graphviz(self.model, formatting="latex")
        with pytest.warns(UserWarning, match="currently not supported"):
            model_to_graphviz(self.model, formatting="plain_with_params")
