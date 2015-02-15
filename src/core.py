from __future__ import division
from matplotlib.pyplot import colormaps

import textwrap
import random
import math
import os

import numpy as np
from scipy import spatial
from sklearn.cluster import *
import time
import log
from sklearn import metrics
from sklearn import preprocessing


from dataset import *

class Config:
    def __init__(self, params):
        self.dataset = self.create_dataset(params['Dataset'])
        self.n_dims = self.dataset.getColNum()  # dimenzija podataka
        self.k_max = params['Max clusters']
        self.velicina_populacije = params['Population size']
        self.trajanje_svijeta = params['Number of generations']
        self.fitness_metoda = params['Fitness method']
        self.dist_metoda = params['Distance measure']
        self.db_param_q = params['q']
        self.db_param_t = params['t']
        self.weights_on = params['Feature significance'] or False
        self.weights = self.dataset.params['Feature weights']

        if self.dist_metoda == 'Mahalanobis':
            self.inv_cov = np.linalg.inv(np.cov(self.dataset.data, rowvar=0))

    def dist(self, a, b):
        if self.dist_metoda == 'Minkowski_2':
            return spatial.distance.minkowski(a, b, 2)
        elif self.dist_metoda == 'Mahalanobis':
            return spatial.distance.mahalanobis(a, b, self.inv_cov)
        elif self.dist_metoda == 'Cosine':
            return spatial.distance.cosine(a, b) if a[0] <= 1 and a[1] <= 1 and b[1] <= 1 and b[0] <= 1 else 100

    def dist_weighted(self, a, b):
        if self.dist_metoda == 'Minkowski_2':
            return spatial.distance.wminkowski(a, b, p=2, w=self.weights)
        elif self.dist_metoda == 'Mahalanobis':
            return spatial.distance.mahalanobis(a, b, self.inv_cov)
        elif self.dist_metoda == 'Cosine':
            return spatial.distance.cosine(a, b) if a[0] <= 1 and a[1] <= 1 and b[1] <= 1 and b[0] <= 1 else 100


    def dist_db(self, a, b):
        if self.weights_on:
            return self.dist_weighted(a,b)
        else:
            return self.dist(a, b)

    def dist_cs(self, a, b):
        if self.weights_on:
            return self.dist_weighted(a,b)
        else:
             return self.dist(a, b)

    def crossover_rate(self, t): # t jer se vremenom spusta
        return 0.5 +  0.5 * (self.trajanje_svijeta - t) / self.trajanje_svijeta

    def scale_factor(self):
        return 0.25 *( 0.5 + random.random() *0.5)

    def create_dataset(self, dataset):
        if dataset == 'Iris': return Iris()
        elif dataset == 'Glass' : return Glass()
        elif dataset == 'Wine' : return Wine()
        elif dataset == 'Breast cancer' : return Cancer()
        elif dataset == 'Naive' : return Naive()

class Core:
    def __init__(self, config):
        self.config = config
        self.p = Populacija(self.config)
        self.cycles = 0
        self.staro = []

    def setConfig(self, config):
        self.config = config

    def cycle(self):
       if self.cycles < self.config.trajanje_svijeta:
           self.p.evoluiraj(self.cycles)

           fitnessi = np.array([kr.fitness() for kr in self.p.trenutna_generacija])
           najkrom = np.argmax(fitnessi)
           grupiranje = self.p.trenutna_generacija[najkrom].pridruzivanje()
           colormap = self.p.trenutna_generacija[najkrom].grupiranje()
           centri = self.p.trenutna_generacija[najkrom].centri_kromosoma()

           print self.p.trenutna_generacija[najkrom].geni[0:self.config.k_max]
           print colormap

           self.staro = grupiranje
           self.cycles +=1

           return CycleResult(colormap, fitnessi, centri)

class CycleResult():
   def __init__(self, colormap, fitnessmap, centroids):
       self.colormap = colormap
       self.fitnessmap = fitnessmap
       self.centroids = centroids

