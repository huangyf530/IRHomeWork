# IRHomeWork

Big homework for Information Retrieval.

## Dependency

+ Python: 3.7
+ Flask: 1.1.1
+ Elasticsearch: 7.1.0
+ Elasticsearch-full: 7.5

## How To RUN?

1. Start elasticsearch server

```shell
/usr/local/bin/elasticsearch
```

2. Edit config

edit `config.py`

```python
maps # index setting
files_to_handle # source file of corpus. Be preprocessed by thulac
```

3. Build index

```shell
python3 build_index.py
```

4. Run application

After build index, run application

**WARN:** Use the same index name in `app.py` and `build_index.py`

```shell
python3 app.py
```

Then open http://localhost:5000 in your browser. You can see following page.

<img src="./report/mainPage.png" alt="main page" style="zoom:50%;" />

5. (Optional) Build word vector

   build word vector to optimize result

   + Use `word2vec.py` to get word vector

   ```shell
   python3 word2vec.py
   --iter: 迭代轮数,int
   --max_doc：使用多少句子,int OR None
   --mode：train/count/test中的一个,str
   --model：存放词向量的路径,str
   --doc_print：每隔多少个句子输出一次,int
   --min_cnt：训练词向量时的最小词频,int
   --workers：多线程中使用多少个线程,int
   --step_store：每隔多少步存储一次词向量,int
   ```