import nltk
from difflib import get_close_matches

from collections import OrderedDict
import json
import os

INTERESETING_TAGS = ['PRP', 'VBG', 'NN', 'JJ', 'VB', 'NNP', 'CD', 'NNS', 'VBP', 'RB']

class Fact(object):
    def __init__(self, text, tags=None):
        self.text = text
        if tags is None:
            self.tagify()
        else:
            self.tags = tags

    def tagify(self):
        tokens = nltk.word_tokenize(self.text)
        tagged = nltk.pos_tag(tokens)

        #combine some tags
        tags = []
        tag_to_add = None
        last_tag = None
        i = 0
        while i < len(tagged):
            if tagged[i][1] in ['NN', 'NNP', 'CD']:
                if tagged[i][1] != last_tag:
                    if tag_to_add is not None:
                        tags.append(tag_to_add)
                        tag_to_add = None
                #and now add new word
                if tag_to_add is None:
                    tag_to_add = tagged[i][0]
                else:
                    tag_to_add = ' '.join([tag_to_add, tagged[i][0]])
            elif tagged[i][1] in INTERESETING_TAGS:
                tags.append(tagged[i][0])

            #reset last_tag
            last_tag = tagged[i][1]

            #increase the loop
            i += 1

        #add the remain tag_to_add
        if tag_to_add is not None:
            tags.append(tag_to_add)

        self.tags = tags

    def __repr__(self):
        return '%s -> %s' % (self.text, self.tags)

    def __eq__(self, other):
        cond1 = self.text == other.text
        cond2 = self.tags == other.tags
        return cond1 and cond2

    def to_json(self):
        return json.dumps([self.text, self.tags])

    @classmethod
    def from_json(cls, json_object):
        text, tags = json.loads(json_object)
        return cls(text, tags)

class TagsDatabase(object):
    def __init__(self, db_path=None):
        self.facts = []
        self.tags = {}
        self.db_path = db_path
        self.load_db()

    def __del__(self):
        self.save_db()

    def load_db(self):
        if self.db_path is not None and os.path.exists(self.db_path):
            facts_jsons, tags_json = json.load(file(self.db_path))
            self.facts = [Fact.from_json(x) for x in facts_jsons]
            self.tags = tags_json

    def save_db(self):
        if self.db_path is not None:
            facts_jsons = [x.to_json() for x in self.facts]
            data_to_json = [facts_jsons, self.tags]
            json.dump(data_to_json, file(self.db_path, 'wb'))

    def add_fact(self, fact):
        current_index = len(self.facts)
        if fact not in self.facts:
            self.facts.append(fact)
            for tag in fact.tags:
                if tag not in self.tags:
                    self.tags[tag] = []
                self.tags[tag].append(current_index)

    @staticmethod
    def compare_search_results(x, y):
        return len(x[1]) > len(y[1])

    def search(self, query):
        query_fact = Fact(query)
        #order by tags, the most having tags - the upper
        #the lesser - the lower
        #no tags - nothing to show
        result = {} #fact : [tags]
        for tag in query_fact.tags:
            # if tag == 'quickly':
                # import pdb; pdb.set_trace()
            possible_matches = get_close_matches(tag, self.tags.keys())
            for match_tag in possible_matches:
                if match_tag in self.tags:
                    for fact_index in self.tags[match_tag]:
                        fact = self.facts[fact_index]
                        if fact not in result:
                            result[fact] = []
                        result[fact].append(match_tag)

        ordered_result = OrderedDict(sorted(result.items(), cmp=self.__class__.compare_search_results))
        return ordered_result

def test():
    facts = ['For personal use, this module Bla Module will come very handy, and quickly you will see you got it right',
             'Stack Overflow is a community of 4.7 million programmers, just like you, helping each other',
             'I thought it looked interesting and might come in handy when I bake for the church',
             'The book is handy for quick reference',
             'Its just handy to have this thing',
             ]
    
    db = TagsDatabase()
    for f in facts:
        db.add_fact(Fact(f))

    #search
    res = db.search('handy and quickly')
    print res

if __name__ == '__main__':
    test()
