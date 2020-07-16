
import json
import os
import math
from collections import defaultdict
import pkuseg
import time

PAGE_DATA_DIRECTORY = "../data/"

LENGTH_ALPHA = 0.114514

class SearchIndex:
    def __init__(self, data_directory):
        self.index = defaultdict(list)
        self.idf = {}
        self.pageStorage = []
        self.data_dir = data_directory
        self.pageMap = []
        self.pageNum = 0
        self.tokenizer = pkuseg.pkuseg(model_name = 'medicine')

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
        filenum = len([lists for lists in os.listdir(self.data_dir)])
        print(filenum, "file(s) found in data directory")
        self.pageNum = filenum
        for fileid in range(filenum):
            self.processFile(self.data_dir + str(fileid) + ".json", fileid)
        print("TF Done.")
        # Calculate IDF for each term
        for key in self.index:
            self.idf[key] = math.log(filenum / len(self.index[key]))
        print("IDF Done.")
        # Calculate TF-IDF for each (term, doc)
        for fileid in range(filenum):
            # curtfidf = {}
            length = 0.0
            for term in self.pageMap[fileid]:
                val = self.idf[term] * (1 + math.log(self.pageMap[fileid][term]))
                # curtfidf[term] = val
                length += val * val
            # self.tfidf.append(curtfidf)
            self.pageStorage[fileid]['wlength'] = math.sqrt(length)
        print("All done")

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
            #  ????
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
            ])
        return search_result


    def query(self, keyword, res_length):
        t1 = time.time()
        keywords = self.tokenizer.cut(keyword)
        # print(keywords)
        return self.search(keywords, res_length)
        # print("Time Elapsed:", time.time() - t1)



def main():
    print("Building Index...")
    tim0 = time.time()
    idx = SearchIndex(PAGE_DATA_DIRECTORY)
    idx.build()
    tim1 = time.time()
    print("Initialization complete, time elapsed:", tim1 - tim0)
    with open("search_test.txt", "r") as f:
        txt = f.readlines()
        for word in txt:
            print(idx.query(word.strip(), 20))

SrcEng = SearchIndex(PAGE_DATA_DIRECTORY)
SrcEng.build()

# main()