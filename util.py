import numpy as np
import re

def get_pos_explain(explanation_file='pos_explaination.txt'):
    pos2chin = {}
    pos_list = []
    pos2show = {}
    with open(explanation_file, 'r') as f:
        for linenum, line in enumerate(f):
            line = line.strip()
            if line == '':
                continue
            line_content = line.split(' ')
            for item in line_content:
                matchObj = re.match(r'(.+)/(.+)$', item)
                pos2chin[matchObj.group(1)] = matchObj.group(2)
                pos_list.append(matchObj.group(1))
    for key in pos2chin:
        pos2show[key] = True
    return pos2chin, pos2show, pos_list



def check_index(words, poses, i, poses_set):
    return poses[i] in poses_set

def getSortKey(elem):
    return elem['tf']

def cal_tf(show_list, avgl, k=1.2, b=0.75):
    for item in show_list:
        item['tf'] = item['termFreq'] * (k + 1) / (item['termFreq'] + k * (1 - b + b * item['dis'] / avgl))


def count_words(results, keywords_list, windowsize=5, poses_set=set(['w'])):
    show_list = []
    words_freq = {}
    words_len = {}
    words_pos = {}
    key_words_set = set(keywords_list[0])
    for k in range(len(results)):
        result = results[k]
        keywords = keywords_list[k]
        for items in result:
            origin_words = items['_source']['text']
            origin_poses = items['_source']['poses']
            words = []
            for key in keywords:
                index_key = origin_words.index(key)
                start = max(0, index_key - windowsize)
                end = min(len(origin_words), index_key + windowsize + 1)
                ans_list = filter(lambda x: check_index(origin_words, origin_poses, x, poses_set), range(start, end))
                for i in ans_list:
                    if origin_words[i] not in key_words_set and i != index_key:
                        if origin_words[i] not in words_freq:
                            words_freq[origin_words[i]] = 0
                            words_len[origin_words[i]] = []
                            words_pos[origin_words[i]] = origin_poses[i]
                        words_freq[origin_words[i]] += 1
                        words_len[origin_words[i]].append(abs(index_key - i))
    for word, cnt in words_freq.items():
        show_list.append({'words': word, 'termFreq': cnt, 'dis': np.mean(words_len[word]), 'pos': words_pos[word]})
    cal_tf(show_list, windowsize)
    show_list.sort(key=getSortKey, reverse=True)
    return show_list
