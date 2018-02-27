import matplotlib.pyplot as plt
import numpy as np
import const
from pprint import pprint

def voltage_plot(G):

    nnumber1 = 0
    nnumber2 = 1#50 # Neurons to graph

    #timesteps = const.timesteps

    x = []
    x.append(0) # first element
    for n in range(len(const.dt_list)):
        x.append(x[-1] + const.dt_list[n])

    #x = const.dt_list#np.linspace(0, const.dt * timesteps , timesteps)
    y1 = G.node[nnumber1]['voltage']
    #y2 = G.node[nnumber2]['voltage']
    y_A = G.node[nnumber1]['conductance_A']
    y_E = G.node[nnumber1]['conductance_E']
    y_I = G.node[nnumber1]['conductance_I']

    xmin = min(x)
    xmax = max(x)
    xwidth = xmax - xmin

    ymin = min([min(y1),min(y_A),min(y_E),min(y_I)])
    ymax = max([max(y1),max(y_A),max(y_E),max(y_I)])
    ywidth = ymax - ymin

    #plt.plot(x,y1)
    plt.plot(x,y_A)
    plt.plot(x,y_E)
    plt.plot(x,y_I)

    #plt.text(xmin,ymin,'Time Increment (dt) = %.2e' % const.dt,fontsize=14)
    plt.title('epsilon = %.2e' % (const.epsilon),fontsize=14)

    plt.xlabel('Time (s)',fontsize=14)
    plt.ylabel('Voltage (V)',fontsize=14)

    plt.legend(['voltage','A','E','I'])
    #plt.legend(['Neuron %d'%(nnumber1),'Neuron %d'%(nnumber2)])
    plt.tight_layout()

    plt.savefig('figures/%dN%dK%.2eP.png'%(const.N,const.K,const.P))
    plt.show()
    plt.clf()


    #t = np.linspace(range(len(const.dt_list))) np.linspace
    t = range(len(const.dt_list))
    y = const.dt_list[:-1]
    x = x[:-1]

    plt.plot(t,x,linestyle = '-.',marker = ',')
    plt.xlabel('Time Index',fontsize=14)
    plt.ylabel('Time',fontsize=14)

    plt.show()

    return