class Kromosom:
    geni = []

    def koord_centra(self, n):
        return [self.geni[self.config.k_max + self.config.n_dims * n + d] for d in range(self.config.n_dims)]

    def __init__(self, config, g=[], nepravi=False):
        self.config = config
        if nepravi: return

        if len(g):
            self.geni = g
        else:
            # aktivacije klastera
            self.geni = [0.5 + random.random() * 0.5 for cluster in range(config.k_max)]
            # koordinate klastera
            self.geni.extend(
                [random.random()
                 for dim in range(config.n_dims) # za svaku dimenziju
                 for k in range(config.k_max)]   # za svaki centar klastera
            )

        for ccluster in range(config.k_max):
            if self.geni[ccluster] < 0:
                self.geni[ccluster] = 0
            elif self.geni[ccluster] > 1:
                self.geni[ccluster] = 1

            centar = self.koord_centra(ccluster)
            if min(centar) >= 0 and max(centar) <= 1:
                continue

            centar_kvadranta = np.array([0.5 for _ in range(self.config.n_dims)])
            razlika = np.subtract(np.array(centar), centar_kvadranta)
            norma = np.linalg.norm(razlika) * 2
            razlika /= norma
            razlika += centar_kvadranta

            for d in range(self.config.n_dims):
                self.geni[self.config.k_max + self.config.n_dims * ccluster + d] = razlika[d]

        provjereno_ispravno = False
        while not provjereno_ispravno:

            for ccluster in range(config.k_max):
                if self.geni[ccluster] < 0:
                    self.geni[ccluster] = random.random() * 0.4 + 0.05
                elif self.geni[ccluster] > 1:
                    self.geni[ccluster] = 1 - (random.random() * 0.4 + 0.05)

            provjereno_ispravno = True
            # sve odavde do kraja funkcije problematicno
            aktivnih = self.aktivnih_centara()
            if aktivnih < 2:
                for ispravak in random.sample(range(config.k_max), int(2 + random.random() * (config.k_max - 2)) ):
                #for ispravak in random.sample(range(config.k_max), 2 ):
                    self.geni[ispravak] = 0.5 + 0.5 * random.random()
                aktivnih = self.aktivnih_centara()

            particija = self.pridruzivanje(ukljuci_neaktivne_centre=True)
            # particija_neprazno = [p for p in particija if p != []]

            ispravnih = sum([len(grupa) >= 2 and self.geni[ig] > 0.5 for ig, grupa in enumerate(particija)])
            if ispravnih >= 2:
                # gasimo neispravne, dovoljno je ispravnih
                for i, gr in enumerate(particija):
                    if len(gr) < 2 and self.geni[i] > 0:
                        self.geni[i] = random.random() * 0.4 + 0.05
                provjereno_ispravno = True
            else:
                provjereno_ispravno = False
            if not provjereno_ispravno:
                tocaka = self.config.dataset.getRowNum()
                po_grupi = tocaka // aktivnih
                ostaci = tocaka % aktivnih
                prva_iduca_tocka = 0
                for grupa in range(config.k_max):
                    if self.geni[grupa] > 0.5:
                        krajnja = prva_iduca_tocka + po_grupi + (ostaci > 0)
                        ostaci -= 1

                        centar = np.average(self.config.dataset.data[prva_iduca_tocka:krajnja], axis=0)
                        prva_iduca_tocka = krajnja

                        self.geni[config.k_max + config.n_dims * grupa:
                                  config.k_max + config.n_dims * (1 + grupa)] = centar

        if len(self.geni) != config.k_max + config.k_max * config.n_dims:
            print("probl")

        particija = self.pridruzivanje()
        particija = [x for x in particija if len(x) > 1]
        K = len(particija)
        if K <= 1:
            print 'uh oh'

    def centri_kromosoma(self, samo_aktivni = True):
        return [[self.geni[self.config.k_max + self.config.n_dims * i + dim] for dim in range(self.config.n_dims)]
                for i in range(self.config.k_max) if (not samo_aktivni) or self.geni[i] > 0.5]

    def aktivnih_centara(self):
        return sum([1 for centar in range(self.config.k_max) if self.geni[centar] > 0.5])

    def pridruzivanje(self, ukljuci_neaktivne_centre = False):
        if ukljuci_neaktivne_centre:
            centri = self.centri_kromosoma(samo_aktivni=False)
            #aktivni_centri = self.centri_kromosoma(samo_aktivni=True)
            troll_tocka = [1000000 for dim in range(len(self.config.dataset.data[0]))]
            centri = [c if self.geni[ic] > 0.5 else troll_tocka for ic, c in enumerate(centri)]
            p = [[] for _ in centri]
            for t in self.config.dataset.data:
                najbl = np.argmin([self.config.dist(c, t) for c in centri])
                p[najbl].append(t)
            return p
        else:
            centri = self.centri_kromosoma()
            p = [[] for _ in centri]
            for t in self.config.dataset.data:
                najbl = np.argmin([self.config.dist(c, t) for c in centri])
                p[najbl].append(t)
            return p

    def grupiranje(self):
        colormap = np.zeros(len(self.config.dataset.data), dtype=int)
        centri = self.centri_kromosoma()
        for t in self.config.dataset.data:
            najbl = np.argmin([self.config.dist(c, t) for c in centri])
            colormap[self.config.dataset.data.index(t)] = najbl
        return colormap

    def fitness_db(self, particija=[]):
        if not particija:
           particija = self.pridruzivanje()
        particija = [x for x in particija if x != []]

        K = len(particija)

        if K <= 1:
            print 'uh oh'

        centri = [np.average(grupa, axis=0) for grupa in particija]

        #rasprsenja
        S = [math.pow(sum([self.config.dist_db(t, centri[igrupa]) ** self.config.db_param_q for t in grupa]) / len(grupa),
                      1 / self.config.db_param_q)
             for igrupa, grupa in enumerate(particija)]

        return sum(
            [max(
                [(S[igrupa] + S[igrupa2]) /
                 spatial.distance.minkowski(centri[igrupa], centri[igrupa2], self.config.db_param_t)
                 for igrupa2, grupa2 in enumerate(particija) if igrupa != igrupa2])
             for igrupa, grupa in enumerate(particija)]
        ) / K

    def fitness_cs(self, particija=[]):
        if not len(particija):
            particija1 = self.pridruzivanje()
            particija1 = [x for x in particija1 if x != []]
        else:
            particija1 = [x for x in particija if x != []]

        duljine = [len(p) for p in particija1]
        a = np.sum([np.sum([np.amax([self.config.dist_cs(particija1[i][x1], particija1[i][x2])
                          for x2 in range(len(particija1[i]))])
                     for x1 in range(len(particija1[i]))]) / duljine[i]
                 for i in range(len(particija1)) if duljine[i] > 1])


        centri = [np.average(grupa, axis=0) for grupa in particija1]
        b = np.sum([np.amin([self.config.dist_cs(centri[i], centri[j])
                      for j in range(len(particija1))
                      if j != i])
                 for i in range(len(particija1))])

        return a / b

    def fitness(self, particija=[]):
        if self.config.fitness_metoda == 'cs':
            return 1 / (self.fitness_cs(particija) + 0.000001)
        else:
            return 1 / (self.fitness_db(particija) + 0.000001)


