import re
import random
from math import fabs
from JRecInterface import JRecInterface

iteration = 100
num_exp = 100
rand = random.Random()

def sim_one(p):
    res = []
    interface = JRecInterface()
    for iter in range(iteration):
        interface.request()
        if rand.random() <= p:
            interface.response(True)
        else:
            interface.response(False)
        res.append(interface.recommender.num_colored())
    return res

######################################################################################################################
ps = [0.1, 0.3, 0.5, 0.7, 0.9]
for p in ps:
    r = []
    for i in xrange(num_exp):
        r.append(sim_one(p))
    r = [float(sum(r[i][iter] for i in xrange(num_exp))) / num_exp for iter in xrange(iteration)]
    print r