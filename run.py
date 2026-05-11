import os
import sys
from pathlib import Path

# Make src/ importable when run.py is invoked from the repo root.
_SRC = Path(__file__).resolve().parent / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

import const
from simulate import simulate
from dynamic_voltage_plot import voltage_plot


def main():
    os.system('cls' if os.name == 'nt' else 'clear')
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

    G, state = simulate(model, tMax=const.tMax)

    print('Time calculated over = ', state.current_time)
    print('Time steps taken     = ', len(state.dt_list), '\n')
    print('Graph: %s, nodes=%d, edges=%d\n' % (G.name, G.number_of_nodes(), G.number_of_edges()))

    voltage_plot(state)


if __name__ == '__main__':
    main()
