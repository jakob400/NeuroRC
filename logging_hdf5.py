"""HDF5 dump of a finished simulation State.

One file per run, named by sha1 of (model, N, K, P, tMax, seed,
fixed_dt_mode, dt_fixed) so reruns of the same configuration overwrite
each other and divergent runs co-exist.
"""

import hashlib
import os

import h5py
import numpy as np

import const


def _config_hash(model, seed) -> str:
    parts = [
        model, const.N, const.K, const.P, const.tMax, seed,
        const.fixed_dt_mode, const.dt_fixed, const.drive_mode,
        const.poisson_rate, const.poisson_delta_g_E,
    ]
    return hashlib.sha1(repr(parts).encode()).hexdigest()[:12]


def dump_state(state, model: str, seed: int, log_dir: str = 'logs') -> str:
    os.makedirs(log_dir, exist_ok=True)
    cfg = _config_hash(model, seed)
    path = os.path.join(log_dir, '%s_%s.h5' % (model, cfg))

    with h5py.File(path, 'w') as f:
        f.attrs['model'] = model
        f.attrs['seed'] = seed
        f.attrs['N'] = state.N
        f.attrs['K'] = const.K
        f.attrs['P'] = const.P
        f.attrs['tMax'] = const.tMax
        f.attrs['fixed_dt_mode'] = const.fixed_dt_mode
        f.attrs['dt_fixed'] = const.dt_fixed
        f.attrs['drive_mode'] = const.drive_mode
        f.attrs['poisson_rate'] = const.poisson_rate
        f.attrs['poisson_delta_g_E'] = const.poisson_delta_g_E
        f.attrs['current_time'] = state.current_time

        f.create_dataset('dt_list', data=np.asarray(state.dt_list))
        f.create_dataset('V', data=np.asarray(state.history['V']))
        if model == 'STR':
            for key in ('g_A', 'g_E', 'g_I', 'g_KIR'):
                if key in state.history:
                    f.create_dataset(key, data=np.asarray(state.history[key]))
        if 'M' in state.history:
            f.create_dataset('M', data=np.asarray(state.history['M']))
        f.create_dataset('last_spike_time', data=state.last_spike_time)

    return path
