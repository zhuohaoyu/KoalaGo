# !/usr/bin/python3
# _*_ coding: utf-8 _*_

from bs4 import BeautifulSoup, Comment
# import hanlp
import pkuseg
import json
import time
import jieba

USER_DICT = '../my_dict.txt'
"""
print("[INFO] Loading jieba")
jieba.enable_paddle()
jieba.load_userdict(USER_DICT)
print("[INFO] Jieba loaded")
"""
print("[INFO] Loading LAC")
from LAC import LAC
lac = LAC(mode = 'seg')
lac.load_customization(USER_DICT, sep = '\n')
print("[INFO] LAC Loaded")

DATA_DIR = "./data/"
# Location for raw data

FILEMAP_DIR = "./filemap"
# Location for filemap

OUTPUT_DIR = "../data/"
# Location for output Files

BLACKLISTED_STRINGS = [
    "您所在的位置", "分享到：", "公众微信二维码", "Copyright ©", "版权所有", "北京市海淀区中关村大街59号", "邮编：100872", 
    "技术支持：", "传真：", "浏览量",
    "color:" , "text-decoration:"
]

STOP_WORDS = set()

titleSet = set()

def getStopwordsList():
    global STOP_WORDS
    with open("cn_stopwords.txt", "r") as f:
        # STOP_WORDS = [line.strip() for line in f.readlines()]
        for line in f.readlines():
            STOP_WORDS.add(line.strip('\n'))

class RawHTMLParser:
    def __init__(self, content, tokenizer, fileid, validfileid, fileurl):
        self.content = content
        self.tokenizer = tokenizer
        self.fileid = fileid
        self.title = ""
        self.time = ""
        self.url = fileurl
        self.oldID = fileid
        self.newID = validfileid
        self.plainText = []
        self.processed = []
    
    def stringAllowed(self, st):
        for blk in BLACKLISTED_STRINGS:
            if blk in st:
                return False
        return True



    def parseHTML(self):
        soup = BeautifulSoup(self.content, 'html.parser')

        # Binary files, Non-html files
        if soup.body == None:
            return []
        
        # Skip listing pages
        if self.url.find("_list.php") != -1:
            return []

        # Remove all scripts
        for sc in soup.select('script'):
            sc.extract()

        # Remove all links
        for sc in soup.select('a'):
            sc.extract()
        
        # Remove all comments
        for sc in soup(text=lambda text: isinstance(text, Comment)):
            sc.extract()
        findres = soup.find("div", {"id": "main"})

        # Binary files, Non-html files
        if soup.body == None:
            return []

        # Find text & output
        text = soup.body.find_all(text = True)
        self.title = soup.head.title.text.replace(' - 中国人民大学信息学院', '')
        resultStrings = []
        # title_processed = self.tokenizer.cut(self.title.strip())
        title_processed = lac.run(self.title.strip())
        for word in title_processed:
            if word not in STOP_WORDS:
                self.processed.append(word)
        for i in text:
            istr = i.strip()
            if "发布时间：" in istr:
                self.time = istr
            elif len(istr) > 1 and self.stringAllowed(istr):
                resultStrings.append(istr)
        self.plainText = resultStrings
        self.time = self.time.replace('发布时间：', '')
        """
        for res in resultStrings:
            curres = self.tokenizer.cut(res)
            # curres = jieba.lcut_for_search(res)
            for word in curres:
                if word not in STOP_WORDS:
                    self.processed.append(word)
        """
        if len(resultStrings) == 0:
            return
        cutall = lac.run(resultStrings)
        for cutres in cutall:
            for curword in cutres:
                cs = curword.strip()
                if cs not in STOP_WORDS:
                    self.processed.append(cs)
        # """
        # self.processed = self.tokenizer.cut(resultStrings)
        # print(self.title, self.time, self.plainText)


    def dump(self):
        with open(OUTPUT_DIR + str(self.newID) + ".json", "w") as f:
            djson = json.dumps({
                "url": self.url,
                "id": self.newID,
                "title":self.title,
                "time": self.time, 
                "text": self.plainText, 
                "words":self.processed
                })
            f.write(djson)



def main():
    print("[INFO] Loading pkuseg")
    time1 = time.time()
    tokenizer = pkuseg.pkuseg(model_name = 'medicine', user_dict=USER_DICT)
    getStopwordsList()
    print("[INFO] pkuseg initialized", time.time() - time1)
    time2 = time.time()


    with open(FILEMAP_DIR, "r") as fmp:
        filemap = fmp.readlines()
        fileid = 0
        validfileid = 0
        for i in filemap:
            try:
                with open(DATA_DIR + str(fileid), "r") as fpage:
                    cont = fpage.read()
                    rp = RawHTMLParser(cont, tokenizer, fileid, validfileid, i.strip())
                    rp.parseHTML()
                    cur_text = ""
                    for word in rp.plainText:
                        wst = word.strip()
                        if ("来源" not in wst) and ("作者" not in wst) and ("您所在的位置" not in wst) and ("新闻类型" not in wst) and ("浏览量" not in wst):
                            cur_text += word.strip()
                    rp.token = hash(cur_text)
                    if rp.token in titleSet:
                        print("[BAD] File", fileid, "is duplicated.")
                    if len(rp.plainText) > 0 and rp.token not in titleSet:
                        rp.dump()
                        titleSet.add(rp.token)
                        validfileid = validfileid + 1
            except FileNotFoundError:
                pass
                print("[BAD] File", fileid, "doesn't exist.")
            else:
                pass
                print("[OK] #{id}  Time={tim:.2f}s, {pgs:.2f}Page/Sec".format(id = fileid, tim = time.time() - time2, pgs = (fileid + 1) / (time.time() - time2)))
            fileid = fileid + 1
    
main()