import matplotlib.pyplot as plt
import numpy as np
import const

def voltage_plot(G):

    nnumber1 = 1
    nnumber2 = 5 # Neurons to graph

    timesteps = const.timesteps

    x = np.linspace(0, const.dt * timesteps , timesteps)
    y1 = G.node[nnumber1]['voltage']
    y2 = G.node[nnumber2]['voltage']

    xmin = min(x)
    xmax = max(x)
    xwidth = xmax - xmin

    ymin = min([min(y1),min(y2)])
    ymax = max([max(y1),max(y2)])
    ywidth = ymax - ymin

    plt.plot(x,y1,linestyle='-.')
    plt.plot(x,y2,linestyle='--')
    #plt.text(xmin,ymin,'Time Increment (dt) = %.2e' % const.dt,fontsize=14)
    plt.title('dt = %.2e, epsilon = %.2e' % (const.dt,const.epsilon),fontsize=14)

    plt.xlabel('Time (s)',fontsize=14)
    plt.ylabel('Voltage (V)',fontsize=14)

    plt.legend(['Neuron %d'%(nnumber1),'Neuron %d'%(nnumber2)])
    plt.tight_layout()

    plt.savefig('figures/dt%.2eN%dK%dP%.2e.png'%(const.dt,const.N,const.K,const.P))
    plt.show()

    return
