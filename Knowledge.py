import Utl
import copy
import random
import Japanese

from collections import Counter as mset


class Process:
    # Accept list[int] as input data
    def __init__(self, id, data):
        self.id = id
        self.uniq_id = -1

        #########################################################################

        # FILTER:

        # self.data = data[:]  # Grammar+Vocabulary
        self.data = [d for d in data if d >= 10000]  # Vocabulary Only
        #self.data = [d for d in data if d < 10000]   # Grammar    Only
        #########################################################################

        self.sentence = ""
        self.sorted_data = sorted(self.data)
        self.concept = set(self.data)

    def easier(self, that):
        if len(self.data) > len(that.data):
            return False
        p1 = self.sorted_data
        p2 = that.sorted_data
        i = 0
        j = 0
        while i < len(p1):
            while j < len(p2) and p1[i] != p2[j]:
                j += 1
            if j >= len(p2):
                break
            i += 1
            j += 1
        if i < len(p1):
            return False
        else:
            return True

    def fuzzy_easier(self, that, fuzzy, concept_weight = None):
        if len(self.data) > len(that.data):
            return False
        p1 = self.sorted_data
        p2 = that.sorted_data
        if len(self.data) == len(that.data):
            if p1 == p2:
                return True
            else:
                return False
        intersection =  list((mset(p1) & mset(p2)).elements())

        if concept_weight == None:
            # all concepts are treated equally
            n_intersection = len(intersection)
            n_p1 = len(p1)
        else:
            # some concepts are promoted
            #n_intersection = len(intersection) + sum(-0.3 for c in intersection if concept_weight[c] < 0.01 * len(concept_weight))
            #n_p1 = len(p1) + sum(-0.3 for c in p1 if concept_weight[c] < 0.01 * len(concept_weight))
            n_intersection = sum(concept_weight[c] for c in intersection)
            n_p1 = sum(concept_weight[c] for c in p1)

        #Case Study
        #if 0.68 * n_p1 <= n_intersection and 0.72 * n_p1 >= n_intersection:
        #    print self.sentence
        #    print that.sentence
        #    print

        if fuzzy * n_p1 <= n_intersection:
            return True
        else:
            return False



# End Process

# Not ready for fuzzy
class KnowledgeBoundary:
    ReInforcement = 0
    ReCombination = 1
    NewKnowledge = 2

    def __init__(self, knowledge):
        self.Concepts = set([])
        self.Processes = set([])
        self.Knowledge = knowledge
        self.ConceptStatus = [False] * len(knowledge.UniqueConcepts)
        self.ProcessStatus = [False] * len(knowledge.UniqueProcesses)

    def __add1__(self, process):
        classification = self.classify(process)
        if classification == KnowledgeBoundary.NewKnowledge:
            for c in process.concept - self.Concepts:
                self.ConceptStatus[self.Knowledge.UniqueConcepts.index(c)] = True
            self.Concepts |= process.concept
        # Remove all processes on the knowledge boundary that is easier than current one
        if classification in (KnowledgeBoundary.ReCombination, KnowledgeBoundary.NewKnowledge):
            self.Processes -= {p for p in self.Processes if p.easier(process)}
            self.Processes |= {process}
            for i in range(len(self.ProcessStatus)):
                if not self.ProcessStatus[i]:
                    if self.Knowledge.easier_graph[self.Knowledge.UniqueProcesses[i].id][process.id]:
                        self.ProcessStatus[i] = True

        # 3% possibility of self check
        if random.random() < 0.05:
            if not self.check():
                print "Knowledge Boundary Check Failed!"

    # Simulate add(process), but does not change self
    # return size of the knowledge after adding
    def increment(self, process):
        return sum([self.ProcessStatus[up.uniq_id] or self.Knowledge.easier_graph[up.id][process.id]
                   for up in self.Knowledge.UniqueProcesses])

    def classify(self, process):
        for p in self.Processes:
            if process.easier(p):
                return KnowledgeBoundary.ReInforcement
        if process.concept - self.Concepts == set([]):
            return KnowledgeBoundary.ReCombination
        else:
            return KnowledgeBoundary.NewKnowledge

    # Add one or more processes to the knowledge boundary
    def add(self, data):
        if type(data) == list:
            for p in data:
                self.__add1__(p)
        else:
            self.__add1__(data)

    def process_in(self, process):
        for p in self.Processes:
            if process.easier(p):
                return True
        return False

    # Check
    def check(self):
        for c in self.Concepts:
            if not self.ConceptStatus[self.Knowledge.UniqueConcepts.index(c)]:
                return False
        for i in range(len(self.ProcessStatus)):
            if self.ProcessStatus[i] != self.process_in(self.Knowledge.UniqueProcesses[i]):
                return False
        return True


