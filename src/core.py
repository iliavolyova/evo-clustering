'''
nepreciznosti u clanku:
   - rjesenje za less than 2
   - dist metrika i za db i za cs
   - koji je tocno postupak za kromosome kod kojih postoji aktivni centar s manje od dvije pridruzene tocke
        7. str pod D - jedini siguran nacin koji vidim na koji se to moze rijesiti zahtjeva rjesavanje
        cijelog clustering problema
        osim u interpretaciji da jedna tocka moze pripadati vise clustera, sto nadam se nije trazeno
   - kad govore o centrima, misle li na artim (ili druge) sredine grupe u particiji ili koordinate u genima
'''
from __future__ import division

import numpy as np
import random
import math
import matplotlib.pyplot as plt
from scipy import spatial


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

tocke = [[t[0], t[1]] for t in tocke]


class Config:
    def __init__(self):
        self.n_dims = 2  # dimenzija podataka
        self.k_max = 5   # max klastera
        self.velicina_populacije = 10
        self.trajanje_svijeta = 50
        self.fitness_metoda = 'cs'
        self.db_param_q = 2
        self.db_param_t = 2

    def dist2d(self, a, b):
        return math.sqrt((a[0] - b[0])**2 + (a[1] - b[1])**2)

    def dist_db(self, a, b):  # TODO: treba ovisi o necemu, ali nije jasno cemu
        return np.power(self.dist2d(a, b), self.db_param_q)

    def dist(self, a, b):
        return self.dist2d(a, b)

    def crossover_rate(self, t): # t jer se vremenom spusta
        return 0.5 + 0.5 * (self.trajanje_svijeta - t) / self.trajanje_svijeta

    def scale_factor(self):
        return 0.5 + random.random() *0.5

class Core:
    def __init__(self):
        self.config = Config()
        # normalizira sve feature na [0, 1], na potencijalno glup i opasan nacin
        for dim in range(self.config.n_dims):
            min_d, max_d = min([t[dim] for t in tocke]), max([t[dim] for t in tocke])
            for t in tocke:
                t[dim] -= min_d
                t[dim] /= (max_d - min_d)

    def start(self):
        p = Populacija(self.config)
        plt.show(False)

        for i in range(self.config.trajanje_svijeta):
            p.evoluiraj(i)
            print(i, '/', self.config.trajanje_svijeta, "\t")

            najkrom = np.argmax([kr.fitness() for kr in p.trenutna_generacija])
            grupiranje = p.trenutna_generacija[najkrom].pridruzivanje()

            if i % 6 == 0:
                plt.clf()
                plt.xlim(0, 100)
                plt.ylim(0, 100)
                for klasa in grupiranje:
                    plt.plot([t[0] * 100 for t in klasa], [t[1] * 100 for t in klasa], 'o', markersize=12 , color=(random.random(), random.random(), random.random()))


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


        #while 1:
            # sve odavde do kraja funkcije problematicno
            aktivnih = self.aktivnih_centara()
            if aktivnih < 2:
                for ispravak in random.sample(range(config.k_max), 2):
                    self.geni[ispravak] = 0.5 + 0.5 * random.random()

            '''
            particija = self.pridruzivanje()
            particija_neprazno = [p for p in particija if p != []]
            svi_ok = all([len(grupa) >= 2 for grupa in particija])
            if not svi_ok:
                #privremeno - randomizirati problematicne
                for igrupa, grupa in enumerate(particija_neprazno):
                    if self.geni[igrupa] > 0.5 and len(grupa) < 2:
                        self.geni[k_max + n_dims * igrupa:k_max + n_dims * (igrupa+1)] = [rand() for x in range(n_dims)]
            else:
                break

            # jos jedno privremeno rjesenje - ugasiti sve problematicne
            # problem s njim - moze uzrokovat da imamo manje od 2 aktinve grupe
            #
            #for igrupa, grupa in enumerate(particija):
            #    if len(grupa) < 2:
            #        self.geni[igrupa] *= -1

            pocetak impl. njihove ideje koja mi se cini besmislenom

            If so, the cluster center positions
            of this special chromosome are reinitialized by an average
            computation. We put n/K data points for every individual
            cluster center, such that a data point goes with a center that is
            nearest to it

            tocaka = len(tocke)
            po_grupi = tocaka // aktivnih
            ostaci = tocaka % aktivnih
            prva_iduca_tocka = 0
            for grupa in range(k_max):
                if self.geni[grupa] > 0.5:
                    krajnja = prva_iduca_tocka + po_grupi + (ostaci > 0)
                    centar = np.average(grupa[prva_iduca_tocka:krajnja])
                    prva_iduca_tocka = krajnja
                    ostaci -= 1
                    self.geni[k_max + n_dims * grupa:k_max + n_dims * grupa+n_dims] = centar
            '''

        if len(self.geni) != config.k_max + config.k_max * config.n_dims:
            print("probl")

    def aktivni_centri(self):
        return [[self.geni[self.config.k_max + self.config.n_dims * i + dim] for dim in range(self.config.n_dims)]
                for i in range(self.config.k_max) if self.geni[i] > 0.5]

    def aktivnih_centara(self):
        return len(self.aktivni_centri())

    def pridruzivanje(self):
        p = []
        centri = self.aktivni_centri()
        p = [[] for c in centri]
        for t in tocke:
            najbl = np.argmin([self.config.dist(c, t) for c in centri])
            p[najbl].append(t)
        #return [x for x in p if x != []]
        return p

    def fitness_db(self, particija=[]):
        if not particija:
           particija = self.pridruzivanje()

        particija = [x for x in particija if x != []]

        K = len(particija)
        duljine = [len(grupa) for grupa in particija]

        centri = [np.average(grupa, axis=0) for grupa in particija]

        #rasprsenja
        S = [math.pow(sum([self.config.dist_db(t, centri[igrupa]) for t in grupa]) / len(grupa),
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
        if not particija:
            particija = self.pridruzivanje()

        K = len(particija)
        duljine = [len(p) for p in particija]
        a = sum([sum([max([self.config.dist(particija[i][x1], particija[i][x2])
                          for x2 in range(len(particija[i]))])
                     for x1 in range(len(particija[i]))]) / duljine[i]
                 for i in range(len(particija)) if duljine[i] > 0])

        b = sum([min([self.config.dist(particija[i][x1], particija[i][x2])
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
    trenutna_generacija = []

    def __init__(self, config):
        self.config = config
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
        for kromy in range(self.config.velicina_populacije):
            dobrost = self.trenutna_generacija[kromy].fitness()
            probni_vek = self.probni_vektor(kromy, t)
            dobrost_alt = probni_vek.fitness()
            iduca_generacija.append(self.trenutna_generacija[kromy] if dobrost > dobrost_alt else probni_vek)

        self.trenutna_generacija = iduca_generacija

if __name__ == '__main__':
    c = Core()
    c.start()