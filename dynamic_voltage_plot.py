import matplotlib.pyplot as plt

import const


def voltage_plot(G):
    node = 0
    attrs = G.nodes[node]
    dt_list = G.graph['dt_list']

    x = [0.0]
    for dt in dt_list:
        x.append(x[-1] + dt)

    y_V = attrs['voltage']
    has_conductances = 'conductance_A' in attrs

    plt.plot(x, y_V, label='voltage')
    if has_conductances:
        plt.plot(x, attrs['conductance_A'], label='g_A')
        plt.plot(x, attrs['conductance_E'], label='g_E')
        plt.plot(x, attrs['conductance_I'], label='g_I')

    plt.title('epsilon = %.2e' % const.epsilon, fontsize=14)
    plt.xlabel('Time (s)', fontsize=14)
    plt.ylabel('Voltage (V) / Conductance (S)', fontsize=14)
    plt.legend()
    plt.tight_layout()
    plt.savefig('figures/%dN%dK%.2eP.png' % (const.N, const.K, const.P))
    plt.show()
    plt.clf()

    plt.plot(range(len(dt_list)), x[:-1], linestyle='-.', marker=',')
    plt.xlabel('Time Index', fontsize=14)
    plt.ylabel('Time (s)', fontsize=14)
    plt.show()
