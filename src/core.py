from __future__ import division
 
import numpy as np
import random
import math
import matplotlib.pyplot as plt
from scipy import spatial

from reader import *

class Config:
    def __init__(self, params):
        self.dataset = self.create_dataset(params['Dataset'])
        self.n_dims = self.dataset.getColNum()  # dimenzija podataka
        self.k_max = params['Max clusters']
        self.velicina_populacije = params['Population size']
        self.trajanje_svijeta = params['Number of generations']
        self.fitness_metoda = params['Fitness method']
        self.db_param_q = params['q']
        self.db_param_t = params['t']

    def distNd(self, a, b, p):
        sum = 0
        for i in range(len(a)):
            sum += (a[i] - b[i])**p
        return math.pow(sum, 1 / p)

    #def dist_db(self, a, b):
    #    return np.power(self.distNd(a, b, 2), self.db_param_q)

    def dist(self, a, b):
        return self.distNd(a, b, 2)

    def dist_db(self, a, b):
        return self.dist(a, b);

    def dist_cs(self, a, b):
        return self.dist(a, b);

    def crossover_rate(self, t): # t jer se vremenom spusta
        return 0.5 + 0.5 * (self.trajanje_svijeta - t) / self.trajanje_svijeta

    def scale_factor(self):
        return 0.5 + random.random() *0.5

    def create_dataset(self, dataset):
        if dataset == 'Iris': return Iris()
        elif dataset == 'Glass' : return Glass()
        elif dataset == 'Wine' : return Wine()
        elif dataset == 'Breast cancer' : return Cancer()

class Core:
    def __init__(self, config):
        self.config = config
        self.p = Populacija(self.config)
        self.cycles = 0
        self.staro = []

    def setConfig(self, config):
        self.config = config

    def start(self):
        p = Populacija(self.config)
        plt.xlim(-50, 150)
        plt.ylim(-50, 150)

        for i in range(self.config.trajanje_svijeta):
            p.evoluiraj(i)
            print(i, '/', self.config.trajanje_svijeta)

            najkrom = np.argmax([kr.fitness() for kr in p.trenutna_generacija])
            grupiranje = p.trenutna_generacija[najkrom].pridruzivanje()

            if i % 1 == 0:
                #plt.clf()
                for klasa in grupiranje:
                    plt.plot([t[0] * 100 for t in klasa], [t[1] * 100 for t in klasa], 'o', markersize=12 , color=(random.random(), random.random(), random.random()))
                #plt.show()

    def cycle(self):
        if self.cycles < self.config.trajanje_svijeta:
            self.p.evoluiraj(self.cycles)

            najkrom = np.argmax([kr.fitness() for kr in self.p.trenutna_generacija])
            grupiranje = self.p.trenutna_generacija[najkrom].pridruzivanje()
            colormap = self.p.trenutna_generacija[najkrom].grupiranje()
            if not np.array_equal(self.staro, grupiranje):
                print('promjena')

            self.staro = grupiranje
            self.cycles +=1
            return colormap

