import matplotlib.pyplot as plt
import numpy as np
import const

def voltage_plot(G):

    timesteps = len(G.node[1]['voltage'])

    x = np.linspace(0, const.dt * timesteps , timesteps)
    y1 = G.node[1]['voltage']
    y2 = G.node[5]['voltage']

    xmin = min(x)
    xmax = max(x)
    xwidth = xmax - xmin

    ymin = min([min(y1),min(y2)])
    ymax = max([max(y1),max(y2)])
    ywidth = ymax - ymin

    plt.plot(x,y1,linestyle='-.')
    plt.plot(x,y2,linestyle='--')
    plt.text(xmin,ymax + (ywidth/8),'Time Increment (dt) = %.1e' % const.dt,fontsize=14)

    plt.xlabel('Time',fontsize=14)
    plt.ylabel('Voltage (V)',fontsize=14)

    plt.savefig('figures/dt%.1eN%dK%dP%d.png'%(const.dt,const.N,const.K,const.P))
    plt.show()

    """
    fig, ax1 = plt.subplots()


    ax1.plot(x,y1,linestyle='-.')
    ax1.set_ylabel('Voltage (V)')
    ax1.set_xticks(np.arange(min(x)),max(x)+1)
    plt.setp(ax1.get_xticklabels(),rotation=70)

    ax2 = ax1.twinx()
    ax2.plot(x,y2,linestyle='--')


    ax1.text(0.2, 0.9,'matplotlib',fontsize=14, horizontalalignment='center', verticalalignment='center', transform = ax1.transAxes)

    fig.legend(['Neuron 1 Voltage'],['Neuron 2 Voltage'])
    plt.show()
    """


    """
    fig, ax1 = plt.subplots()
    ax1.plot(x,y1)
    ax1.set_ylabel('Voltage (V)')
    ax1.set_xticks(np.arange(min(x)),max(x)+1)
    plt.setp(ax1.get_xticklabels(),rotation=70)
    ax1.legend(['Time Increment (dt) = %.1e' % const.dt])
    ax1.legend(markerscale=0)

    plt.show()
    """





    """
    timesteps = len(G.node[1]['voltage'])

    fig = plt.figure()
    x = np.linspace(0, const.dt * timesteps , timesteps)
    y1 = G.node[1]['voltage']
    y2 = G.node[2]['voltage']
    ax = fig.add_axes([0,0,1,1])

    plt.plot(x,y1,linestyle='-.')
    plt.plot(x,y2,linestyle='--')


    x0, xmax = plt.xlim()
    y0, ymax = plt.ylim()
    data_width = xmax - x0
    data_height = ymax - y0
    plt.text(x0 + data_width * 0.5, y0 + data_height * 0.5,'dt = %.3e' % const.dt)



    plt.savefig('figures/dt%.1eN%dK%dP%d.png'%(const.dt,const.N,const.K,const.P))
    plt.show()
    """
    return
