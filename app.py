from flask import Flask
from flask import render_template
from flask import request
from build_index import SearchEngine
from config import files_to_handle
from util import count_words, get_pos_explain
from word2vec import get_similar_word, load_wordvector

se = SearchEngine(index_name='search-index')
app = Flask(__name__)
pos2chin, pos2show, pos_list = get_pos_explain()
pos2show['w'] = False
pos2show['x'] = False
pos_info = {'pos2chin': pos2chin, 'pos2show': pos2show, 'pos': pos_list, 'length': len(pos_list)}
fuzzy_search = True
wv = None

def transfer_checkbox(value):
    return value is not None

def get_more_query(wv, keyWords, results, keywords_list):
    similar_words = get_similar_word(keyWords[0], wv)
    print(similar_words)
    words = []
    sims = []
    number = 0
    for word, score in similar_words:
        if score > 0.64:
            words.append(word)
            sims.append(score)
    for sim_word in words:
        temp_keywords = keyWords.copy()
        temp_keywords[0] = sim_word
        temp_num, temp_result = se.query(temp_keywords, size=5000)
        results.append(temp_result)
        keywords_list.append(temp_keywords)
        number += temp_num
    return words, sims, number

@app.route('/', methods=['GET', 'POST'])
@app.route('/search', methods=['GET', 'POST'])
def index(name=None):
    keyWord = None
    pageNum = 0
    fuzzy_search = True
    if request.method =='POST':
        keyWord = request.form['keyword']
        poses = request.form.getlist('poses')
        fuzzy_search = transfer_checkbox(request.form.get('fuzzy'))
        for key in pos2show:
            pos2show[key] = False
        for select_pos in poses:
            pos2show[select_pos] = True
        try:
            windowSize = int(request.form['window'])
        except ValueError as e:
            windowSize = 5
        keyWords = keyWord.split(' ')
        print("Query: {}".format(keyWord))
        results = []
        keywords_list = []
        number, result = se.query(keyWords, size=5000)
        results.append(result)
        keywords_list.append(keyWords)
        if fuzzy_search:
            words, sims, temp_number = get_more_query(wv, keyWords, results, keywords_list)
            number += temp_number
        print("Got {} Hits.".format(number))
        to_show = count_words(results, keywords_list, windowsize=windowSize, poses_set=set(poses))
        for item in to_show:
            try:
                item['pos'] = pos2chin[item['pos']]
            except KeyError as e:
                item['pos'] = item['pos']
        initial_info = {'query': keyWord, 'window': request.form['window'], 'poses': poses}
        if fuzzy_search:
            if len(words) == 0:
                sim_words = "没有找到意思相近的词语"
            else:
                sim_words = '关联的词语：{}'.format(' '.join(words)) 
            return render_template('search.html', info=initial_info, ans=to_show, pos_info=pos_info, \
                                    fuzzy=fuzzy_search, sim_words=sim_words)
        else:
            return render_template('search.html', info=initial_info, ans=to_show, pos_info=pos_info, \
                                    fuzzy=fuzzy_search)
    return render_template('search.html', pos_info=pos_info, fuzzy=fuzzy_search)

if __name__ == '__main__':
    wv = load_wordvector('wordvec')
    app.run()