class Kromosom:
    geni = []

    def __init__(self, config, g=[]):
        self.config = config
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

        provjereno_ispravno = False
        while not provjereno_ispravno:
            provjereno_ispravno = True
            # sve odavde do kraja funkcije problematicno
            aktivnih = self.aktivnih_centara()
            if aktivnih < 2:
                for ispravak in random.sample(range(config.k_max), 2):
                    self.geni[ispravak] = 0.5 + 0.5 * random.random()
                aktivnih = self.aktivnih_centara()

            particija = self.pridruzivanje()
            particija_neprazno = [p for p in particija if p != []]

            ispravnih = sum([len(grupa) >= 2 for grupa in particija])
            if ispravnih >= 2:
                # gasimo neispravne, dovoljno je ispravnih
                particija = [grupa for grupa in particija if len(grupa) >= 2]
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

    def aktivni_centri(self):
        return [[self.geni[self.config.k_max + self.config.n_dims * i + dim] for dim in range(self.config.n_dims)]
                for i in range(self.config.k_max) if self.geni[i] > 0.5]

    def aktivnih_centara(self):
        return len(self.aktivni_centri())

    def pridruzivanje(self):
        centri = self.aktivni_centri()
        p = [[] for c in centri]
        for t in self.config.dataset.data:
            najbl = np.argmin([self.config.dist(c, t) for c in centri])
            p[najbl].append(t)
        return p

    def grupiranje(self):
        colormap = np.zeros(len(self.config.dataset.data), dtype=int)
        for t in self.config.dataset.data:
            najbl = np.argmin([self.config.dist(c, t) for c in self.aktivni_centri()])
            colormap[self.config.dataset.data.index(t)] = najbl
        return colormap

    def fitness_db(self, particija=[]):
        if not particija:
           particija = self.pridruzivanje()

        particija = [x for x in particija if x != []]

        K = len(particija)
        duljine = [len(grupa) for grupa in particija]

        centri = [np.average(grupa, axis=0) for grupa in particija]

        #rasprsenja
        S = [math.pow(sum([self.config.dist_db(t, centri[igrupa]) ** self.config.db_param_q for t in grupa]) / len(grupa),
                      1 / self.config.db_param_q)
             for igrupa, grupa in enumerate(particija)]

        return K / sum(
            [max(
                [(S[igrupa] + S[igrupa2]) /
                 self.config.distNd(centri[igrupa], centri[igrupa2], self.config.db_param_t)
                 for igrupa2, grupa2 in enumerate(particija) if igrupa != igrupa2])
             for igrupa, grupa in enumerate(particija)]
        )

    def fitness_cs(self, particija=[]):
        if not particija:
            particija = self.pridruzivanje()

        K = len(particija)
        duljine = [len(p) for p in particija]
        a = sum([sum([max([self.config.dist_cs(particija[i][x1], particija[i][x2])
                          for x2 in range(len(particija[i]))])
                     for x1 in range(len(particija[i]))]) / duljine[i]
                 for i in range(len(particija)) if duljine[i] > 0])

        b = sum([min([self.config.dist_cs(particija[i][x1], particija[i][x2])
                      for x1 in range(len(particija[i]))
                      for x2 in range(len(particija[i]))
                      if x1 != x2])
                 for i in range(len(particija)) if duljine[i] > 1])

        return b / (a + 0.000001)

    def fitness(self, particija=[]):
        if self.config.fitness_metoda == 'cs':
            return self.fitness_cs(particija)
        else:
            return self.fitness_db(particija)


class Populacija:

    def __init__(self, config):
        self.config = config
        self.trenutna_generacija = []
        for t in range(config.velicina_populacije):
            self.trenutna_generacija.append(Kromosom(config))

    def probni_vektor(self, k, t):
        fiksirani = self.trenutna_generacija.pop(k)
        izabrani = random.sample(self.trenutna_generacija, 3)
        m, i, j = izabrani[0], izabrani[1], izabrani[2]
        assert isinstance(i, Kromosom)
        self.trenutna_generacija.insert(k, fiksirani) # vracamo privremeno izbaceni element k
        if random.random() < self.config.crossover_rate(t):
            return Kromosom(self.config, np.add(m.geni, np.multiply(self.config.scale_factor(), np.subtract(i.geni, j.geni))))
        else:
            return fiksirani

    def evoluiraj(self, t):
        iduca_generacija = []
        for kr in range(self.config.velicina_populacije):
            dobrost = self.trenutna_generacija[kr].fitness()
            probni_vek = self.probni_vektor(kr, t)
            dobrost_alt = probni_vek.fitness()
            iduca_generacija.append(self.trenutna_generacija[kr] if dobrost > dobrost_alt else probni_vek)

        self.trenutna_generacija = iduca_generacija

if __name__ == '__main__':
    c = Core(Config(Iris()))
    c.start()