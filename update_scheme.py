def update_scheme(g):

    N = len(g.nodes) # number of nodes
    timesteps = 100 #timesteps

    for i in range(N):
        for k in range(timesteps): #set each node to have certain number of timesteps
            g.node[i][k] = { 'voltage' : 0 } #find better way to do this

    for k in range(timesteps):
        for i in (N):
            num_nn = len(dict(g[i]).keys()) #get number of nearest neighbours from number of keys in dict g[i]
            g.node[i][k+1]['voltage'] = g.node[i][k]['voltage']
            for j in range(num_nn): #iterates over nearest neighbours
                g.node[i][k+1]['voltage'] = g.node[i][k+1]['voltage']+ state_calc(g,j)


def state_calc(g,j):
    #voltage =

def euler_update():
