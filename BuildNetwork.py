# -*- coding: utf-8 -*-
"""
Created on Fri Oct 21 14:07:37 2016

@author: Shaw
"""
import pandas
import pyomo
import networkx
import geoplotter




class BuildNetwork():
    def __init__(self,fname='austin.csv'):
        self.df = pandas.read_csv(fname)

    def getstart(self):
        self.start = self.df.kmlgeology.str.extract('\(([0-9-.]* [0-9-.]*),')