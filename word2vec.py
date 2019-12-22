from gensim.models import Word2Vec
from gensim.models import KeyedVectors
from gensim.test.utils import datapath
from gensim.models.callbacks import CallbackAny2Vec
from config import files_to_handle
import argparse
import re
from datetime import datetime
import os

MAX_DOUBLE = 1e10
def str2bool(v):
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Unsupported value encountered.')

def intOrNone(v):
    try:
        return int(v)
    except ValueError as e:
        if v is None:
            return None
        else:
            raise argparse.ArgumentTypeError('Unsupported value encountered.')

def init_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--max_doc', type=intOrNone, default=None, 
                        help='Max number of document.')
    parser.add_argument('--mode', type=str, default='train',
                        help='The mode to instrcut code running. Must be count/train')
    parser.add_argument('--model', type=str, default='wordvec',
                        help='A trained word vector model path.')
    parser.add_argument('--iter', type=int, default=50,
                        help='Train epoch.')
    parser.add_argument('--doc_print', type=int, default=2000000, help='Print every X doc.')
    parser.add_argument('--workers', type=int, default=4, help='Workers to run word2vector.')
    parser.add_argument('--min_cnt', type=int, default=5, help='Minimum count of word that be computed.')
    parser.add_argument('--step_store', type=int, default=10, help='Store word vectors after X epoch.')
    return parser

def get_words(txt):
    matchObj = re.match(r'(.+)/(.+)$', txt)
    return matchObj.group(1)

class MyCorpus(object):
    def __init__(self, input_file_names, doc_print, max_doc=None):
        self.input_file_names = input_file_names
        self.doc_print = doc_print
        self.max_doc = max_doc

    
    def __iter__(self):
        """Returns a list of a list of words. Each sublist is a sentence."""
        sentence_words = []
        doc_num = 0
        for file_name in self.input_file_names:
            if doc_num == self.max_doc:
                break
            print("{}\tRead words from {}".format(str(datetime.now()), file_name))
            for line in open(file_name):
                line = line.strip()
                if line == '':
                    continue
                doc_num += 1
                # sent_words = filter(lambda w: w.split('/')[-1] != 'w', line.split())
                sent_words = line.split()
                sent_words = map(get_words, sent_words)
                words = []
                for word in sent_words:
                    words.append(word)
                if doc_num % self.doc_print == 0:
                    print('{}\tRead doc number is {}'.format(str(datetime.now()), doc_num))
                yield words
                if doc_num == self.max_doc:
                    break
        print('{}\tTotal read doc number is {}'.format(str(datetime.now()), doc_num))

class callback(CallbackAny2Vec):
    '''Callback to print loss after each epoch.'''
    def __init__(self, step_store, model_path):
        self.epoch = 0
        self.loss_to_be_subed = 0
        self.loss = []
        self.step_store = step_store
        self.best_loss = MAX_DOUBLE
        self.best_epoch = None
        self.model_path = model_path

    def on_epoch_end(self, model):
        loss = model.get_latest_training_loss()
        loss_now = loss - self.loss_to_be_subed
        if loss_now < self.best_loss:
            self.best_epoch = self.epoch
            self.best_loss = loss_now
            if self.epoch >= 30:
                model.wv.save_word2vec_format(os.path.join(self.model_path, 'word2vec.txt'), binary=False)
        self.loss_to_be_subed = loss
        self.loss.append(loss_now)
        self.epoch += 1
        print('{}\tLoss after epoch {}: {}'.format(str(datetime.now()), self.epoch, loss_now))
        print('\t\t\t\tMinimum Loss: {}, best epoch: {}'.format(self.best_loss, self.best_epoch))
        if self.epoch % self.step_store == 0:
            model.wv.save_word2vec_format(os.path.join(self.model_path, '{}_word2vec.txt'.format(self.epoch)),
                                          binary=False)

def train(file_names, model_path, iter, doc_print, workers, min_count, step_store, max_doc=None):
    myCorpus = MyCorpus(file_names, doc_print, max_doc)
    myCallback = callback(step_store, model_path)
    if not os.path.exists(model_path):
        os.mkdir(model_path)
    model = Word2Vec(myCorpus, size=128, window=5, min_count=min_count, workers=workers, iter=iter,
                     compute_loss=True, callbacks=[myCallback])
    # model.wv.save_word2vec_format(model_path, binary=False)
    wv = model.wv
    del model
    # plt.figure(figsize=[6, 6])
    # plt.title('Loss Curve')
    # plt.plot(myCallback.loss)
    # plt.savefig('./image/loss_curve.png', dpi=300)
    return wv

def count(file_names, doc_print, min_count, max_doc=None):
    myCorpus = MyCorpus(file_names, doc_print, max_doc)
    words_set = dict()
    for words in myCorpus:
        for word in words:
            try:
                words_set[word] += 1
            except KeyError as e:
                words_set[word] = 1
    count = 0
    for key in words_set:
        if words_set[key] >= min_count:
            count += 1
    return count

def analogy(x1, x2, y1, wv):
    ''' Calculate x2 - x1 + y1, like Japanese - Japan + France '''
    result = wv.most_similar(positive=[y1, x2], negative=[x1])
    print('{} - {} + {} = {}\t Similarity is {}'.format(x2, x1, y1, result[0][0], result[0][1]))
    return result

def test(model):
    wv = KeyedVectors.load_word2vec_format(model, binary=False)
    print(wv.most_similar('牛市'))

if __name__=='__main__':
    parser = init_parser()
    args = parser.parse_args()
    wv = None
    if args.mode == 'train':
        wv = train(files_to_handle, args.model, args.iter, args.doc_print, args.workers, args.min_cnt, args.step_store, args.max_doc)
    elif args.mode == 'count':
        print("Total Word Number is {}.".format(count(files_to_handle, args.doc_print, args.min_cnt, args.max_doc)))
    elif args.mode == 'test':
        test(args.model)
    else:
        raise ValueError('Mode must be one of count/train')


