import pandas
import networkx
import scipy
import logging



class RoadNetWork(object):
    def __init__(self,fname = 'austin.csv'):
        self.df = pandas.read_csv(fname,index_col = 'SEGMENT_ID')

    def createNetwork(self):

