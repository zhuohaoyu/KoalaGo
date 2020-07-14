# !/usr/bin/python3
# _*_ coding: utf-8 _*_

from bs4 import BeautifulSoup, Comment
import jieba


DATA_DIR = "./data/"
# Location for raw data

FILEMAP_DIR = "./filemap"
# Location for filemap

OUTPUT_DIR = "./data_norm/"
# Location for output Files

BLACKLISTED_STRINGS = [
    "您所在的位置", "分享到：", "公众微信二维码", "Copyright ©", "版权所有", "北京市海淀区中关村大街59号", "邮编：100872", 
    "技术支持：", "传真："
    "color:" , "text-decoration:"
]




class RawHTMLParser:
    def __init__(self, content):
        self.content = content
        self.plainText = []
    
    def stringAllowed(self, st):
        for blk in BLACKLISTED_STRINGS:
            if blk in st:
                return False
        return True



    def parseHTML(self):
        soup = BeautifulSoup(self.content, 'html.parser')

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

        # Find text & output
        text = soup.body.find_all(text = True)
        resultStrings = []
        for i in text:
            istr = i.strip()
            if len(istr) > 1 and self.stringAllowed(istr):
                resultStrings.append(istr)
        self.plainText = resultStrings
        print(resultStrings)





def main():


    with open("test.html", "r") as f:
        t = f.read()
        rp = RawHTMLParser(t)
        rp.parseHTML()
    
main()