class Populacija:

    def __init__(self, config):
        self.config = config
        self.trenutna_generacija = []
        for t in range(config.velicina_populacije):
            self.trenutna_generacija.append(Kromosom(config))

    def probni_vektor(self, k, t):
        if random.random() < self.config.crossover_rate(t):
            fiksirani = self.trenutna_generacija.pop(k)
            izabrani = random.sample(self.trenutna_generacija, 3)
            m, i, j = izabrani[0], izabrani[1], izabrani[2]
            assert isinstance(i, Kromosom)
            self.trenutna_generacija.insert(k, fiksirani) # vracamo privremeno izbaceni element k
            return Kromosom(self.config, np.add(m.geni, np.multiply(self.config.scale_factor(), np.subtract(i.geni, j.geni))))
        else:
            return self.trenutna_generacija[k]

    def evoluiraj(self, t):
        iduca_generacija = []
        for kr in range(self.config.velicina_populacije):
            dobrost = self.trenutna_generacija[kr].fitness()
            probni_vek = self.probni_vektor(kr, t)
            dobrost_alt = probni_vek.fitness()
            iduca_generacija.append(self.trenutna_generacija[kr] if dobrost > dobrost_alt else probni_vek)

        self.trenutna_generacija = iduca_generacija

if __name__ == '__main__':

    
    diffs = []

    preskoci = 0

    resfolder = os.path.join('..', 'res')
    run_groups = []
    run_paths = []
    dbase = []
    for dirname, dirnames, filenames in os.walk(resfolder):
        for subdirname in dirnames:

            basepath = os.path.join(resfolder, subdirname)
            for dirname, dirnames, filenames in os.walk(basepath):
                for f in filenames:
                    f = os.path.join(basepath, f)
                    #if "kmeans" in f or "dbscan" in f or '_Weights' in f:
                    if '_Weights' in f:
                        continue
                    #print f
                    if "kmeans" in f:
                        alg = "kmeans"
                    elif "acde" in f:
                        alg = "acde"
                    elif "dbscan" in f:
                        alg = "dbscan"

                    logger = log.Log()
                    logger.load(f)
                    msrs = logger.measures[len(logger.measures) - 1]
                    info = logger.head_as_array

                    fitm = info[3]
                    distm = info[4]
                    q = int(info[5])
                    t = int(info[6])

                    dbase.append([subdirname, alg, fitm, distm, q, t] + msrs[0:6])

    dbase_wine = filter(lambda x: x[0] == 'Wine', dbase)
    dbase_iris = filter(lambda x: x[0] == 'Iris', dbase)
    dbase_glass = filter(lambda x: x[0] == 'Glass_1', dbase)
    dbases = [dbase_glass, dbase_iris, dbase_wine]

    # koja metrika u prosjeku najbolji score za scores 0 - 4 ?
    latex_table1_prefix = textwrap.dedent("""\\begin{table}[h]
        \\begin{tabular}{l|lllll}
           & Rand & Zajednicka informacija & Homogenost & Potpunost & V-mjera \\\\ \\hline
        """)

    latex_table1_postfix = textwrap.dedent("""\\end{tabular}
        \\caption{CAPT}
        \\label{my-label}
        \\end{table}
        """)

    for db in dbases:
        #print db[0][0], "\n"
        print latex_table1_prefix
        reci = [str(br) for br in range(1, 7)]
        for metric in range(5):
            db_by_metric = sorted(filter(lambda x: x[1] == 'acde', db),
                                  lambda x, y: -cmp(x[metric + 6], y[metric + 6])*100)
            #print metric, db_by_metric

            print 1

            for run in zip(db_by_metric, range(1, 7)):
                if run[0][3] == 'Cosine':
                    hrv = "Cos., "
                elif run[0][3] == 'Minkowski_2':
                    hrv = "Eukl., "
                elif run[0][3] == 'Mahalanobis':
                    hrv = "Mah., "
                dbcs = (' db(' + str(run[0][4]) + ', ' + str(run[0][5]) +')') if run[0][2] == 'db' else ' cs'
                reci[run[1] - 1] += " & \\begin{tabular}[c]{@{}l@{}}" + hrv + dbcs + " \\\\" + str(run[0][metric + 6])  + "\\end{tabular}"

        for r in reci:
            print r, "\\\\\n"

        print latex_table1_postfix.replace('CAPT', db[0][0]), "\n\n"

    exit()

    # ako fiskiramo db/cs, sto je u prosjeku bolje?
    for db in dbases:
        print 2, db[0][0]
        for metr in ['db', 'cs']:
            filt = filter(lambda x: x[2] == metr, filter(lambda x: x[1] == 'acde', db))
            filt = [x[6:] for x in filt]
            filt = [np.array(f) for f in filt] # da mozemo sumirati
            avg =  sum(filt) / len(filt)
            print metr, avg
        print '\n\n'

    # ako fiskiramo metriku i db/cs, sto je u prosjeku bolje?
    for db in dbases:
        print 3, db[0][0]
        for metric in  ["Minkowski_2", "Cosine", "Mahalanobis"]:
            for metr in ['db', 'cs']:
                filt = filter(lambda x: x[2] == metr and x[3] == metric, filter(lambda x: x[1] == 'acde', db))
                filt = [x[6:] for x in filt]
                filt = [np.array(f) for f in filt] # da mozemo sumirati
                avg =  sum(filt) / len(filt)
                print metric, metr, avg
        print '\n\n'

    for db in dbases:
        print 4, db[0][0]
        for metric in  ["Minkowski_2"]: # jer kmeans radi samo s mink
            for metr in ['db', 'cs']:
                latex_plot_text = textwrap.dedent("""\
                    \\begin{tikzpicture}
                    \\begin{axis}[%
                    scatter/classes={%
                        a={mark=square*,blue, mark size=6},%
                        b={mark=square*,red, mark size=6},%
                        c={mark=square*,green, mark size=6}}]
                    \\addplot[scatter,only marks,%
                        scatter src=explicit symbolic]%
                    table[meta=label] {
                    q t label
                    """)

                for t in [int(x) for x in [1, 2, 4]]:
                    for q in [int(x) for x in [1, 2, 4]]:
                        if (q != 1 or t != 1) and metr == 'cs':
                            continue
                        # print metric, metr, q, t, '\n'
                        r_acde = filter(lambda x: x[1] == 'acde' and x[2] == metr and x[3] == metric and x[4] == q and x[5] == t, db)[0]
                        r_kmeans = filter(lambda x: x[1] == 'kmeans' and x[2] == metr and x[3] == metric and x[4] == q and x[5] == t, db)[0]
                        r_dbscan = filter(lambda x: x[1] == 'dbscan' and x[2] == metr and x[3] == metric and x[4] == q and x[5] == t, db)[0]

                        #print r_acde[-1:][0], '\n', r_kmeans[-1:][0], '\n', r_dbscan[-1:][0]
                        z = zip([r_acde[-6:-5][0], r_kmeans[-6:-5][0], r_dbscan[-6:-5][0]], ['a', 'b', 'c'])
                        #print z
                        rez = sorted(z, lambda x, y: cmp(y[0], x[0]))

                        latex_plot_text += str(q) + " " + str(t) + " " + rez[0][1] + "\n"

                latex_plot_text += textwrap.dedent("""\
                    };
                    \\end{axis}
                    \\end{tikzpicture}""")

                print "\n" + metr + "\n\n", latex_plot_text + "\n"


        print '\n\n'

    #print str(dbase_glass).replace('], [', '\n')
    exit()


    for dts in ['Iris', 'Glass', 'Wine']:
        for mcl in [10]:
            if dts == 'Iris':
                mcl = 10
            elif dts == 'Glass':
                mcl = 25
            elif dts == 'Wine':
                mcl = 10
            for dst in ["Minkowski_2"]: # , "Cosine", "Mahalanobis"], jer kmeans je za M2, pa da sve isto bude
                for fs in [True, False]:
                    if dts == 'Wine' and fs:
                        continue # nemamo weightove za Wine
                    for fm in ['db', 'cs']:
                        for t in [1, 2, 4]:
                            for q in [1, 2, 4]:
                                if fm == 'cs' and (t != 1 or q != 1):
                                    continue # ima i uvlacenje losih strana

                                if preskoci > 0:
                                    preskoci -= 1
                                    continue

                                confs = {
                                        'Dataset' : dts,
                                        'Number of generations' : 30,
                                        'Population size': 1,
                                        'Max clusters' : mcl,
                                        'Fitness method': fm,
                                        'q' : q,
                                        't' : t,
                                        'Distance measure': dst,
                                        'Feature significance': fs
                                }

                                print confs

                                fname_sfx = confs['Dataset'] + "_" + confs['Distance measure'] + \
                                ("_Weights_" if confs['Feature significance'] else "_noWeights_") + \
                                confs['Fitness method'] + \
                                ('_' + str(confs['q']) + '_' + str(confs['t']) if confs['Fitness method'] == 'db' else "")


    diffs.sort()
    print diffs
