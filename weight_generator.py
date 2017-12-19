import random
import networkx as nx

small = 0
large = 1
decimals = 5

def getWeight(): #returns random number between n and N, to 'decimals' decimals
    return round(random.uniform(small,large),decimals)

def weight_generator(g): #adds random weights to graph g
    for i,j,k in g.edges(data = True):
        g[i][j]['weight'] = getWeight()
        #print(g[i][j]['weight'])
    return g