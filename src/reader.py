from __future__ import division

class Dataset(object):
    def __init__(self):
        self.data = []

    def readFile(self, localfile, classCol=False):
        f = open(localfile, "r")
        for columns in ( raw.strip().split(',') for raw in f):
            if classCol:
                self.data.append([float(col) for col in columns[:-1]])
                self.classes = columns[-1]
            else:
                self.data.append([float(col) for col in columns])
                self.classes = None
        self.normalize()

    def readArray(self, arr):
        self.data = [[t[0], t[1]] for t in arr]
        self.normalize()

    def normalize(self):
        for dim in range(self.getColNum()):
            min_d, max_d = min([t[dim] for t in self.data]), max([t[dim] for t in self.data])
            for t in self.data:
                t[dim] -= min_d
                t[dim] /= (max_d - min_d)

    def getColNum(self):
        return len(self.data[0])

    def getRowNum(self):
        return len(self.data)

class Iris(Dataset):

    def __init__(self):
        self.localfile = '../data/iris.data'
        Dataset.__init__(self)
        Dataset.readFile(self, self.localfile, classCol=True)

class Wine(Dataset):

    def __init__(self):
        self.localfile = '../data/wine.data'
        Dataset.__init__(self)
        Dataset.readFile(self, self.localfile)

class Cancer(Dataset):

    def __init__(self):
        self.localfile = '../data/breast-cancer-wisconsin.data'
        Dataset.__init__(self)
        Dataset.readFile(self, self.localfile, classCol=True)

class Glass(Dataset):

    def __init__(self):
        self.localfile = '../data/glass.data'
        Dataset.__init__(self)
        Dataset.readFile(self, self.localfile, classCol=True)

class Naive(Dataset):
    def __init__(self):
        tocke = [(36, 39), (20, 42), (26, 27), (23, 43), (32, 33), (24, 39), (36, 39), (23, 32), (36, 44), (24, 37),
             (26, 31), (27, 30), (37, 45), (37, 28), (24, 25), (29, 44), (29, 26), (31, 28), (32, 35), (36, 27),
             (34, 26), (30, 30), (22, 27), (22, 42), (30, 35), (23, 40), (32, 27), (32, 28), (26, 33), (20, 39),
             (30, 40), (28, 33), (26, 42), (45, 50), (52, 53), (57, 45), (48, 36), (55, 54), (49, 55), (49, 45),
             (56, 51), (46, 52), (55, 49), (58, 52), (59, 38), (65, 47), (47, 38), (51, 43), (57, 45), (48, 39),
             (56, 41), (59, 53), (49, 52), (57, 37), (60, 54), (58, 54), (62, 44), (56, 46), (56, 39), (56, 49),
             (57, 54), (53, 36), (48, 48), (46, 43), (61, 45), (62, 49), (52, 54), (56, 80), (63, 78), (56, 64),
             (62, 70), (62, 67), (73, 79), (57, 68), (68, 79), (61, 69), (64, 71), (59, 76), (67, 69), (56, 67),
             (59, 61), (71, 66), (59, 79), (61, 66), (63, 66), (65, 67), (65, 75), (56, 60), (62, 60), (70, 76),
             (74, 70), (74, 80), (58, 68), (62, 65), (65, 77), (56, 73), (58, 67), (63, 64), (56, 79), (61, 62)]
        Dataset.__init__(self)
        Dataset.readArray(self, tocke)

