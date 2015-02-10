# from core import Config

class log:
    def __init__(self):
        self.colormaps = []
        self.measures = []
        self.loc = "tmp"
        self.head = "none"

        # rand; shared info; homogeneity; completeness; v_measure_score; fitness; [4 rezervirano]
        self.info_cols_len = 10

        # vidi load za poredak
        self.head_as_array = None


    def load(self, location = None):
        self.loc = location or self.loc
        f = open(self.loc, "r")
        self.head = f.readline().strip()
        self.head_as_array = self.head.split(';')

        for columns in [raw.strip().split(';') for raw in f.readlines() if raw.strip() != ""]:
            #print int(columns[0:-self.info_cols_len][0])
            #print columns[-self.info_cols_len:]
            self.colormaps.append([int(col.strip().replace(',', '.')) for col in columns[0:-self.info_cols_len]])
            self.measures.append([float(col.strip().replace(',', '.')) for col in columns[-self.info_cols_len:]])

    def set_file(self, location):
        self.loc = location

    def set_info_cols_len(self, n):
        self.info_cols_len = n

    def set_header(self, confs):
        self.head = str(confs.k_max) + ';' + str(confs.weights_on) + ';' + str(confs.trajanje_svijeta) + ';' + \
                    str(confs.fitness_metoda) + ';' + str(confs.dist_metoda) + ';' + str(confs.db_param_q) + ';' + \
                    str(confs.db_param_t)

    def flush(self, location = None):
        self.loc = location or self.loc
        f = open(self.loc, "w")
        f.write(self.head.replace('.', ',') + '\n')
        for cols in zip(self.colormaps, self.measures):
            f.write(';'.join([str(x).replace('.', ',') for x in cols[0]]) + ';' + \
                    ';'.join([str(x).replace('.', ',') for x in cols[1]]) + '\n')
        f.close()


    def push_colormap(self, map):
        self.colormaps.append(map)

    def push_measures(self, ms):
        for x in range(self.info_cols_len-len(ms)):
            ms.append(0)
        self.measures.append(ms)

def test():
    l = log()
    l.set_info_cols_len(2)
    l.load("proba_csv")
    l.push_colormap([3, 2, 1, 0])
    l.push_measures([999])
    l.flush()

    print l.head_as_array
    print l.colormaps
    print l.measures
