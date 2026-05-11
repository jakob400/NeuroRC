import os

import matplotlib.pyplot as plt
import numpy as np

import const


def voltage_plot(state, node=0):
    dt_list = state.dt_list
    x = np.concatenate(([0.0], np.cumsum(dt_list)))

    V_hist = np.array(state.history['V'])  # (n_steps, N)
    plt.plot(x, V_hist[:, node], label='V')
    if state.model == 'STR':
        plt.plot(x, np.array(state.history['g_A'])[:, node], label='g_A')
        plt.plot(x, np.array(state.history['g_E'])[:, node], label='g_E')
        plt.plot(x, np.array(state.history['g_I'])[:, node], label='g_I')

    plt.title('epsilon = %.2e' % const.epsilon, fontsize=14)
    plt.xlabel('Time (s)', fontsize=14)
    plt.ylabel('Voltage (V) / Conductance (S)', fontsize=14)
    plt.legend()
    plt.tight_layout()
    os.makedirs('figures', exist_ok=True)
    plt.savefig('figures/%dN%dK%.2eP.png' % (const.N, const.K, const.P))
    plt.show()
    plt.clf()

    plt.plot(range(len(dt_list)), x[:-1], linestyle='-.', marker=',')
    plt.xlabel('Time Index', fontsize=14)
    plt.ylabel('Time (s)', fontsize=14)
    plt.show()
