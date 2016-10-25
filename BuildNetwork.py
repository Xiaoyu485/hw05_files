# -*- coding: utf-8 -*-
"""
Created on Fri Oct 21 14:07:37 2016

@author: Shaw
"""
import pandas
import scipy
import pyomo
import re
import networkx
import geoplotter




class BuildNetwork():
    def __init__(self,fname='austin.csv'):
        self.df = pandas.read_csv(fname)
        self.add = pandas.read_csv('addresses.csv')
        self.plotter = geoplotter.GeoPlotter()
        self.net = networkx.DiGraph(node_styles = dict(default=dict()),edge_styles=dict(default=dict(color='blue',linewidths=0.1)))
        self.nodearray=[]
        self.arcframe = pandas.DataFrame(columns=['Start','End','Miles'])
        self.nodeframe=pandas.DataFrame(columns=['node'])
#        self.df['way']=self.df.kmlgeometry.str.extractall('\((.*)\)')

    def getstart(self):
        self.start = self.df.kmlgeometry.str.extract('\(([0-9-.]* [0-9-.]*),')
        self.start = self.start.to_frame()
        self.start = pandas.DataFrame(self.start.kmlgeometry.str.split(' ',1).tolist(),columns = ['x','y'])
        self.start.x = self.start.x.astype(float)
        self.start.y = self.start.y.astype(float)
        self.df['Start'] = self.start.x.astype(str)+ ' ' + self.start.y.astype(str)
        self.startlist = list(zip(self.start.x,self.start.y)) ##list of start points (x,y)
        
    def getend(self):
        self.end = self.df.kmlgeometry.str.extract(',([0-9-.]* [0-9-.]*)\)')
        self.end = self.end.to_frame()
        self.end = pandas.DataFrame(self.end.kmlgeometry.str.split(' ',1).tolist(),columns = ['x','y'])
        self.endstring = self.end
        self.end.x = self.end.x.astype(float)
        self.end.y = self.end.y.astype(float)
        self.df['End'] = self.end.x.astype(str)+ ' ' + self.end.y.astype(str)
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
            
            node1 = self.df.Start[i] ##shoter version of decimal by string conversion for node name
            node2 = self.df.End[i]
            self.net.add_node(node1,lon = self.start.x[i],lat=self.start.y[i],style='default')
            self.net.add_node(node2,lon=self.end.x[i],lat=self.end.y[i],style='default')
            if self.df.ONE_WAY[i] == 'FT':
                self.net.add_edge(node1,node2,style='default',miles = self.df.MILES[i])
                self.nodearray.append([self.start.x[i],self.start.y[i]])
                df2 = pandas.DataFrame([node1,node2,self.df.MILES[i]],columns=['start','node','miles'])
                self.arcframe.append(df2)
            elif self.df.ONE_WAY[i] == 'TF':
                self.net.add_edge(node2,node1,style='default',miles = self.df.MILES[i])
                self.nodearray.append([self.start.x[i],self.start.y[i]])
            else:
                self.net.add_edge(node1,node2,style='default',miles = self.df.MILES[i])
                self.net.add_edge(node2,node1,style='default',miles = self.df.MILES[i])
                self.nodearray.append([self.start.x[i],self.start.y[i]])
                self.nodearray.append([self.start.x[i],self.start.y[i]])

        self.nodearray = scipy.array(self.nodearray)
        
    def drawstreets(self):
        self.plotter.drawNetwork(self.net)
        self.plotter.setZoom(-97.8526, 30.2147, -97.6264, 30.4323)
        self.plotter.getAxes().get_xaxis().set_visible(False)
        self.plotter.getAxes().get_yaxis().set_visible(False)
    
    def drawaddresses(self):
        for i in scipy.arange(len(self.add.Lat)):
            if self.add.Address[i] == 'Engineering Teaching Center, 304 E 26 1/2 St, Austin, TX':
                self.plotter.drawPoints(self.add.Lon[i],self.add.Lat[i],color='green',s=1)
            else:
                self.plotter.drawPoints(self.add.Lon[i],self.add.Lat[i],color='red',s=1)
    
    def findclosest(self): ##data is a dictionary of the coordinates
        self.add['Closest_Node'] = self.add['Lon']
        self.addressarray = []
        for i in scipy.arange(len(self.add.Lon)):
            self.addressarray.append([self.add.Lon[i],self.add.Lat[i]])
        self.addressarray =scipy.array(self.addressarray)
        i=0
        for loc in self.addressarray:
            dis = -scipy.sqrt(scipy.sum((self.nodearray-loc)*(self.nodearray-loc),axis=1))
            idx = scipy.argmax(dis)
            node = str(self.nodearray[idx][0])+' '+str(self.nodearray[idx][1])
            self.add.Closest_Node.iloc[i] = node
            i+=1

    
    def getSPNetworkx(self):
        start = self.add.Closest_Node.loc[15]
        end = self.add.Closest_Node.loc[3]
        route = networkx.shortest_path(self.net,source=start,target=end,weight='miles')
        return route
       
    def drawroute(self,route):
        routel = len(route)
        for i in scipy.arange(routel-1):
            node1 = route[i]
            node2 = route[i+1]
            way = self.df.kmlgeometry[((self.df.Start==node1) & (self.df.End == node2))|((self.df.Start==node2) & (self.df.End == node1))].str.extract('\((.*)\)').tolist()
#            if not self.df[((self.df.Start==node2) & (self.df.End == node1))].empty:
#                if self.df[((self.df.Start==node1) & (self.df.End == node2))].empty:
#                    print node1, node2
#                    print self.df[self.df.End==node1].ONE_WAY

            way = way[0].split(',')
            self.drawway(way)
    
    def drawway(self,way):
        line = []
        r = []
        waylen = len(way)
        for i in scipy.arange(waylen):
            node1 = way[i]
            node1 = node1.split()
            node1 = [float(i) for i in node1]
            r.append((node1[0],node1[1]))
        line.append(r)
        self.plotter.drawLines(line,color='orange',alpha=0.92)
    
    def getSPCplex(self):
        self.nodeframe=pandas.DataFrame(self.net.nodes(),columns=['node'])
#        def loaddata():
            

if __name__ == '__main__':
    BN = BuildNetwork();
    BN.getstart();
    BN.getend();
    BN.create_net();
    BN.findclosest();
    path = BN.getSPNetworkx();
    BN.drawstreets();
    BN.drawroute(path)#  
    BN.drawaddresses();
