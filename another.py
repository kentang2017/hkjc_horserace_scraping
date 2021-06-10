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

columns = ["賽次","比賽日期", "開始時間", "名次","馬ID", "馬名", "馬歲數", "馬性別", "馬身顏色", "馬出生地", "馬父系", "馬母系", 
           "馬外祖父", "季初獎金", "總共獎金", "場地", "路途", "位置", "季初評分", "評分", "練馬師", "騎師", "頭馬距離", "賠率", 
           "賽際負磅", "沿途走位", "完成時間", "排位體重", "配備", "天馬", "日馬", "丁馬", "初傳", "中傳", "末傳", "神煞"]

url_list = ["https://racing.hkjc.com/racing/information/Chinese/Horse/SelectHorsebyChar.aspx?ordertype="+str(i) for i in [2,3,4]]
        
def gethorsename_from_url(url):
    browser.get(url)
    lt = []
    for y in range(1,200):
        try:
            c = [browser.find_element_by_xpath(".//html/body/div/p/table/tbody/tr[2]/td/table/tbody/tr["+str(y)+"]/td["+str(i)+"]/table/tbody/tr/td[1]/li").text for i in range(1,6)]
            lt.append(c)
        except NoSuchElementException:
            pass
    total = []
    for i in lt:
        total += i
    return total

def gethorsenames():
    total = []
    for i in [gethorsename_from_url(i) for i in url_list]:
        total += i
    return total

def gethorseid_from_url(url):
    browser.get(url)
    lt = []
    for y in range(1,200):
        try:
            c = [browser.find_element_by_xpath(".//html/body/div/p/table/tbody/tr[2]/td/table/tbody/tr["+str(y)+"]/td["+str(i)+"]/table/tbody/tr/td[1]/li").get_attribute('innerHTML')[62:74] for i in range(1,6)]
            lt.append(c)
        except NoSuchElementException:
            pass
    total = []
    for i in lt:
        total += i
    return total

def gethorseids():
    total = []
    for i in [gethorseid_from_url(i) for i in url_list]:
        total += i
    return total

def gethorse1():
    return dict(zip(gethorseids(), gethorsenames()))

def gethorse2():
    return dict(zip(gethorsenames(), gethorseids()))

d = gethorse2()

def gethorsedata(hid):
    url = "https://racing.hkjc.com/racing/information/Chinese/Horse/Horse.aspx?HorseId="+hid
    browser.get(url)
    dict1 = {"馬名":browser.find_element_by_xpath(".//html/body/div/div[1]/table[1]/tbody/tr/td[1]/table/tbody/tr[1]/td/span").text.replace(" ", "").split("(")[0], "馬號":browser.find_element_by_xpath(".//html/body/div/div[1]/table[1]/tbody/tr/td[1]/table/tbody/tr[1]/td/span").text.replace(" ", "").split("(")[1][:-1]}
    dict2 = dict(zip(["出生地", "馬歲數"],browser.find_element_by_xpath(".//html/body/div/div[1]/table[1]/tbody/tr/td[2]/table/tbody/tr[1]/td[3]").text.replace(" ", "").split("/")))
    dict3 = dict(zip(["馬毛色", "馬性別"],browser.find_element_by_xpath(".//html/body/div/div[1]/table[1]/tbody/tr/td[2]/table/tbody/tr[2]/td[3]").text.replace(" ", "").split("/")))
    dict4 = {"練馬師":browser.find_element_by_xpath(".//html/body/div/div[1]/table[1]/tbody/tr/td[3]/table/tbody/tr[1]/td[3]").text,
             "進口類別":browser.find_element_by_xpath(".//html/body/div/div[1]/table[1]/tbody/tr/td[2]/table/tbody/tr[3]/td[3]").text,
             "今季獎金":browser.find_element_by_xpath(".//html/body/div/div[1]/table[1]/tbody/tr/td[2]/table/tbody/tr[4]/td[3]").text,
             "總獎金":browser.find_element_by_xpath(".//html/body/div/div[1]/table[1]/tbody/tr/td[2]/table/tbody/tr[5]/td[3]").text,"冠亞季總出賽次數":browser.find_element_by_xpath(".//html/body/div/div[1]/table[1]/tbody/tr/td[2]/table/tbody/tr[6]/td[3]").text,
             "馬主":browser.find_element_by_xpath(".//html/body/div/div[1]/table[1]/tbody/tr/td[3]/table/tbody/tr[2]/td[3]").text,"現時評分":browser.find_element_by_xpath(".//html/body/div/div[1]/table[1]/tbody/tr/td[3]/table/tbody/tr[3]/td[3]").text, "季初評分":browser.find_element_by_xpath(".//html/body/div/div[1]/table[1]/tbody/tr/td[3]/table/tbody/tr[4]/td[3]").text, "馬父系":browser.find_element_by_xpath(".//html/body/div/div[1]/table[1]/tbody/tr/td[3]/table/tbody/tr[5]/td[3]").text, "馬母系":browser.find_element_by_xpath(".//html/body/div/div[1]/table[1]/tbody/tr/td[3]/table/tbody/tr[6]/td[3]").text, "馬外祖父":browser.find_element_by_xpath(".//html/body/div/div[1]/table[1]/tbody/tr/td[3]/table/tbody/tr[7]/td[3]").text,
            } 
    return {**dict1, **dict2, **dict3, **dict4} 

