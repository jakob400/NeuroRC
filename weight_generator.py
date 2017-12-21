import random
import networkx as nx

small = 0
large = 1
decimals = 5

def getWeight(): #returns random number between n and N, to 'decimals' decimals
    return round(random.uniform(small,large),decimals)

def weight_generator(G): #adds random weights to graph g
    for i,j,k in G.edges(data = True):
        G[i][j]['weight'] = getWeight()
    return G
