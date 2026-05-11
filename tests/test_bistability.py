"""B1: Slow-K (Kir2) plumbing test.

The full bimodal V distribution test belongs after B2 (OU drive lands), since
the present Poisson drive at g_E_ss = 20 nS is too strong for any reasonable
slow K to hold the down state. What B1 alone must do is wire g_KIR through
the integrator correctly:

  - State carries a g_KIR array; LIF does not (None).
  - The slow K activation rectifies with voltage: sigma_KIR(-90 mV) ~ 1
    and sigma_KIR(0 mV) ~ 0.
  - In an isolated neuron held below V_KIR_half via large hyperpolarizing
    drive, g_KIR climbs toward conductance_KIR_max.
  - In an isolated neuron driven above V_KIR_half, g_KIR rectifies (drops)
    toward zero on its slow time constant.
  - History records g_KIR alongside g_A, g_E, g_I for STR.
"""

import numpy as np

import const
import math_functions as fn
from state import build_state
from simulate import simulate


def test_sigma_KIR_rectifies():
    """sigma_KIR is high at hyperpolarized V, low at depolarized V."""
    V = np.array([-90e-3, -60e-3, -30e-3])
    s = fn.sigma_KIR_vec(V)
    assert s[0] > 0.95, 'sigma_KIR at -90 mV should be ~1, got %s' % s[0]
    assert 0.4 < s[1] < 0.6, 'sigma_KIR at -60 mV (half) should be ~0.5, got %s' % s[1]
    assert s[2] < 0.05, 'sigma_KIR at -30 mV should be ~0, got %s' % s[2]


def test_g_KIR_in_state_for_STR_only():
    """STR state carries a g_KIR ndarray; LIF state does not."""
    import networkx as nx
    G_str = nx.DiGraph()
    G_str.add_node(0)
    s_str = build_state(G_str, 'STR')
    assert s_str.g_KIR is not None
    assert s_str.g_KIR.shape == (1,)
    assert 'g_KIR' in s_str.history

    G_lif = nx.DiGraph()
    G_lif.add_node(0)
    s_lif = build_state(G_lif, 'LIF')
    assert s_lif.g_KIR is None
    assert 'g_KIR' not in s_lif.history


def test_g_KIR_records_with_history():
    """STR run produces a g_KIR history array of the right shape."""
    G, s = simulate('STR', N=2, K=1, P=1e-5, tMax=100, seed=0,
                    fixed_dt_mode=True)
    g_KIR = np.asarray(s.history['g_KIR'])
    assert g_KIR.shape == (101, 2)
    assert np.all(np.isfinite(g_KIR))
    # g_KIR must stay nonnegative (it's a conductance) within numerical
    # tolerance of the exp-Euler scheme.
    assert g_KIR.min() > -1e-15
