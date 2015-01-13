import pandas as pd

class Iris(object):

    def __init__(self):
        self.localfile = '../data/iris.data'
        self.df = pd.read_csv(self.localfile, header=None)
        self.classes = self.df[4]
        del self.df[4]

class Wine(object):

    def __init__(self):
        self.localfile = '../data/wine.data'
        self.df = pd.read_csv(self.localfile)

class Cancer(object):

    def __init__(self):
        self.localfile = '../data/breast-cancer-wisconsin.data'
        self.df = pd.read_csv(self.localfile, index_col=0, header=None)
        self.classes = self.df[10]
        del self.df[10]

class Glass(object):

    def __init__(self):
        self.localfile = '../data/glass.data'
        self.df = pd.read_csv(self.localfile, header=None)