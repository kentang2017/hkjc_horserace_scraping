# -*- coding: utf-8 -*-
"""
Created on Thu Jul 30 08:30:35 2020

@author: Ken Tang
@email: kinyeah@gmail.com
"""
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
import shlex
import pandas as pd
import datetime

chrome_options = Options()
chrome_options.add_argument("--headless")
browser = webdriver.Chrome(chrome_options=chrome_options)
url = 'https://racing.hkjc.com/racing/info/meeting/Results/Chinese/Local/'
browser.get(url)

# -*- coding: utf-8 -*-
"""
Created on Thu Jul 30 08:30:35 2020
@author: Ken Tang
@email: kinyeah@gmail.com
"""
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
import shlex
import pandas as pd
import datetime

chrome_options = Options()
chrome_options.add_argument("--headless")
browser = webdriver.Chrome(chrome_options=chrome_options)
url = 'https://racing.hkjc.com/racing/info/meeting/Results/Chinese/Local/'
browser.get(url)

class Getresult():
    def __init__(self, date):
        self.date = date
        
        
    def getracedate(self):
        #racedate = [shlex.split(str(datetime.datetime.strptime(i, '%d/%m/%Y')))[0].replace("-", "") for i in shlex.split(browser.find_element_by_xpath(".//html/body/div").text)[4:-300]]
        racedate = shlex.split(browser.find_element_by_xpath(".//html/body/div").text)[4:]
        datelist = [str(x) for x in racedate if len(x) == 10 and x.count("/") == 2]
        return [shlex.split(str(datetime.datetime.strptime(g, '%d/%m/%Y')))[0].replace("-", "") for g in datelist]

    def testfindrace(self, racecourse, raceno):
        url = 'https://racing.hkjc.com/racing/info/meeting/Results/Chinese/Local/'+self.date+"/"+racecourse+"/"+str(raceno)
        browser.get(url)
        return browser.find_element_by_xpath(".//html/body/div").text

    def findsinglerace(self, racecourse, raceno):
        raw_no = self.testfindrace(racecourse, raceno).index("第")
        return self.testfindrace(racecourse, raceno)[raw_no:]

    def findraces(self, racecourse):
        racenum = []
        for i in range(0, 18):
            url = 'https://racing.hkjc.com/racing/info/meeting/Results/Chinese/Local/'+self.date+"/"+racecourse+"/"+str(i)
            browser.get(url)
            if racecourse == "HV":
                content = (browser.find_element_by_xpath(".//html/body/div").text[9029:]).replace("\n", " ")
                racenum.append(content)
            elif racecourse == "ST":
                content = (browser.find_element_by_xpath(".//html/body/div").text[9031:]).replace("\n", " ")
                racenum.append(content)
        race_num = [x for x in racenum if len(x) > 281]
        return list(set(race_num))

    def findraces2(self,  racecourse):
        racenum = []
        for i in range(0, 18):
            url = 'https://racing.hkjc.com/racing/info/meeting/Results/Chinese/Local/'+self.date+"/"+racecourse+"/"+str(i)
            browser.get(url)
            if racecourse == "HV":
                content = (browser.find_element_by_xpath(".//html/body/div").text[9029:]).replace("\n", " ")
                if content[0] != "第":
                    content = (browser.find_element_by_xpath(".//html/body/div").text[9029:]).replace("\n", " ")
                racenum.append(content)
            elif racecourse == "ST":
                content = (browser.find_element_by_xpath(".//html/body/div").text[9026:]).replace("\n", " ")
                if content[0] == "第":
                    content2 = content
                elif content[0] != "第" or content[0] == " ":
                    content2 = browser.find_element_by_xpath(".//html/body/div").text[9025:].replace("\n", " ")
                    if content2[0]  == "場":
                        content2 = browser.find_element_by_xpath(".//html/body/div").text[9024:].replace("\n", " ")
                racenum.append(content2)
        race_num = [x for x in racenum if len(x) > 283 or len(x) > 283]
        return list(set(race_num))

    def daymatchresults(self):
        if self.date[0:4] == "2020":
            if len(self.findraces("HV")) > len(self.findraces("ST")):
                data = self.findraces("HV")
            elif len(self.findraces("HV")) < len(self.findraces("ST")):
                data = self.findraces("ST")
        elif self.date[0:4] != "2020":
            try:
                data = self.findraces2("HV")
            except IndexError:
                data = self.findraces2("ST")
        matches = []
        for r in data:
            horsedata = shlex.split(str(r)[str(r).index("賠率"):str(r).index("備註")])[2:]
            raceno = r[:r.index("場")].strip().replace("第", "").replace("場", "")
            b = [x for x in horsedata if len(x) > 7][0:4]
            c = [horsedata[horsedata.index(horse)-1] for horse in b][0:4]
            d = []
            for i in range(0,4):
                g = "("+c[i]+") "+b[i]
                d.append(g)
            try:
                horse_nn = {str(raceno):d}
                matches.append(horse_nn)
            except ValueError:
                pass
        return pd.concat([pd.DataFrame(matches[i], index=["第一名", "第二名", "第三名", "第四名"]).transpose() for i in range(0, len(matches))]).sort_index(ascending=True)

    def getdayraceresult(self, racecourse):
        rlist = []
        for r in range(1,12):
            try:
                a = [i.split(" ") for i in Getresult(self.date).findsinglerace(racecourse, r).split("\n")][10:][0::3]
                g = list(filter(lambda a: len(a) == 9, a))
                rlist.append(g)
            except ValueError:
                pass
        index = ["名次", " 馬號", "馬名", "騎師", "練馬師", "實際負磅", "體重", "檔位", "頭馬距離"]
        data = []
        for i in range(0, len(rlist)):
            d = pd.DataFrame(rlist[i],columns=index)
            data.append(d)
        return data
    
    def gettable(self):
        overall = len( Getresult(self.date).getdayraceresult(racecourse))
        index = ["名次", " 馬號", "馬名", "騎師", "練馬師", "實際負磅", "體重", "檔位", "頭馬距離"]
        data = []
        for i in range(0, len(overall)):
            d = pd.DataFrame(overall[i],columns=index)
            data.append(d)
        return data
    
    def daymatchresults2(self, racecourse):
        data = []
        for i in range(0,15):
            try:
                d = self.findsinglerace(racecourse, i)
                data.append(d)
            except ValueError:
                pass
        matches = []
        for r in data:
            horsedata = shlex.split(str(r)[str(r).index("賠率"):str(r).index("備註")])[2:]
            raceno = r[:r.index("場")].strip().replace("第", "").replace("場", "")
            b = [x for x in horsedata if len(x) > 7][0:4]
            c = [horsedata[horsedata.index(horse)-1] for horse in b][0:4]
            d = []
            for i in range(0,4):
                g = "("+c[i]+") "+b[i]
                d.append(g)
            try:
                horse_nn = {str(raceno).replace(" ", ""):d}
                matches.append(horse_nn)
            except ValueError:
                pass
        return pd.concat([pd.DataFrame(matches[i], index=["第一名", "第二名", "第三名", "第四名"]).transpose() for i in range(0, len(matches))]).sort_index(ascending=True)

    def getallresults(self):
        datelist = self.getracedate()[1:]
        alldata = []
        for i in datelist:
            try:
                data = {i:self.daymatchresults(i).transpose().to_dict()}
                alldata.append(data)
            except (ValueError, UnboundLocalError):
                pass
        return alldata

    def getdayresult(self):
        try:
            result = {self.date:self.daymatchresults2("HV").transpose().to_dict()}
        except (ValueError, NoSuchElementException):
             result = {self.date:self.daymatchresults2("ST").transpose().to_dict()}
        return result
    
    def getdayresult2(self):
        try:
            result = {self.date:self.getdayraceresult("HV")}
        except (ValueError, NoSuchElementException):
             result = {self.date:self.getdayraceresult("ST")}
        return result
    

if __name__ == '__main__':
    print(Getresult("20200624").getdayresult2())
