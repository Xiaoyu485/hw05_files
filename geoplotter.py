# -*- coding: utf-8 -*-
"""
Created on Fri Oct 21 14:22:00 2016


"""

#Author: Ned Dimitrov
#Date: 09/11/14

from mpl_toolkits.basemap import Basemap
import mpl_toolkits.basemap.shapefile as shapefile
import scipy
from scipy import array
import matplotlib.pyplot
import pylab
 
class GeoPlotter:  
    """Class for plotting geographic objects using matplotlib.
    
    The class is largely a wrapper for basemap and associated functions."""

    def __init__(self, **kwargs):
        """Creates the map.
      
        kwargs -- arguments to a Basemap object"""
        defaults = dict(projection = 'cyl', 
                llcrnrlon=-180,
                llcrnrlat=-90,
                urcrnrlon=180,
                urcrnrlat=90,
                area_thresh=1000,
                resolution='h')
        defaults.update(kwargs)
        self.zorder = 0
        self.m = Basemap(**defaults)
        #pylab.rc('lines', solid_capstyle='round', solid_joinstyle='bevel', dash_capstyle='round', dash_joinstyle='bevel')

    def getAxes(self):
        ax = self.m.ax
        if ax == None:
            return pylab.gca()
        return ax

    def getFigure(self):
        return self.getAxes().figure

    def setAxisSize(self, pos):
        """Mostly a wrapper for ax.set_position.  Sets the size of the axis, relative to the total figure."""
        self.getAxes().set_position(pos)

    def autoSizeAxes(self):
        xlength = float(self.m.urcrnrx - self.m.llcrnrx)
        ylength = float(self.m.urcrnry - self.m.llcrnry)
        maxlen = max(xlength, ylength)
        xlength = xlength/maxlen
        ylength = ylength/maxlen
        self.getAxes().figure.set_figheight(ylength*10)
        self.getAxes().figure.set_figwidth(xlength*10)
        self.setAxisSize([.05,.05,.9,.9])
 
    def setZoom(self, llcrnrlon, llcrnrlat, urcrnrlon, urcrnrlat, border=0):
        x1,y1 = self.m(llcrnrlon-border,llcrnrlat-border)
        x2,y2 = self.m(urcrnrlon+border,urcrnrlat+border)
        self.m.llcrnrlon = llcrnrlon - border
        self.m.llcrnrlat = llcrnrlat - border
        self.m.llcrnrx = x1
        self.m.llcrnry = y1
        self.m.urcrnrlon = urcrnrlon + border
        self.m.urcrnrlat = urcrnrlat + border
        self.m.urcrnrx = x2
        self.m.urcrnry = y2
        ax = self.getAxes()
        ax.set_ylim(y1,y2)
        ax.set_xlim(x1,x2)
        self.redraw()

    def redraw(self):
        self.getAxes().figure.canvas.draw()
    
    def clear(self):
        self.getAxes().clear()
    
    def savefig(self, *arg, **kwarg):
        """Wrapper for figure.savefig"""
        defaults = dict(facecolor = 'lightsteelblue', edgecolor='lightsteelblue')
        defaults.update(kwarg)
        self.getAxes().figure.savefig(*arg, **defaults)

    def _set_zorder(self, args):
        if 'zorder' not in args:
            args['zorder'] = self.zorder
            self.zorder += 1
        else:
            self.zorder = max(self.zorder, args['zorder']) + 1
        return args

    def _get_next_zorder(self):
        self.zorder += 1
        return self.zorder - 1

    def drawMapBoundary(self, **kwargs):
        """Largely a wrapper for Basemap.drawmapboundary.  Provides some defaults"""
        defaults = dict(fill_color = 'lightsteelblue', linewidth=0)
        defaults.update(kwargs)
        defaults = self._set_zorder(defaults)
        self.m.drawmapboundary(**defaults) 
    
    def drawCoastLines(self, **kwargs):
        """Largely a wrapper for Basemap.drawcoastlines.  Provides some defaults"""
        defaults = dict(linewidth = 0.5)
        defaults.update(kwargs)
        defaults = self._set_zorder(defaults)
        self.m.drawcoastlines(**defaults) 
    
    def drawCountries(self, **kwargs):
        """Largely a wrapper for Basemap.drawcountries.  Provides some defaults"""
        defaults = dict(linewidth = 0.5)
        defaults.update(kwargs)
        defaults = self._set_zorder(defaults)
        self.m.drawcountries(**defaults) 
    
    def drawStates(self, **kwargs):
        """Largely a wrapper for Basemap.drawstates.  Provides some defaults"""
        defaults = dict(linewidth = 0.5)
        defaults.update(kwargs)
        defaults = self._set_zorder(defaults)
        self.m.drawstates(**defaults) 

    def drawWorld(self):
        """Draws oceans, continents, coastlines, countries, and states."""
        self.drawMapBoundary()
        self.fillContinents()
        self.drawCoastLines(linewidth=0.7)
        self.drawCountries(linewidth=1.5)
        self.drawStates(linewidth=0.7)
    
    def drawParallels(self, **kwargs):
        """Largely a wrapper for Basemap.drawcoastlines.  Provides some defaults"""
        defaults = dict(color = 'k') 
        defaults.update(kwargs)
        defaults = self._set_zorder(defaults)
        self.m.drawparallels(**defaults) 
    
    def drawMeridians(self, **kwargs):
        """Largely a wrapper for Basemap.drawcoastlines.  Provides some defaults"""
        defaults = dict(color = 'k') 
        defaults.update(kwargs)
        defaults = self._set_zorder(defaults)
        self.m.drawmeridians(**defaults) 
    
    def setBBoxZoomShapefile(self, name, idxs, border_perc = 0.1):
        """Set the zoom to a bounding box defined by the polygons in shapefile <name> and indices <idxs>.

        border_perc -- the percentage of space to leave for a border around the region"""
        shapes = []
        for idx in idxs:
            shapes.append( getattr(self.m, name)[idx] )
        self.setBBoxZoom( shapes, border_perc = border_perc )

   
    def setBBoxZoom(self, shapes, border_perc = 0.1):
        """Set the zoom to a bounding box defined by the shapes in <shapes>.

        shapes -- [ [(lat, lon)] ]
        border_perc -- the percentage of space to leave for a border around the region"""
        min_lat = scipy.inf
        max_lat = -scipy.inf
        min_lon = scipy.inf
        max_lon = -scipy.inf
        for sh in shapes:
            for lat,lon in sh:
                min_lat = min(lat, min_lat)
                min_lon = min(lon, min_lon)
                max_lat = max(lat, max_lat)
                max_lon = max(lon, max_lon)
        self.setZoom(min_lat, min_lon, max_lat, max_lon, border = border_perc* min(max_lat - min_lat, max_lon - min_lon) )


    def readShapefile(self, shapefileLoc, name):
        """shapefileLoc -- the location of the shapefile.  For example 'world_borders/TM_WORLD_BORDERS-0.3.' 
                           expects the corresponding .shp .dbf etc files to be there
           name -- the shapefile will be stored in self.m.name and info in self.m.name_info  You can then 
                   use that to plot polygons etc on the map"""
        self.m.readshapefile(shapefileLoc,name,drawbounds=False)
   
    def drawShapes(self, name, idxs, **kwargs):
        """Draw the shapes from shapefile <name> with indices <idxs> using the properties in <kwargs>"""
        defaults = dict(facecolor = 'orange', lw=0) 
        defaults.update(kwargs)
        defaults = self._set_zorder(defaults)
        collection = []
        for i in idxs:
            poly = matplotlib.patches.Polygon( getattr(self.m, name)[i])
            collection.append(poly)
        collection = matplotlib.collections.PatchCollection(collection, **defaults )
        self.getAxes().add_collection(collection)


    def fillContinents(self, **kwargs):
        """Largely a wrapper for Basemap.fillcontinents.  Provides some defaults"""
        defaults = dict(color = (0.94901960784313721, 0.93725490196078431, 0.97647058823529409),
                lake_color = 'lightsteelblue')
        defaults.update(kwargs)
        defaults = self._set_zorder(defaults)
        self.m.fillcontinents(**defaults) 

    def drawPoints(self,lon,lat, **kwargs):  
        """Largely a wrapper for Basemap.scatter.  Provides some defaults"""
        defaults = dict(color = 'b',
                marker = 'o')
        defaults.update(kwargs)
        defaults = self._set_zorder(defaults)
        self.m.scatter(lon,lat,**defaults)

    def drawLines(self, lines, **kwargs):
        """Largely a wrapper for LineCollection.  Draw lines on the map. 

        lines -- a list of lines [ [(x1, y1), (x2, y2)], [(x1, y1), (x2, y2), (x3, y3)] ]"""
        defaults = dict(color = 'g')
        defaults.update(kwargs)
        defaults = self._set_zorder(defaults)
        lc = matplotlib.collections.LineCollection(lines, **defaults)
