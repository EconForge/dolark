# -*- coding: utf-8 -*-
# %%
from matplotlib import pyplot as plt

# %%
# Let's import the heterogeneous agents model
from dolark import HModel
aggmodel = HModel('ayiagari.yaml')
aggmodel # TODO: find a reasonable representation of this object

# %% [markdown]
# First we can check whether the one-agent sub-part of it works

# %%
from dolo import time_iteration
discretization_options = {"N": 2}
model = aggmodel.model
mc = model.exogenous.discretize(to='mc', options=[{},discretization_options])
sol0 = time_iteration(model, details=True, dprocess=mc)

# %%
# TEMP:  we need to supply a projection function, which maps aggregate variables
# into the exogenous shocks received by idiosyncratic agents.
# This should be read from the YAML file. For now, we monkey-patch

def projection(self, m: 'n_e', y: "n_y", p: "n_p"):

    from numpy import exp
    z = m[0]
    K = y[0]
    A = [0]
    alpha = p[1]
    delta = p[2]
    N = 1
    r = alpha*exp(z)*(N/K)**(1-alpha) - delta
    w = (1-alpha)*exp(z)*(K/N)**(alpha)
    return {'r': r, "w": w}

import types
aggmodel.projection = types.MethodType(projection, aggmodel)

# %%
# We can now solve for the aggregate equilibrium

eq = aggmodel.find_steady_state()
eq

# %%
# lot's look at the aggregate equilibrium
for i in range(eq.μ.shape[0]):
    s = eq.dr.endo_grid.nodes() # grid for states (temporary)
    plt.plot(s, eq.μ[i,:]*(eq.μ[i,:].sum()), label=f"y={eq.dr.exo_grid.node(i)[2]: .2f}")
plt.plot(s, eq.μ.sum(axis=0), label='total', color='black')
plt.grid()
plt.legend(loc='upper right')
plt.title("Wealth Distribution by Income")

# %%
# alternative way to plot equilibrium

import altair as alt
df = eq.as_df()
spec = alt.Chart(df).mark_line().encode(
    x = 'a',
    y = 'μ',
    color = 'i_m:N'
)
spec

# %%
# alternative way to plot equilibrium (with some interactivity)
# TODO: function to generate it automatically.

import altair as alt
single = alt.selection_single(on='mouseover', nearest=True)
df = eq.as_df()
ch = alt.Chart(df)
spec = ch.properties(title='Distribution', height=100).mark_line().encode(
    x = 'a',
    y = 'μ',
    color = alt.condition(single, 'i_m:N', alt.value('lightgray'))
).add_selection(
        single
) + ch.mark_line(color='black').encode(
    x = 'a',
    y = 'sum(μ)'
) & ch.properties(title='Decision Rule', height=100).mark_line().encode(
    x = 'a',
    y = 'i',
    color = alt.condition(single, 'i_m:N', alt.value('lightgray'))
).add_selection(
        single
)

# %%

# Resulting object can be saved to a file. (try to open this file in jupyterlab)
open('distrib.json','tw').write(spec.to_json())

# %%

# %%
import xarray

# %%
# now we compute the perturbation
peq = aggmodel.perturb(eq)


# %%
# and we simulate given initial value of aggregate shock
sim = peq.response([0.1])

# %%
plt.subplot(121)
for t, (m,μ,x,y) in enumerate(sim):
    plt.plot(μ.sum(axis=0), color='red', alpha=0.01)
plt.xlabel('a')
plt.ylabel('density')
plt.grid()
plt.subplot(122)
plt.plot( [e[3][0] for e in sim])
plt.xlabel("t")
plt.ylabel("k")
plt.grid()
plt.tight_layout()
