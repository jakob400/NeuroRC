"""F5: round-trip assertion for logging_hdf5.dump_state.

The HDF5 schema is the proposal-#2 EWS pipeline's input contract; silent
breakage of attrs or array shapes would only surface at analysis time.
This test simulates, dumps, reloads, and asserts shapes/attrs/values.
"""

import os
import tempfile

import h5py
import numpy as np
import pytest

import const
from simulate import simulate


def _run_and_dump(model, tmp_path, **overrides):
    log_dir = str(tmp_path)
    G, state = simulate(model, N=4, K=2, P=0.2, tMax=200, seed=0,
                        log_dir=log_dir, **overrides)
    files = [f for f in os.listdir(log_dir) if f.endswith('.h5')]
    assert len(files) == 1, files
    return os.path.join(log_dir, files[0]), state


def test_hdf5_lif_round_trip(tmp_path):
    path, state = _run_and_dump('LIF', tmp_path)
    with h5py.File(path, 'r') as f:
        assert f.attrs['model'] == 'LIF'
        assert int(f.attrs['seed']) == 0
        assert int(f.attrs['N']) == 4
        assert int(f.attrs['tMax']) == 200
        V_disk = f['V'][()]
        dt_disk = f['dt_list'][()]
        last_spike_disk = f['last_spike_time'][()]
        # LIF dump skips conductance datasets.
        for key in ('g_A', 'g_E', 'g_I'):
            assert key not in f, key

    V_mem = np.asarray(state.history['V'])
    assert V_disk.shape == V_mem.shape == (201, 4)
    np.testing.assert_array_equal(V_disk, V_mem)
    np.testing.assert_array_equal(dt_disk, np.asarray(state.dt_list))
    np.testing.assert_array_equal(last_spike_disk, state.last_spike_time)


def test_hdf5_str_round_trip(tmp_path):
    path, state = _run_and_dump('STR', tmp_path)
    with h5py.File(path, 'r') as f:
        assert f.attrs['model'] == 'STR'
        V_disk = f['V'][()]
        for key in ('g_A', 'g_E', 'g_I'):
            data = f[key][()]
            mem = np.asarray(state.history[key])
            assert data.shape == mem.shape == (201, 4), (key, data.shape)
            np.testing.assert_array_equal(data, mem)
        assert f.attrs['drive_mode'] == const.drive_mode
        np.testing.assert_allclose(float(f.attrs['poisson_rate']),
                                   const.poisson_rate)
    np.testing.assert_array_equal(V_disk, np.asarray(state.history['V']))


def test_hdf5_same_config_overwrites(tmp_path):
    """Two runs with identical config land in the same filename (sha1 keyed)."""
    _run_and_dump('LIF', tmp_path)
    _run_and_dump('LIF', tmp_path)
    files = [f for f in os.listdir(str(tmp_path)) if f.endswith('.h5')]
    assert len(files) == 1, files