class Knowledge:


    # Read data from input
    # input can be either a string meaning the name of the input file
    #                  or a doc_id:article dict
    # First line of the file indicates the lesson_size
    # Data in format of capital letters (char=True) or integers (char=False)
    # Blank line is recognized as an empty process with no concepts
    # Assume data is valid
    def __init__(self, input, fuzzy = 1.0, char=False):

        # Read Knowledge

        if type(input) == str:
            #
            input_filename = input

            # GV: Grammar + Vocabulary
            try:
                f = open('KnowledgeGV/' + input_filename + '.txt')
                #f = open('Knowledge/' + input_filename + '.txt')
            except IOError:
                f = open('JPEDU/KnowledgeGV/' + input_filename + '.txt')
                #f = open('JPEDU/Knowledge/' + input_filename + '.txt')

            first_line = True
            self.data = []
            for line in f:
                if first_line:  # read lesson_size
                    self.input_lesson_size = [int(s) for s in Utl.split(line, ' \n')]
                    if len(self.input_lesson_size) == 1:  # fixed lesson size
                        self.input_lesson_size = self.input_lesson_size[0]
                    first_line = False
                else:  # read data
                    if char:
                        self.data.append(Process(len(self.data), [ord(c) - ord('A') for c in line[:-1]]))
                    else:
                        self.data.append(Process(len(self.data), [int(s) for s in Utl.split(line, ' \n')]))
            f.close()

            # Read Sentences
            if char:
                try:
                    f = open('Knowledge/' + input_filename + '.txt')
                except IOError:
                    f = open('JPEDU/Knowledge/' + input_filename + '.txt')
                i = 0
                first = True
                for line in f:
                    if first:
                        first = False
                        continue
                    self.data[i].sentence = line[:-1]
                    i += 1
                if i != len(self.data):
                    print 'Knowledge and Sentence not match!'
                f.close()
            else:
                try:
                    f = open('Sentence/' + input_filename + '.txt')
                except IOError:
                    f = open('JPEDU/Sentence/' + input_filename + '.txt')
                i = 0
                for line in f:
                    self.data[i].sentence = line[:-1]
                    i += 1
                if i != len(self.data):
                    print 'Knowledge and Sentence not match!'
                f.close()


        elif type(input) == dict:
            #
            articles = input
            self.data = []

            all_uniq_wl = []
            for article in articles.values():
                all_uniq_wl += article.uniq_wordlist
            all_uniq_wl = list(set(all_uniq_wl))
            word_index = {all_uniq_wl[i]:i + 10000 for i in range(len(all_uniq_wl))}

            for article in articles.values():
                # Sentence Only
                if article.doc_id.find("_s") == -1:
                    continue
                p = Process(len(self.data), [word_index[w] for w in article.wordlist])
                #########################################################################
                #########################################################################
                # TODO: Here process with no concept will be dropped.
                # TODO: This might not be good forever.
                #########################################################################
                #########################################################################
                if len(p.data) == 0:
                    continue
                self.data.append(p)
                self.data[-1].sentence = article.text

        ############################
        # Concepts
        self.UniqueConcepts = set([])
        for p in self.data:
            self.UniqueConcepts |= p.concept
        self.UniqueConcepts = sorted(list(self.UniqueConcepts))
        self.UniqueConceptsIndex = {self.UniqueConcepts[i]:i for i in range(len(self.UniqueConcepts))}

        self.ConceptNum = {}
        for p in self.data:
            for c in p.data:
                if self.ConceptNum.has_key(c):
                    self.ConceptNum[c] += 1
                else:
                    self.ConceptNum[c] = 1
        t = sorted(self.ConceptNum.iteritems(), key=lambda d: d[1], reverse=True)
        t = [i[0] for i in t]
        self.ConceptNumRank = {t[i]:i for i in range(len(t))}

        ###############################
        ###############################
        ###############################
        indexed_stoplist = [word_index[w] for w in Japanese.downweighting_stoplist if w in word_index.keys()]
        self.ConceptWeight = {}
        for i in range(len(t)):
            #if i < 0.01 * len(t):
            if t[i] in indexed_stoplist:
                self.ConceptWeight[t[i]] = 0
            else:
                self.ConceptWeight[t[i]] = 1


        ###############################
        ###############################
        ###############################
        # Easier Graph
        self.easier_graph = []

        if fuzzy == 1.0:
            for i in range(len(self.data)):
                self.easier_graph.append([self.data[i].easier(self.data[j]) for j in range(len(self.data))])
        else:
            for i in range(len(self.data)):
                self.easier_graph.append([self.data[i].fuzzy_easier(self.data[j], fuzzy, self.ConceptWeight) for j in range(len(self.data))])
                if i%10 == 0:
                    print i

        self.eq = range(len(self.data))
        for i in range(len(self.data)):
            for j in range(i):
                if self.easier_graph[i][j] and self.easier_graph[j][i]:
                    self.eq[i] = j
                    break

        ############################
        # Process
        self.UniqueProcesses = [self.data[i] for i in range(len(self.data)) if i == self.eq[i]]
        for i in range(len(self.UniqueProcesses)):
            self.UniqueProcesses[i].uniq_id = i
        for i in range(len(self.data)):
            self.data[i].uniq_id = self.data[self.eq[i]].uniq_id

        # Init Random
        random.seed()
    # __init__

    def num(self):
        return len(self.data)

    def uniq_num(self):
        return len(self.UniqueProcesses)

    def id_easier(self, id1, id2):
        return self.easier_graph[id1][id2]

    def uniq_id_easier(self, uniq_id1, uniq_id2):
        return self.easier_graph[self.UniqueProcesses[uniq_id1].id][self.UniqueProcesses[uniq_id2].id]

    def EdgeNum(self):
        cnt = 0.0
        for p in self.UniqueProcesses:
            for q in self.UniqueProcesses:
                #if p != q:
                if p.id != q.id and len(p.data) != 0:
                    cnt += self.easier_graph[p.id][q.id]
                    if self.easier_graph[p.id][q.id]:
                        print int(cnt)
                        print p.sentence
                        print q.sentence
        return cnt


    def ProcessConceptPerSentence(self, seq, lesson_size=0):
        if lesson_size == 0:  # default lesson_size
            lesson_size = self.input_lesson_size
        status = [[0, 0, 0]]
        kb = KnowledgeBoundary(self)
        p = 0

        for i in range(len(lesson_size)):
            for j in range(p, lesson_size[i]):
                kb.add(self.data[seq[j]])
            # Update Knowledge Boundary
            status.append([lesson_size[i], sum(kb.ProcessStatus), sum(kb.ConceptStatus)])
            p = lesson_size[i]

        for p in status:
            print p[0], p[1], p[2]
        return status

    # Evaluate the RC/NK proportion of a sequence of processes based on lesson_size
    def proportion(self, seq, lesson_size=0):
        if lesson_size == 0:  # default lesson_size
            lesson_size = self.input_lesson_size
        stats = []
        kb = KnowledgeBoundary(self)
        p = 0

        for i in range(len(lesson_size)):
            l = [0, 0, 0]
            for j in range(p, lesson_size[i]):
                l[kb.classify(self.data[seq[j]])] += 1
            stats.append([float(k) / (lesson_size[i] - p) for k in l])
            for j in range(p, lesson_size[i]):
                kb.add(self.data[seq[j]])
            p = lesson_size[i]

        #Careful!!!!!
        stats = [stats, float(sum(kb.ProcessStatus))]


        return stats


    def proportion_pace(self, seq):
        p = self.proportion(seq, range(1, len(seq) + 1) )
        ri = float(sum([q[0] for q in p[0]]))
        rc = float(sum([q[1] for q in p[0]]))
        nk = float(sum([q[2] for q in p[0]]))
        if ri + rc + nk != len(seq):
            print "Proportion Sum Wrong!"
        return [float(p[1]), ri/float(len(seq)), nk/float(len(seq))]



    # Evaluate the process/concept progress of a sequence of processes based on lesson_size
    def progress(self, seq, lesson_size=0):
        if lesson_size == 0:  # default lesson_size
            lesson_size = self.input_lesson_size
        status = [[0, 0, 0]]
        kb = KnowledgeBoundary(self)
        p = 0

        for i in range(len(lesson_size)):
            for j in range(p, lesson_size[i]):
                kb.add(self.data[seq[j]])
            # Update Knowledge Boundary
            status.append([0, float(sum(kb.ProcessStatus)) / len(kb.ProcessStatus),
                          float(sum(kb.ConceptStatus)) / len(kb.ConceptStatus)])
            p = lesson_size[i]

        return status

    # Calculate the squared error of the pacing with regret to functions f_rc, f_nk, both [0,1]->[0,1]
    # lesson_size can be a fixed number, or a list of numbers indicating the index of lesson ends
    def squared_error(self, seq, f_rc, f_nk, lesson_size=0):
        if lesson_size == 0:  # default lesson_size
            lesson_size = self.input_lesson_size

        # fixed lesson_size
        if type(lesson_size) == int:
            lesson_size = [i * lesson_size for i in range(1, len(seq) / lesson_size + 1)]
            if lesson_size[-1] < len(seq):
                lesson_size.append(len(seq))

        if len(lesson_size) <= 1:
            print "Too few lessons!"
            return 0

        # TODO
        # Select which function to evaluate: proportion or progress
        stats = self.progress(seq, lesson_size)
        for l in stats:
            print l[1], l[2]

        error = 0
        for i in range(0, len(lesson_size)):
            x = float(lesson_size[i]) / len(seq)
            error += (f_rc(x) - stats[i][KnowledgeBoundary.ReCombination]) ** 2 \
                     #+ \
                     #(f_nk(x) - stats[i][KnowledgeBoundary.NewKnowledge]) ** 2
        error /= len(stats) - 1
        return error

    ##################################################################################################
    ##################################################################################################
    #
    # Progression Strategies
    #
    ##################################################################################################
    ##################################################################################################

    # Trivial BFS for topsort
    def bfs(self):
        a = copy.deepcopy(self.easier_graph)
        for i in range(self.num()):
            for j in range(i, self.num()):
                if a[i][j] and a[j][i]:  # Equal
                    a[i][j] = False
                    a[j][i] = False
        d = [sum([a[j][i] for j in range(self.num())]) for i in range(self.num())]
        queue = [i for i in range(self.num()) if d[i] == 0]
        seq = []
        while len(queue) > 0:
            p = queue[0]
            queue = queue[1:]
            seq.append(p)
            for i in range(self.num()):
                if a[p][i]:
                    a[p][i] = False
                    d[i] -= 1
                    if d[i] == 0:
                        queue.append(i)

        # test
        flag = True
        for i in range(self.num()):
            for j in range(i + 1, self.num()):
                if self.data[seq[j]].easier(self.data[seq[i]]) and not self.data[seq[i]].easier(self.data[seq[j]]):
                    flag = False
        if not flag:
            print "Wrong BFS!"

        return seq

    # Greedy select `next problem' one by one by minimizing the difference from the perfect gradual
    def greedy1_gradual(self):
        kb = KnowledgeBoundary(self)
        n = self.num()
        nUniqueConcepts = len(self.UniqueConcepts)
        nUniqueProcesses = len(self.UniqueProcesses)
        seq = [0] * n
        dif_process = [99999999] * n
        dif_concept = [99999999] * n
        dif_combine = [99999999] * n
        in_seq = [False] * n
        for current in range(n):
            progress_process = float(nUniqueProcesses) * current / n
            #progress_concept = float(nUniqueConcepts)  * current / n
            for up in self.UniqueProcesses:
                dif_process[up.id] = abs(progress_process - kb.increment(up))
                #dif_concept[up.id] = abs(progress_concept -
                    #(len(kb.Concepts) + sum([not kb.ConceptStatus[self.UniqueConcepts.index(c)] for c in up.concept])))
            for i in range(n):
                dif_process[i] = dif_process[self.eq[i]]
                dif_concept[i] = dif_concept[self.eq[i]]
            for i in range(n):
                if in_seq[i]:
                    dif_combine[i] = 99999999
                else:
                    dif_combine[i] = dif_process[i] + dif_concept[i]
            min_dif = min(dif_combine)
            candidate = [i for i in range(n) if dif_combine[i] == min_dif]
            seq[current] = random.choice(candidate)
            in_seq[seq[current]] = True
            kb.add(self.data[seq[current]])
        return seq


    def greedy_dis(self, num, fea):
        kb = KnowledgeBoundary(self)
        n = self.num()
        seq = []
        while(len(seq) < num):
            dis = [9999999] * n
            #for i in seq:
            #    dis[i] = 88888888
            for i in range(n):
                if dis[i] != 88888888:
                    seq.append(i)
                    f1 = self.proportion_pace(seq)
                    f1[0] = float(f1[0]) / len(seq)
                    dis[i] = 0.01*(f1[0]-fea[0])*(f1[0]-fea[0])+(f1[1]-fea[1])*(f1[1]-fea[1])+(f1[2]-fea[2])*(f1[2]-fea[2])
                    seq = seq[:-1]
            min_dis = min(dis)
            candidate = [i for i in range(n) if (dis[i] - min_dis) * (dis[i] - min_dis) < 1e-8]
            seq.append(random.choice(candidate))
        return seq

    def greedys(self, num, fea):
        best_dis = 9999999
        for i in range(100):
            seq = self.greedy_dis(num, fea)
            f1 = self.proportion_pace(seq)
            f1[0] = float(f1[0]) / len(seq)
            dis = 0.01*(f1[0]-fea[0])*(f1[0]-fea[0])+(f1[1]-fea[1])*(f1[1]-fea[1])+(f1[2]-fea[2])*(f1[2]-fea[2])
            if dis < best_dis:
                best_dis = dis
                best_seq = seq
        return seq

