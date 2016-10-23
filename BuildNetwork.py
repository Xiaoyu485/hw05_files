# -*- coding: utf-8 -*-
"""
Created on Fri Oct 21 14:07:37 2016

@author: Shaw
"""
import pandas
import scipy
import pyomo
import networkx
import geoplotter




class BuildNetwork():
    def __init__(self,fname='austin.csv'):
        self.df = pandas.read_csv(fname)
        self.add = pandas.read_csv('addresses.csv')
        self.plotter = geoplotter.GeoPlotter()
        self.net = networkx.DiGraph(node_styles = dict(default=dict()),edge_styles=dict(default=dict(color='blue',linewidths=0.1)))

    def getstart(self):
        self.start = self.df.kmlgeometry.str.extract('\(([0-9-.]* [0-9-.]*),')
        self.start = self.start.to_frame()
        self.start = pandas.DataFrame(self.start.kmlgeometry.str.split(' ',1).tolist(),columns = ['x','y'])
        self.start.x = self.start.x.astype(float)
        self.start.y = self.start.y.astype(float)
        self.startlist = list(zip(self.start.x,self.start.y)) ##list of start points (x,y)
        
    def getend(self):
        self.end = self.df.kmlgeometry.str.extract(',([0-9-.]* [0-9-.]*)\)')
        self.end = self.end.to_frame()
        self.end = pandas.DataFrame(self.end.kmlgeometry.str.split(' ',1).tolist(),columns = ['x','y'])
        self.end.x = self.end.x.astype(float)
        self.end.y = self.end.y.astype(float)
        self.endlist = list(zip(self.end.x,self.end.y))##list of end points (x,y)
    def create_net(self):
        """Draws a network on the map.

        net should have the following attributes:
            node_styles -- a dictionary of style dictionaries for nodes, including a 'default'
            edge_styles -- a dictionary of style dictionaries for edges, including a 'default'

        Each node/edge data dictionary has a 'style' entry that specifies the style to be looked up
        in node_styles/edge_styles.  If no style is specified the default style is used.  Only attributes
        of the default style are changed in plotting."""
        for i in scipy.arange(len(self.start.x)):
            startNode = 'Start'+str(i)
            endNode = 'End'+str(i)
            self.net.add_node(startNode,lon = self.start.x[i],lat=self.start.y[i],style='default')
            self.net.add_node(endNode,lon=self.end.x[i],lat=self.end.y[i],style='default')
            if self.df.ONE_WAY[i] == 'FT':
                self.net.add_edge(startNode,endNode,style='default',miles = self.df.MILES[i])
            elif self.df.ONE_WAY[i] == 'TF':
                self.net.add_edge(endNode,startNode,style='default',miles = self.df.MILES[i])
            else:
                self.net.add_edge(startNode,endNode,style='default',miles = self.df.MILES[i])
                self.net.add_edge(endNode,startNode,style='default',miles = self.df.MILES[i])
        
    def drawstreets(self):
        self.plotter.drawNetwork(self.net)
        self.plotter.setZoom(-97.8526,30.2147,-97.6264,30.4323)
        self.plotter.getAxes().get_xaxis().set_visible(False)
        self.plotter.getAxes().get_yaxis().set_visible(False)
    
    def drawaddresses(self):
        for i in scipy.arange(len(self.add.Lat)):
            if self.add.Address[i] == 'Engineering Teaching Center, 304 E 26 1/2 St, Austin, TX':
                self.plotter.drawPoints(self.add.Lon[i],self.add.Lat[i],color='green',s=1)
            else:
                self.plotter.drawPoints(self.add.Lon[i],self.add.Lat[i],color='red',s=1)
            
            
#      dict(miles=self.df.MILES[i],streetname=self.df.STREET_NAM[i],leftfrom=self.df.LEFT_FROM_[i],leftto=self.df.LEFT_TO_AD[i],rightfrom=self.df.RIGHT_FROM[i],rightto=self.df.RIGHT_TO_A[i])      
            
if __name__ == '__main__':
    BN = BuildNetwork();
    BN.getstart();
    BN.getend();
    BN.create_net();
    BN.drawstreets();
    BN.drawaddresses();
#    line = BN.drawstreets()