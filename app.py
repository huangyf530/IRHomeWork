from flask import Flask
from flask import render_template
from flask import request
from build_index import SearchEngine
from config import files_to_handle
from util import count_words, get_pos_explain

se = SearchEngine(index_name='search-index')
app = Flask(__name__)
pos2chin, pos2show, pos_list = get_pos_explain()
pos2show['w'] = False
pos2show['x'] = False
pos_info = {'pos2chin': pos2chin, 'pos2show': pos2show, 'pos': pos_list, 'length': len(pos_list)}

@app.route('/', methods=['GET', 'POST'])
@app.route('/search', methods=['GET', 'POST'])
def index(name=None):
    keyWord = None
    pageNum = 0
    if request.method =='POST':
        keyWord = request.form['keyword']
        poses = request.form.getlist('poses')
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
        number, result = se.query(keyWords, size=10000)
        print("Got {} Hits.".format(number))
        to_show = count_words(result, keyWords, windowsize=windowSize, poses_set=set(poses))
        for item in to_show:
            try:
                item['pos'] = pos2chin[item['pos']]
            except KeyError as e:
                item['pos'] = item['pos']
        initial_info = {'query': keyWord, 'window': request.form['window'], 'poses': poses}
        return render_template('search.html', info=initial_info, ans=to_show, pos_info=pos_info)
    return render_template('search.html', pos_info=pos_info)

if __name__ == '__main__':
    app.run()