# Getting the path to bevel this way is just too hard, and probably not worth it
# Probably the right way to do it is make my own "beveled line collection" class.
# Or maybe add a keyword attribute for "bevel" for each line?
#        if 'linewidth' in defaults:
#             newparams = defaults.copy()
#             del newparams['linewidth']
#             newparams = self._set_zorder(newparams)
#             xs = []
#             ys = []
#             s = []
#             for i, line in enumerate(lines):
#                 for point in line:
#                     xs.append(point[0])
#                     ys.append(point[1])
#                     s.append( (defaults['linewidth'][i] / 2.0)**2 * scipy.pi )
#             self.drawPoints(xs, ys, s=s, **newparams)
        self.getAxes().add_collection(lc)
    
    def figureText(self,x,y,txt, **kwarg):
        """Largely a wrapper for axes.text.  Provides some defaults"""
        self.getAxes().text(x,y,txt,**kwarg)

    def annotate(self, text, xy, **kwargs):
        """Largely a wrapper for axes.annotate.  Provides some defaults"""
        defaults = dict(xycoords='data',
                    xytext=(20, 20), textcoords='offset points',
                    size=18,
                    bbox=dict(boxstyle="round4,pad=.5", fc="0.9"),
                    arrowprops=dict(arrowstyle="fancy",fc="0.6",
                        connectionstyle="angle3,angleA=0,angleB=-90", edgecolor='black', linewidth=1)
                    )
        if 'bbox' in kwargs:
            defaults['bbox'].update(kwargs['bbox'])
            del kwargs['bbox']
        if 'arrowprops' in kwargs:
            defaults['arrowprops'].update(kwargs['arrowprops'])
            del kwargs['arrowprops']
        defaults.update(kwargs)
        defaults = self._set_zorder(defaults)
        ax = self.getAxes()
        try:
            return ax.annotate(text, xy=xy, **defaults)
        except ValueError:
            defaults['arrowprops'] = dict(arrowstyle="->",connectionstyle="angle,angleA=0,angleB=-90,rad=10")
            return ax.annotate(text, xy=xy, **defaults)

    def _getNodeLonLat(self, node, node_data):
        if hasattr(node, 'lon'):
           lon = node.lon
           lat = node.lat
        elif 'lon' in node_data:
           lon = node_data['lon']
           lat = node_data['lat']
        elif 'Lon' in node_data:
           lon = node_data['Lon']
           lat = node_data['Lat']
        else:
            raise ValueError('Node does not have lat/lon specs %s'%repr(node))
        return lon,lat

    def drawNetwork(self, net, greatCircle=False):
        """Draws a network on the map.

        net should have the following attributes:
            node_styles -- a dictionary of style dictionaries for nodes, including a 'default'
            edge_styles -- a dictionary of style dictionaries for edges, including a 'default'

        Each node/edge data dictionary has a 'style' entry that specifies the style to be looked up
        in node_styles/edge_styles.  If no style is specified the default style is used.  Only attributes
        of the default style are changed in plotting."""
        # plot the edges
        edge_kwargs = {}
        default_style = net.graph['edge_styles']['default']
        edge_options = default_style.keys()
        for name in edge_options:
            edge_kwargs[name] = []
        lines = []
        if 'bevel' in edge_options:
            bevel_lon = []
            bevel_lat = []
            bevel_kwargs = {}
            bevel_kwargs['s'] = []
            for name in edge_options:
                bevel_kwargs[name] = []
            del bevel_kwargs['bevel']
            del edge_kwargs['bevel']
        for node1, node2, edge_data in net.edges(data=True):
            new_line = []
            new_line.append( self._getNodeLonLat( node1, net.node[ node1 ]) )
            new_line.append( self._getNodeLonLat( node2, net.node[ node2 ]) )
            lines.append(new_line)
            line_style = default_style.copy()
            if 'style' in edge_data:
                line_style.update( net.graph['edge_styles'].get( edge_data['style'], {}) )
            line_style.update(edge_data) 
            if 'bevel' in edge_options:
                if line_style['bevel']:
                    bevel_lon.append(new_line[0][0])
                    bevel_lat.append(new_line[0][1])
                    bevel_lon.append(new_line[1][0])
                    bevel_lat.append(new_line[1][1])
                    bevel_kwargs['s'].append( (line_style['linewidth']/2.0)**2 * scipy.pi )
                    bevel_kwargs['s'].append( (line_style['linewidth']/2.0)**2 * scipy.pi )
                    for name in edge_options:
                        if name == 'bevel': continue
                        bevel_kwargs[name].append(line_style[name])
                        bevel_kwargs[name].append(line_style[name])
                    bevel_kwargs['linewidth'][-1] = 0
                    bevel_kwargs['linewidth'][-2] = 0
            for name in edge_options:
                if name == 'bevel': continue
                edge_kwargs[name].append(line_style[name])
        if not greatCircle:
            self.drawLines(lines,**edge_kwargs)
        else:
            i = 0
            for i in range(len(lines)):
                lon1, lat1 = lines[i][0]
                lon2, lat2 = lines[i][1]
                kwargs = {}
                for name in edge_options:
                    if name == 'bevel': continue
                    kwargs[name] = edge_kwargs[name][i]
                kwargs = self._set_zorder(kwargs)
                self.m.drawgreatcircle(lon1,lat1,lon2,lat2,**kwargs)
        if 'bevel' in edge_options and len(bevel_lon) > 0:
            self.drawPoints(bevel_lon, bevel_lat, **bevel_kwargs)
        # plot the nodes
        node_kwargs = {}
        default_style = net.graph['node_styles']['default']
        node_options = default_style.keys()
        for name in node_options:
            node_kwargs[name] = []
        lon = []
        lat = []
        for node, node_data in net.nodes(data=True):
            node_lon,node_lat = self._getNodeLonLat(node, node_data)
            lon.append(node_lon)
            lat.append(node_lat)
            node_style = default_style.copy()
            if 'style' in node_data:
                node_style.update( net.graph['node_styles'].get( node_data['style'], {}) )
            node_style.update(node_data)
            for name in node_options:
                node_kwargs[name].append(node_style[name])
        lon = scipy.array(lon)
        lat = scipy.array(lat)
        if 'marker' not in node_options:
            node_kwargs = self._set_zorder(node_kwargs)
            #self.drawPoints(lon,lat,**node_kwargs)
        else:
            # Have to plot each type of marker separately
            markers = scipy.array(node_kwargs['marker'])
            marker_types = scipy.unique(markers)
            del node_kwargs['marker']
            for m in marker_types:
                idxs = scipy.where(markers==m)[0]
                tmp_node_kwargs = {}
                for k,v in node_kwargs.iteritems():
                    tmp_node_kwargs[k] = list(scipy.array(v)[idxs])
                tmp_node_kwargs['marker'] = m
                tmp_node_kwargs = self._set_zorder(tmp_node_kwargs)
                self.drawPoints(lon[idxs],lat[idxs],**tmp_node_kwargs) 
        min_lat = lat.min()
        max_lat = lat.max()
        lat_range = max_lat - min_lat
        min_lon = lon.min()
        max_lon = lon.max()
        lon_range = max_lon - min_lon
#        self.setZoom(-97.8526,30.2147,-97.6264,30.4323)
        self.setZoom(min_lon - .1*lon_range, min_lat - .1*lat_range, max_lon + .1*lon_range, max_lat + .1*lat_range)
    
