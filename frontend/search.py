
import json
import os
import math
from collections import defaultdict
import pkuseg
import time


SrcEng = None

# Location for dictionary file
USER_DICT = "my_dict.txt"

# Location for dumped index file
INDEX_DIR = "search_index.json"

# Location for parsed pages
PAGE_DATA_DIRECTORY = "../data/"

# A constant affecting accuracy
LENGTH_ALPHA = 0.33

# Length of snippet generated for user
SNIPPET_LENGTH = 150

# Location for stopwords
STOP_WORDS_DIR = "../crawler/cn_stopwords.txt"

"""
# LAC
print("[INFO] Loading LAC")
from LAC import LAC
lac = LAC(mode = 'seg')
lac.load_customization(USER_DICT, sep = '\n')
print("[INFO] LAC Loaded")

# jieba
print("[INFO] Loading jieba")
jieba.enable_paddle()
# jieba.load_userdict(USER_DICT)
print("[INFO] Jieba loaded")
"""

time_before_run = time.time()

print("[INFO] Loading pkuseg")
tokenizer = pkuseg.pkuseg(model_name = 'medicine', user_dict= USER_DICT)
print("[INFO] pkuseg loaded.")

STOP_WORDS = []


def getStopwordsList():
    global STOP_WORDS
    with open(STOP_WORDS_DIR, "r") as f:
        STOP_WORDS = [line.strip() for line in f.readlines()]