def gethorsedata(horsename):
    url = "https://racing.hkjc.com/racing/information/Chinese/Horse/Horse.aspx?HorseId="+gethorse2().get(horsename)
    browser.get(url)
    dict1 = {"馬名":browser.find_element_by_xpath(".//html/body/div/div[1]/table[1]/tbody/tr/td[1]/table/tbody/tr[1]/td/span").text.replace(" ", "").split("(")[0], "馬號":browser.find_element_by_xpath(".//html/body/div/div[1]/table[1]/tbody/tr/td[1]/table/tbody/tr[1]/td/span").text.replace(" ", "").split("(")[1][:-1]}
    dict2 = dict(zip(["出生地", "馬歲數"],browser.find_element_by_xpath(".//html/body/div/div[1]/table[1]/tbody/tr/td[2]/table/tbody/tr[1]/td[3]").text.replace(" ", "").split("/")))
    dict3 = dict(zip(["馬毛色", "馬性別"],browser.find_element_by_xpath(".//html/body/div/div[1]/table[1]/tbody/tr/td[2]/table/tbody/tr[2]/td[3]").text.replace(" ", "").split("/")))
    dict4 = {"練馬師":browser.find_element_by_xpath(".//html/body/div/div[1]/table[1]/tbody/tr/td[3]/table/tbody/tr[1]/td[3]").text,
             "進口類別":browser.find_element_by_xpath(".//html/body/div/div[1]/table[1]/tbody/tr/td[2]/table/tbody/tr[3]/td[3]").text,
             "今季獎金":browser.find_element_by_xpath(".//html/body/div/div[1]/table[1]/tbody/tr/td[2]/table/tbody/tr[4]/td[3]").text,
             "總獎金":browser.find_element_by_xpath(".//html/body/div/div[1]/table[1]/tbody/tr/td[2]/table/tbody/tr[5]/td[3]").text,"冠亞季總出賽次數":browser.find_element_by_xpath(".//html/body/div/div[1]/table[1]/tbody/tr/td[2]/table/tbody/tr[6]/td[3]").text,
             "馬主":browser.find_element_by_xpath(".//html/body/div/div[1]/table[1]/tbody/tr/td[3]/table/tbody/tr[2]/td[3]").text,"現時評分":browser.find_element_by_xpath(".//html/body/div/div[1]/table[1]/tbody/tr/td[3]/table/tbody/tr[3]/td[3]").text, "季初評分":browser.find_element_by_xpath(".//html/body/div/div[1]/table[1]/tbody/tr/td[3]/table/tbody/tr[4]/td[3]").text, "馬父系":browser.find_element_by_xpath(".//html/body/div/div[1]/table[1]/tbody/tr/td[3]/table/tbody/tr[5]/td[3]").text, "馬母系":browser.find_element_by_xpath(".//html/body/div/div[1]/table[1]/tbody/tr/td[3]/table/tbody/tr[6]/td[3]").text, "馬外祖父":browser.find_element_by_xpath(".//html/body/div/div[1]/table[1]/tbody/tr/td[3]/table/tbody/tr[7]/td[3]").text,
            } 
    
    
    return {**dict1, **dict2, **dict3, **dict4} 


class Getresult():
    def __init__(self, date):
        self.date = date
        
    def gethorsedatabase(self):
        url_list = ["https://racing.hkjc.com/racing/information/Chinese/Horse/SelectHorsebyChar.aspx?ordertype="+str(i) for i in [2,3,4]]
        
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
    
    def getdayresult3(self):
        try:
            data = self.getdayraceresult("HV")
            c = {}
            for i in range(0, len(data)):
                b = {i: data[i].to_dict()}
                c.update(b)
            result = {self.date: c}
        except (ValueError, NoSuchElementException):
            data = self.getdayraceresult("ST")
            c = {}
            for i in range(0, len(data)):
                b = {i: data[i].to_dict()}
                c.update(b)
            result = {self.date: c}
        return result


