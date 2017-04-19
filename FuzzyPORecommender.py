#!/usr/bin/python
# -*- coding: UTF-8 -*-

from JRecRequest import JRecRequest
from random import *
from Knowledge import *
from collections import Counter
import json

FuzzyPORecommender_Version = 20170406

PSEODO_COUNT = 1.1

class FuzzyPORecommender:
    def __init__(self, articles, json_str = None):
        self.articles = articles
        self.knowledge = Knowledge(articles, 0.8)
        self.N = len(self.knowledge.data)
        self.random = Random()

    ##########################################################
    ## Serialized Part
        if json_str != None:
            _l = json.loads(json_str)
        else:
            _l = []
        if len(_l) != 4:
        # if json_str == None or l[0] != FuzzyPORecommender_Version
            self.version = FuzzyPORecommender_Version
            self.request_history = []
            self.response_history = []
            self.color = [-1] * self.N  # -1 for unknown, or [0,1]
        else:
            self.version = _l[0]
            self.request_history = _l[1]
            self.response_history = _l[2]
            self.color = _l[3]

        ##########################################################
        ## Aux Part
        #self.easiers = [set([j for j in xrange(self.N) if self.knowledge.easier_graph[j][i] and i != j]) for i in xrange(self.N)]
        #self.harders = [set([j for j in xrange(self.N) if self.knowledge.easier_graph[i][j] and i != j]) for i in xrange(self.N)]

    def json_str(self):
        return json.dumps([self.version, self.request_history, self.response_history, self.color])

    # Expected Gain (number of nodes that can be colored) after Asking one doc to the student
    def color_gain(self, id, alpha=1.0):
        color_easier = sum(1 for i in self.knowledge.easiers[id] if self.color[i] == -1)
        color_harder = sum(1 for i in self.knowledge.harders[id] if self.color[i] == -1)
        return 1 + color_easier + alpha * color_harder

    def assessment_request(self):
        response_history_stats = {0:0, 1:0}
        for i in range(self.N):
            if self.color[i] == 0 or self.color[i] == 1:
                response_history_stats[self.color[i]] += 1
        alpha = (PSEODO_COUNT + response_history_stats[0]) / (PSEODO_COUNT + response_history_stats[1])
        #alpha = 1.0
        color_gains = {id:self.color_gain(id, alpha) for id in range(self.N) if self.color[id] == -1}
        if len(color_gains) == 0:
            return None
        max_color_gain = max(color_gains.values())
        max_color_gain_ids = [id for id in color_gains.keys() if color_gains[id] == max_color_gain]
        self.random.shuffle(max_color_gain_ids)
        print max_color_gain, max_color_gain_ids[0]
        self.request_history.append(self.knowledge.data[max_color_gain_ids[0]].doc_id)

    def recommendation_request(self):
        #TODO Today
        for i in range(self.N):
            if self.color[i] == 1:
                return i

    def request(self):
        if len(self.response_history) < len(self.request_history):
            return JRecRequest(self.articles[self.request_history[-1]])
        response_history_stats = {0:0, 1:0}
        for i in range(self.N):
            if self.color[i] == 0 or self.color[i] == 1:
                response_history_stats[self.color[i]] += 1
        alpha = (PSEODO_COUNT + response_history_stats[0]) / (PSEODO_COUNT + response_history_stats[1])
        #alpha = 1.0
        color_gains = {id:self.color_gain(id, alpha) for id in range(self.N) if self.color[id] == -1}
        if len(color_gains) == 0:
            return None
        max_color_gain = max(color_gains.values())
        max_color_gain_ids = [id for id in color_gains.keys() if color_gains[id] == max_color_gain]
        self.random.shuffle(max_color_gain_ids)
        print max_color_gain, max_color_gain_ids[0]
        self.request_history.append(self.knowledge.data[max_color_gain_ids[0]].doc_id)
        return JRecRequest(self.articles[self.request_history[-1]])

    # Color one node and all related node(s)
    def color_node(self, id, res):
        if res == True:
            self.color[id] = 1
            for i in self.knowledge.easiers[id]:
                if self.color[i] == -1:
                    self.color[i] = 1
        elif res == False:
            self.color[id] = 0
            for i in self.knowledge.harders[id]:
                if self.color[i] == -1:
                    self.color[i] = 0

    def response(self, response):
        self.color_node(self.knowledge.doc_id_to_id[self.request_history[-1]], response.understood)
        self.response_history.append(response.understood)

    def num_colored(self):
        return sum(1 for i in range(self.N) if self.color[i] != -1)