class SearchIndex:
    def __init__(self, data_directory):
        self.index = defaultdict(list)
        self.pageStorage = []
        self.data_dir = data_directory
        self.pageMap = []
        self.pageNum = 0


    def dumpjson(self):
        print("[INFO] Dumping data to ", INDEX_DIR)
        out = {}
        out["index"] = self.index
        out["pageStorage"] = self.pageStorage
        out["pageNum"] = self.pageNum
        with open(INDEX_DIR, "w") as f:
            strout = json.dumps(out)
            f.write(strout)
        print("[INFO] Data dumped to json.")


    def loadjson(self):
        print("[INFO] Loading data from ", INDEX_DIR)
        with open(INDEX_DIR, "r") as f:
            data = json.loads(f.read())
            self.index = data["index"]
            self.pageStorage = data["pageStorage"]
            self.pageNum = data["pageNum"]
            print("[INFO] Data loaded from json.")


    def processFile(self, data_file, fileid):
        data = {}
        with open(data_file, "r") as f:
            data_str = f.read()
            data = json.loads(data_str)
        self.pageStorage.append({
            'url' : data['url'],
            'title' : data['title'],
            'time' : data['time'],
            'text' : data['text']
        })
        curdict = defaultdict(int)
        for word in data['words']:
            curdict[word] += 1
        self.pageMap.append(curdict)
        for key in curdict:
            # Calculate TF for each (term, doc)
            self.index[key].append([fileid, 1 + math.log(curdict[key])]) # id, tf(key, curdoc)


    def build(self):
        cidf = {}
        filenum = len([lists for lists in os.listdir(self.data_dir)])
        print("[INFO] ",filenum, "file(s) found in data directory")
        self.pageNum = filenum
        for fileid in range(filenum):
            self.processFile(self.data_dir + str(fileid) + ".json", fileid)
        # Calculate IDF for each term
        for key in self.index:
            cidf[key] = math.log(filenum / len(self.index[key]))
        # Calculate TF-IDF for each (term, doc)
        for fileid in range(filenum):
            # curtfidf = {}
            length = 0.0
            for term in self.pageMap[fileid]:
                val = cidf[term] * (1 + math.log(self.pageMap[fileid][term]))
                # curtfidf[term] = val
                length += val * val
            # self.tfidf.append(curtfidf)
            self.pageStorage[fileid]['wlength'] = math.sqrt(length)


    def search(self, keywords, res_length):
        score = [0.0] * self.pageNum
        for keyword in keywords:
            if keyword not in self.index:
                continue
            cnt = 0
            for k2 in keywords:
                if k2 == keyword:
                    cnt += 1
            wtq = 1 + math.log(cnt)
            for pair in self.index[keyword]:
                score[pair[0]] += pair[1] * wtq
        
        result_unsorted = []

        for fileid in range(self.pageNum):
            global LENGTH_ALPHA
            score[fileid] /= self.pageStorage[fileid]['wlength'] ** LENGTH_ALPHA
            if(score[fileid] > 0) :
                result_unsorted.append((score[fileid], fileid))
        
        result_sorted = sorted(result_unsorted, key = lambda s: s[0], reverse = True)

        search_result = []
        for i in range(min(len(result_sorted), res_length)):
            search_result.append([
                self.pageStorage[result_sorted[i][1]]['title'], 
                self.pageStorage[result_sorted[i][1]]['url'],
                self.pageStorage[result_sorted[i][1]]['time'],
                result_sorted[i][1]
            ])
        return search_result


    def query(self, keyword, res_length):
        keywords_raw = tokenizer.cut(keyword)
        keywords = []
        for keyword in keywords_raw:
            if keyword not in STOP_WORDS:
                keywords.append(keyword)
        # keywords = [keys for keys in keywords not in STOP_WORDS]
        rawSearch = self.search(keywords, res_length)
        searchResult = []
        
        for res in rawSearch:
            cont = self.pageStorage[res[3]]['text']
            cont_str = ""
            min_res = 1000000000
            for sentence in cont:
                cont_str += sentence.strip()
            for word in keywords:
                pos = cont_str.find(word)
                if min_res > pos:
                    min_res = pos
            if min_res == 1000000000:
                min_res = 0
            min_res -= 10
            if min_res < 0:
                min_res = 0
            if min_res == 0:
                summary = cont_str[min_res: min_res + SNIPPET_LENGTH]
            else:
                summary = '<small class=\"text-muted\">……</small>' + cont_str[min_res: min_res + SNIPPET_LENGTH]
            
            for word in keywords:
                summary = summary.replace(word, "<mark>" + word + "</mark>")
            if len(summary) == 0:
                summary = "<p><small class=\"text-muted\">Summary Not Available.</small></p>"
            elif len(cont_str) < min_res + SNIPPET_LENGTH:
                summary += '<small class=\"text-muted\">……</small>'
            if len(res[2]) == 0:
                res[2] = "Time not available."
            searchResult.append([res[0], res[1], res[2], summary])
        return searchResult
        # print("Time Elapsed:", time.time() - t1)


    def query_raw(self, keyword, res_length):
        # keywords = jieba.lcut_for_search(keyword, HMM = True)
        keywords_raw = tokenizer.cut(keyword)
        keywords = []
        for keyword in keywords_raw:
            if keyword not in STOP_WORDS:
                keywords.append(keyword)
        # keywords = lac.run(keyword)
        # keywords = jieba.lcut(keyword, HMM = True, use_paddle = True)
        return self.search(keywords, res_length)


def main():
    global SrcEng
    print("[INFO] Building Index for TF-IDF.")
    SrcEng = SearchIndex(PAGE_DATA_DIRECTORY)
    SrcEng.build()
    print("[INFO] Initialization of TF-IDF completed.")
    getStopwordsList()
    print("[INFO] Time elapsed:", time.time() - time_before_run)


def build_dump():
    global SrcEng
    print("[INFO] Building Index for TF-IDF.")
    SrcEng = SearchIndex(PAGE_DATA_DIRECTORY)
    SrcEng.build()
    print("[INFO] Initialization of TF-IDF completed.")
    SrcEng.dumpjson()
    getStopwordsList()
    print("[INFO] Time elapsed:", time.time() - time_before_run)

def build_load():
    global SrcEng
    SrcEng = SearchIndex(PAGE_DATA_DIRECTORY)
    SrcEng.loadjson()
    getStopwordsList()
    print("[INFO] Time elapsed:", time.time() - time_before_run)

build_load()
