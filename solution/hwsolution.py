import pandas
import networkx
import scipy
import logging



class RoadNetWork(object):
    def __init__(self,fname = 'austin.csv'):
        self.df = pandas.read_csv(fname,index_col = 'SEGMENT_ID')

    def createNetwork(self):
        newcols = self.df.kmlgeometry.str.extract('LINESTRING \(([-0-9.]*) ([-0-9.]*)[-, 0-9.]*,([-0-9.]*) ([-0-9.]*)\)').astype(float)
        newcols.columns = ['LonsSt','LatSt','LonEnd','LatEnd']
        self.df = pandas.concat([self.df, newcols], axis=1)
        self.net = networkx.DiGraph()
        node={}
        for i,data in self.df.iterrows():
            stName = hash((data.LatSt, data.LonsSt))
            endName = hash((data.LatEnd, data.LonEnd))
            print i,stName
            if pandas.isnull(data.ONE_WAY) or data.ONE_WAY =='B' or data.ONE_WAY == 'FT':
                self.net.add_edge(stName,endName,data_id=i,time=data.SECONDS,length =data.MILES)
            if pandas.isnull(data.ONE_WAY) or data.ONE_WAY == 'B' or data.ONE_WAY == 'TF':
                self.net.add_edge(endName,stName, data_id=i, time = data.SECONDS, length = data.MILES)
            nodes[stName] = (data.LatSt,data.LonsSt)
            nodes[endName] = (data.LatEnd, data.LonEnd)
            self.net.node[stName]['lat'] = data.LatSt
            self.net.node[stName]['lon'] = data.LonsSt
            self.net.node[endName]['lat'] = data.LatEnd
            self.net.node[endName]['lon'] = data.LonEnd

        self.nodes = pandas.DataFrame.from_dict(nodes, orient='index')
        self.nodes.columns = ['Lat','Lon']

        self_loops = self.net.nodes_with_selfloops()
        self_loops = zip(self_loops, self_loops)
        self.net.remove_edges_from(self_loops)

        self.net.node_styles ={}
        self.net.edge_styles = {}
        self.net.node_styles['default'] = dict(s=0,color='blue')
        self.net.edge_styles['default'] = dict(lw=0.15,color='blue')

    def findClosestNode(self,lat,lon):
        arr = scipy.column_stack((self.nodes.Lat.tolist(),self.nodes.Lon.tolist()))
        target = scipy.array([lat,lon])
        sub = arr - target
        dist = scipy.sqrt(scipy.sum(sub*sub,axis=1))
        dist = pandas.DataFrame(dist)
        node = dist.idxmin()
        return self.nodes.loc[node]

    def getSPNetworkx(self,startnode,destnode):
        path = networkx.shortest_path(self.net,startnode,destnode,weight='time')
        return path

    def getSPCplex(self,startnode,destnode):
        import pyomo
        import pyomo.opt
        import pyomo.environ as pe
        self.m = pe.ConcreteModel()

        self.m.node_set = pe.Set(initialize=sorted(self.net.nodes()))
        self.m.arc_set = pe.Set(initialize=sorted(self.net.edges()), dimen=2)

        self.m.Y = pe.Var(self.m.arc_set, domain=pe.NonNegativeReals)

        def obj_rule(m):
            return sum(m.Y[e] * self.net.edge[e[0]][e[1]]['time'] for e in self.m.arc_set)

        self.m.OBJ = pe.Objective(rule=obj_rule, sense=pe.minimize)

        def flow_bal_rule(m, n):
            preds = self.net.predecessors(n)
            succs = self.net.successors(n)
            return sum(m.Y[(p, n)] for p in preds) - sum(m.Y[(n, s)] for s in succs) == 0 - 1 * int(
                n == startnode) + 1 * (n == destnode)

        self.m.FlowBal = pe.Constraint(self.m.node_set, rule=flow_bal_rule)

        solver = pyomo.opt.SolverFactory('cplex')
        results = solver.solve(self.m, tee=True, keepfiles=False,
                               options_string='mip_tolerances_integrality=1e-9 mip_tolerance_mipgap=0')
        if results.solver.status != pyomo.opt.SolverStatus.ok:
            logging.warning('Check solver not ok?')
        if results.solver.termination_condition != pyomo.opt.TerminationCondition.optimal:
            logging.warning('Check solver optimality?')

        curnode = startnode
        path = []
        path.append(curnode)
        while curnode != destnode:
            for n in self.net.successors(curnode):
                if int(self.m.Y[curnode, n]) == 1:
                    curnode = n
                    path.append(curnode)
                    break
        return path

    def setEdgeStyle(self,edgelist,style,style_name=None):
        if style_name == None:
            import uuid
            style_name = str(uuid.uuid4())
        self.net.edge_styles[style_name] = style
        for e in edgelist:
            self.net.edge[e[0]][e[1]]['style'] = style_name

    def setNodeStyle(self, nodelist, style, style_name=None):
        if style_name == None:
            import uuid
            style_name = str(uuid.uuid4())
        self.net.node_styles[style_name] = style
        for e in nodelist:
            self.net.node[n]['style'] = style_name

if __name__ == '__main__':
        r = RoadNetWork()
        r.createNetwork()
        import geoplotter
        g = geoplotter.GeoPlotter()
        a = pandas.read_csv('address.csv')
        nodes = [r.findClosestNode(x.Lat,x.Lon).name for i,x in a.iterrows()]
        r.setNodeStyle(nodes[:-1],dict(color='red',s=15),'delivery')
        r.setNodeStyle(nodes[-1:],dict(color='green',s=15),'depot')

        a['nodeid'] = nodes
        hulahut = a[a.Address.str.contains('Hula')].nodeid.values[0]
        etc = a[a.Address.str.contains('Engineering')].nodeid.values[0]
        path = r.getSPNetorkx(etc,hulahut)
        edges = zip(path[:-1],path[1:])
        r.setEdgeStyle(edges,dict(color='orange',lw=2),'hulahutpath')
        g.clear()
        g.drawNetwork(r.net)
        g.setZoom(-97.8526,30.2147,-97.6264,30.4323)

