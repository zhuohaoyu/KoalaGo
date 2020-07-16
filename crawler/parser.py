# !/usr/bin/python3
# _*_ coding: utf-8 _*_

from bs4 import BeautifulSoup, Comment
# import hanlp
import pkuseg
import json
import time



DATA_DIR = "./data/"
# Location for raw data

FILEMAP_DIR = "./filemap"
# Location for filemap

OUTPUT_DIR = "./data_norm/"
# Location for output Files

BLACKLISTED_STRINGS = [
    "您所在的位置", "分享到：", "公众微信二维码", "Copyright ©", "版权所有", "北京市海淀区中关村大街59号", "邮编：100872", 
    "技术支持：", "传真：", "浏览量",
    "color:" , "text-decoration:"
]




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
        self.title = soup.head.title.text
        resultStrings = []
        for i in text:
            istr = i.strip()
            if "发布时间：" in istr:
                self.time = istr
            elif len(istr) > 1 and self.stringAllowed(istr):
                resultStrings.append(istr)
        self.plainText = resultStrings
        for res in resultStrings:
            self.processed.append(self.tokenizer.cut(res))
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
    print("Initializing...")
    time1 = time.time()
    # tokenizer = hanlp.load('PKU_NAME_MERGED_SIX_MONTHS_CONVSEG')
    tokenizer = pkuseg.pkuseg(model_name = 'medicine')
    print("Initialized, Time Elapsed:", time.time() - time1)
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
                    rp.dump()
                    validfileid = validfileid + 1
            except FileNotFoundError:
                print("[BAD] File", fileid, "doesn't exist.")
            else:
                print("[OK] #{id}  Time={tim:.2f}s, {pgs:.2f}Page/Sec".format(id = fileid, tim = time.time() - time2, pgs = (fileid + 1) / (time.time() - time2)))
            fileid = fileid + 1
    
main()