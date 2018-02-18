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
    y2 = G.node[nnumber2]['voltage']

    xmin = min(x)
    xmax = max(x)
    xwidth = xmax - xmin

    ymin = min([min(y1),min(y2)])
    ymax = max([max(y1),max(y2)])
    ywidth = ymax - ymin

    plt.plot(x,y1,linestyle='-.',marker = '.')
    plt.plot(x,y2,linestyle='--',marker = ',')
    #plt.text(xmin,ymin,'Time Increment (dt) = %.2e' % const.dt,fontsize=14)
    plt.title('epsilon = %.2e' % (const.epsilon),fontsize=14)

    plt.xlabel('Time (s)',fontsize=14)
    plt.ylabel('Voltage (V)',fontsize=14)

    plt.legend(['Neuron %d'%(nnumber1),'Neuron %d'%(nnumber2)])
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
