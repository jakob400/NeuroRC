import os

import const
from simulate import simulate
from dynamic_voltage_plot import voltage_plot


def main():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')
    print(' =========================================== ')
    print('|-|   NeuroRC: Version 2.3.1              |-|')
    print('|-|   Author: J Weirathmueller            |-|')
    print('|-|   Last Updated: February 26th, 2018   |-|')
    print(' =========================================== ')

    while True:
        response = input('Which model would you like to use? (STR/LIF)\n').strip()
        if response in ('STR', 'LIF'):
            model = response
            break
        print('Invalid input; Please try again.\n')

    G = simulate(model, tMax=const.tMax)

    time_taken = sum(G.graph['dt_list'])
    print('Time calculated over = ', time_taken)
    print('Time steps taken     = ', len(G.nodes[0]['voltage']), '\n')
    print('Graph: %s, nodes=%d, edges=%d\n' % (G.name, G.number_of_nodes(), G.number_of_edges()))

    voltage_plot(G)


if __name__ == '__main__':
    main()