def getrow(date, racecourse, raceno):
    #2021/06/06
    url = "https://racing.hkjc.com/racing/information/Chinese/Racing/LocalResults.aspx?RaceDate="+date+"&Racecourse="+racecourse+"&RaceNo="+raceno
    browser.get(url)
    name = browser.find_element_by_xpath(".//html/body/div/div[5]/table/tbody/tr[1]/td[3]").text.split("(")[0]
    raceid = browser.find_element_by_xpath(".//html/body/div/div[4]/table/thead/tr/td[1]").text.split("(")[1].replace(")", "")
    horseid = browser.find_element_by_xpath(".//html/body/div/div[5]/table/tbody/tr[1]/td[3]").text.split("(")[1][:-1]
    ground_status  = browser.find_element_by_xpath(".//html/body/div/div[4]/table/tbody/tr[2]/td[3]").text
    horseid = browser.find_element_by_xpath(".//html/body/div/div[5]/table/tbody/tr[1]/td[3]").text.split("(")[1][:-1]
    racerank = browser.find_element_by_xpath(".//html/body/div/div[5]/table/tbody/tr[1]/td[1]").text
    horseno = browser.find_element_by_xpath(".//html/body/div/div[5]/table/tbody/tr[1]/td[2]").text
    horsen = browser.find_element_by_xpath(".//html/body/div/div[5]/table/tbody/tr[1]/td[3]/a").text
    jockey = browser.find_element_by_xpath(".//html/body/div/div[5]/table/tbody/tr[1]/td[4]").text
    ground_dist = browser.find_element_by_xpath(".//html/body/div/div[4]/table/tbody/tr[2]/td[1]").text.split(" ")[2]
    trainer = browser.find_element_by_xpath(".//html/body/div/div[5]/table/tbody/tr[1]/td[5]").text
    weight = browser.find_element_by_xpath(".//html/body/div/div[5]/table/tbody/tr[1]/td[6]").text
    act_weight = browser.find_element_by_xpath(".//html/body/div/div[5]/table/tbody/tr[1]/td[7]").text
    place = browser.find_element_by_xpath(".//html/body/div/div[5]/table/tbody/tr[1]/td[8]").text
    distance_to_first = browser.find_element_by_xpath(".//html/body/div/div[5]/table/tbody/tr[1]/td[9]").text
    running_position = browser.find_element_by_xpath(".//html/body/div/div[5]/table/tbody/tr[1]/td[10]").text
    finish_time = browser.find_element_by_xpath(".//html/body/div/div[5]/table/tbody/tr[1]/td[11]").text
    win_odds = browser.find_element_by_xpath(".//html/body/div/div[5]/table/tbody/tr[1]/td[12]").text
    trainer=browser.find_element_by_xpath(".//html/body/div/div[5]/table/tbody/tr[1]/td[5]").text
    jockey=browser.find_element_by_xpath(".//html/body/div/div[5]/table/tbody/tr[1]/td[4]").text
    col1 = ["賽次","比賽日期", "開始時間", "名次","馬ID", "馬名", "馬歲數", "馬性別", "馬毛色", "馬出生地", "馬父系", "馬母系", 
           "馬外祖父", "季初獎金", "總共獎金", "場地", "路途", "位置", "季初評分", "評分", "練馬師", "騎師", "頭馬距離", "賠率", 
           "賽際負磅", "沿途走位", "完成時間", "排位體重", "天馬", "日馬", "丁馬", "初傳", "中傳", "末傳", "神煞"]
    col2 = [ 
            raceid,
            racedate,
            raceno,
            "未知",
            racerank,
            horseid,
            horsen,
            gethorsedata(name).get("馬歲數"),
            gethorsedata(name).get("馬性別"),
            gethorsedata(name).get("馬毛色"),
            gethorsedata(name).get("出生地"),
            gethorsedata(name).get("馬父系"),
            gethorsedata(name).get("馬母系"),
            gethorsedata(name).get("馬外祖父"),
            gethorsedata(name).get("今季獎金"),
            gethorsedata(name).get("總獎金"),
            racecourse,
            ground_dist,
            place,
            gethorsedata(name).get("季初評分"),
            gethorsedata(name).get("現時評分"),
            trainer,
            jockey,
            distance_to_first,
            win_odds,
            weight,
            running_position,
            finish_time,
            act_weight,
             "未知",
             "未知",
             "未知",
             "未知",
             "未知",
             "未知",
             "未知",
           ]
    
    return dict(zip(col1,col2))

    
#if __name__ == '__main__':
    #print(Getresult("20201216").getdayresult())
