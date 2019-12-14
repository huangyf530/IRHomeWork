from elasticsearch import Elasticsearch
from elasticsearch import client
from elasticsearch import helpers
from datetime import datetime
from config import maps, files_to_handle, query
from sys import getrefcount
import gc
import re

class SearchEngine:
    def __init__(self, files, wrong_log='wrong.log', sentence_log='sentence_id', index_name='search-index'):
        self.es = Elasticsearch()
        self.files = files
        self.wrong_log = wrong_log
        self.sentence_log = sentence_log
        self.sentenc_id = self.read_sentence_id()
        self.maps = maps
        self.index_name = index_name
    
    def delete_index(self, index_name):
        self.es.indices.delete(index=index_name, ignore=[400, 404])
        print('Delete index {} succesful!'.format(index_name))

    
    def read_sentence_id(self):
        try:
            with open(self.sentence_log, 'r') as f:
                return int(f.readline().strip())
        except FileNotFoundError as e:
            return 0
    
    def write_sentence_id(self):
        with open(self.sentence_log, 'w') as f:
            f.write('{}'.format(self.sentenc_id))
    
    def split_word_pos(self, word_poses):
        wrong_word = open(self.wrong_log, 'a')
        words = []
        poses = []
        for word in word_poses:
            matchObj = re.match(r'(.+)/(.+)$', word)
            try:
                words.append(matchObj.group(1))
                poses.append(matchObj.group(2))
            except AssertionError as e:
                wrong_word.write('{}\t{}\n'.format(self.sentenc_id, word))
        wrong_word.close()
        return words, poses
    
    def store_index(self, result):
        action = ({
                    "_index": self.index_name,
                    "_source": {
                        'text': row[0], 'poses': row[1]
                    },
                    "_id": row[2]
                } for row in result)
        helpers.bulk(self.es, action, index="index_new", raise_on_error=True)
        self.write_sentence_id()
    
    def read_source(self, file_name):
        result = []
        with open(file_name) as f:
            for linenum, line in enumerate(f):
                line = line.strip()
                if line == '':
                    continue
                line_content = line.split(' ')
                words, poses = self.split_word_pos(line_content)
                result.append([words, poses, self.sentenc_id])
                self.sentenc_id += 1
                if self.sentenc_id % 100000 == 0:
                    self.store_index(result)
                    del result
                    gc.collect()
                    result = []
                    print("Handle {} sentence!".format(self.sentenc_id))
                    
    
    def build_index(self):
        if not self.es.indices.exists(index=self.index_name):
            result = self.es.indices.create(index=self.index_name, ignore=[400, 404], body = self.maps)
            print('Create index {}.'.format(self.index_name))
        else:
            print('Find index {}. So don\'t create a new one.'.format(self.index_name))
        for file_name in self.files:
            self.read_source(file_name)
        print("Total sentence number is {}!".format(self.sentenc_id))
    
    def query(self, query):
        res = self.es.search(index=self.index_name, body=query, size=50)
        return res




if __name__=='__main__':
    indexCreater = SearchEngine(files_to_handle)
    # indexCreater.delete_index('search-index')
    indexCreater.build_index()
    # res = indexCreater.query(query)
    # print("Got %d Hits:" % res['hits']['total']['value'])
    # cnt = 0
    # for hit in res['hits']['hits']:
    #     print(cnt)
    #     print(hit["_source"])
    #     cnt += 1
    # res = es.search(index=index_name, body=query)
    # print("Got %d Hits:" % res['hits']['total']['value'])
    # print(res)

