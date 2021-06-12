# -*- coding: utf-8 -*-
"""
Created on Thu Jul 30 08:30:35 2020
@author: Ken Tang
@email: kinyeah@gmail.com
"""

from pymongo import MongoClient
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
import shlex
import pandas as pd
import datetime, itertools
from kinqimen import Qimen
import kinliuren
import sxtwl

chrome_options = Options()
chrome_options.add_argument("--headless")
browser = webdriver.Chrome(chrome_options=chrome_options)
url = 'https://racing.hkjc.com/racing/info/meeting/Results/Chinese/Local/'
browser.get(url)

columns = ["賽次","比賽日期", "開始時間", "名次","馬ID", "馬名", "馬歲數", "馬性別", "馬身顏色", "馬出生地", "馬父系", "馬母系", 
           "馬外祖父", "季初獎金", "總共獎金", "場地", "路途", "位置", "季初評分", "評分", "練馬師", "騎師", "頭馬距離", "賠率", 
           "賽際負磅", "沿途走位", "完成時間", "排位體重", "配備", "天馬", "日馬", "丁馬", "初傳", "中傳", "末傳", "神煞"]

url_list = ["https://racing.hkjc.com/racing/information/Chinese/Horse/SelectHorsebyChar.aspx?ordertype="+str(i) for i in [2,3,4]]

tiangan = list('甲乙丙丁戊己庚辛壬癸')
dizhi = list('子丑寅卯辰巳午未申酉戌亥')

client = MongoClient("mongodb+srv://savedata:savedata@cluster0-im6tx.gcp.mongodb.net/test?retryWrites=true&w=majority")
db = client.get_database('qimen')
db_shigankeying = db.shigankeying

hrdb = client.get_database('hkjc')
db_matches = hrdb.matches

def multi_key_dict_get(d, k):
    for keys, v in d.items():
        if k in keys:
            return v
    return None

def jiazi():
    jiazi = [tiangan[x % len(tiangan)] + dizhi[x % len(dizhi)] for x in range(60)]
    return jiazi

def repeat_list(n, thelist):
        return [repetition for i in thelist for repetition in itertools.repeat(i,n) ]
    
def minutes_jiazi_d():
    t = []
    for h in range(0,24):
        for m in range(0,60):
            b = str(h)+":"+str(m)
            t.append(b)
    minutelist = dict(zip(t, itertools.cycle(repeat_list(2, jiazi()))))
    return minutelist

def gangzhi(year, month, day, hour, minute):
    lunar = sxtwl.Lunar()
    cdate = lunar.getDayBySolar(year, month, day)
    yy_mm_dd = tiangan[cdate.Lyear2.tg]+dizhi[cdate.Lyear2.dz],  tiangan[cdate.Lmonth2.tg]+dizhi[cdate.Lmonth2.dz],  tiangan[cdate.Lday2.tg]+dizhi[cdate.Lday2.dz]
    timegz = lunar.getShiGz(cdate.Lday2.tg, hour)
    new_hh = tiangan[timegz.tg]+dizhi[timegz.dz]
    gangzhi_minute = minutes_jiazi_d().get(str(hour)+":"+str(minute))
    return [yy_mm_dd[0], yy_mm_dd[1],  yy_mm_dd[2], new_hh, gangzhi_minute]

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

def gethorsedata2(hid):
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

generals_zhi = {**dict(zip(['貴'+i for i in dizhi], "吉,吉,凶,吉,凶,凶,凶,吉,吉,凶,凶,吉".split(","))),
**dict(zip(['后'+i for i in dizhi], "凶,凶,吉,凶,凶,凶,凶,凶,吉,凶,凶,吉".split(","))),
**dict(zip(['陰'+i for i in dizhi], "凶,凶,凶,凶,吉,凶,凶,吉,吉,吉,凶,凶".split(","))),
**dict(zip(['玄'+i for i in dizhi], "吉,吉,凶,凶,吉,凶,凶,凶,吉,吉,吉,凶".split(","))),
**dict(zip(['常'+i for i in dizhi], "凶,吉,凶,凶,吉,吉,吉,吉,吉,吉,凶,吉".split(","))),
**dict(zip(['虎'+i for i in dizhi], "凶,凶,凶,凶,凶,凶,凶,凶,吉,凶,凶,凶".split(","))),
**dict(zip(['空'+i for i in dizhi], "凶,凶,凶,凶,凶,凶,凶,吉,凶,凶,凶,凶".split(","))),
**dict(zip(['龍'+i for i in dizhi], "吉,凶,吉,吉,吉,凶,凶,凶,凶,凶,吉,吉".split(","))),
**dict(zip(['勾'+i for i in dizhi], "凶,凶,凶,凶,吉,吉,凶,吉,凶,凶,凶,凶".split(","))),
**dict(zip(['合'+i for i in dizhi], "凶,吉,吉,吉,凶,凶,吉,吉,吉,凶,凶,吉".split(","))),
**dict(zip(['雀'+i for i in dizhi], "凶,凶,吉,吉,凶,吉,吉,凶,吉,凶,凶,凶".split(","))),
**dict(zip(['蛇'+i for i in dizhi], "吉,吉,吉,凶,吉,吉,吉,吉,吉,凶,凶,吉".split(",")))}

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
    
def getrow(date, racecourse, raceno, ri, timeslot):
    #2021/06/06
    url = "https://racing.hkjc.com/racing/information/Chinese/Racing/LocalResults.aspx?RaceDate="+date+"&Racecourse="+racecourse+"&RaceNo="+str(raceno)
    browser.get(url)
    name = browser.find_element_by_xpath(".//html/body/div/div[5]/table/tbody/tr["+str(ri)+"]/td[3]").text.split("(")[0]
    raceid = browser.find_element_by_xpath(".//html/body/div/div[4]/table/thead/tr/td[1]").text.split("(")[1].replace(")", "")
    racedate = date
    horseid = browser.find_element_by_xpath(".//html/body/div/div[5]/table/tbody/tr["+str(ri)+"]/td[3]").text.split("(")[1][:-1]
    ground_status  = browser.find_element_by_xpath(".//html/body/div/div[4]/table/tbody/tr[2]/td[3]").text
    horseid = browser.find_element_by_xpath(".//html/body/div/div[5]/table/tbody/tr["+str(ri)+"]/td[3]").text.split("(")[1][:-1]
    racerank = browser.find_element_by_xpath(".//html/body/div/div[5]/table/tbody/tr["+str(ri)+"]/td[1]").text
    horseno = browser.find_element_by_xpath(".//html/body/div/div[5]/table/tbody/tr["+str(ri)+"]/td[2]").text
    horsen = browser.find_element_by_xpath(".//html/body/div/div[5]/table/tbody/tr["+str(ri)+"]/td[3]/a").text
    jockey = browser.find_element_by_xpath(".//html/body/div/div[5]/table/tbody/tr["+str(ri)+"]/td[4]").text
    ground_dist = browser.find_element_by_xpath(".//html/body/div/div[4]/table/tbody/tr[2]/td[1]").text.split(" ")[2]
    trainer = browser.find_element_by_xpath(".//html/body/div/div[5]/table/tbody/tr["+str(ri)+"]/td[5]").text
    weight = browser.find_element_by_xpath(".//html/body/div/div[5]/table/tbody/tr["+str(ri)+"]/td[6]").text
    act_weight = browser.find_element_by_xpath(".//html/body/div/div[5]/table/tbody/tr["+str(ri)+"]/td[7]").text
    place = browser.find_element_by_xpath(".//html/body/div/div[5]/table/tbody/tr["+str(ri)+"]/td[8]").text
    distance_to_first = browser.find_element_by_xpath(".//html/body/div/div[5]/table/tbody/tr["+str(ri)+"]/td[9]").text
    running_position = browser.find_element_by_xpath(".//html/body/div/div[5]/table/tbody/tr["+str(ri)+"]/td[10]").text
    finish_time = browser.find_element_by_xpath(".//html/body/div/div[5]/table/tbody/tr["+str(ri)+"]/td[11]").text
    win_odds = browser.find_element_by_xpath(".//html/body/div/div[5]/table/tbody/tr["+str(ri)+"]/td[12]").text
    trainer=browser.find_element_by_xpath(".//html/body/div/div[5]/table/tbody/tr["+str(ri)+"]/td[5]").text
    jockey=browser.find_element_by_xpath(".//html/body/div/div[5]/table/tbody/tr["+str(ri)+"]/td[4]").text
    
    whichday = {"Tue":"星期二", "Mon": "星期一", "Wed":"星期三", "Thu":"星期四", "Fri":"星期五", "Sat":"星期六", "Sun":"星期日"}
    dayornight = {("星期一", "星期二", "星期三", "星期四", "星期五"):"夜", ("星期六", "星期日"):"晝" }
    dayt = {"夜":18, "晝":12}
    daytt = {"晝":
            {0:["12:45","13:15", "13:45", "14:15", "15:10", "15:40", "16:10", "16:40", "17:15", "17:50"],
            1:["12:30","13:00", "13:30", "14:00", "14:30", "15:00", "15:35", "16:05", "16:35", "17:10", "17:45"],
            2:["13:00","13:30", "14:00", "14:30", "15:00", "15:35", "16:05", "16:35", "17:10", "17:45"]}, 
            "夜":
            {0:["19:00", "19:30", "20:00", "20:30", "21:00", "21:30", "22:00", "22:30"], 
            1:["19:30", "20:00", "20:30", "21:00", "21:30", "22:00", "22:30", "23:00"],
            2:["19:15", "19:45", "20:15", "20:45", "21:15", "21:45", "22:15", "22:50"],
            3:["18:45", "19:15", "19:45", "20:15", "20:45", "21:15", "21:45", "22:15", "22:50"]}
            }
    ddate = whichday.get(datetime.datetime.strptime(date.replace("/",""), '%Y%m%d').strftime("%a"))
    dnn = multi_key_dict_get(dayornight, ddate)
    time = dict(zip(range(1, len(daytt.get(dnn).get(timeslot))), daytt.get(dnn).get(timeslot))).get(int(raceno))
    hour = int(time.split(":")[0])
    minute = int(time.split(":")[1])
    getdhorse = dhorse(date, hour, minute)
    getthree = three(date, hour, minute)
    getdaythree = daythree(date, hour, minute)
    liuren_place_day = int(place) in getdaythree
    liuren_horseno =  int(horseno) in getthree
    getmhorse = moonhorse(date, hour, minute)
    getdinhorse = dinhorse(date, hour, minute)
    ggolden = golden(date, hour, minute, int(place))
    try:
        getqimenh = qimenh(date, hour, minute, int(place))
    except TypeError:
        getqimenh = "凶"
    
    if int(horseno) == getdhorse:
        liuren_dhoresno = True
    else:
        liuren_dhoresno = False
    if getdhorse == int(place):
        liuren_dhorse = True
    else:
        liuren_dhorse = False
    if getmhorse == int(place):
        liuren_mhorse = True
    else:
        liuren_mhorse = False
    if getdinhorse == int(place):
        liuren_dinhorse = True
    else:
        liuren_dinhorse = False
    liuren_place = int(place) in getthree
    general = getgeneral(date, hour, minute, int(place))
    dict2 = {
            "賽次":raceid,
            "日夜":dnn,
            "日期":racedate,
            "時間":time,
            "路途":ground_dist,
            "路況":ground_status,
            "馬名":name,
            "名次":racerank,
            "檔位":place,
            "騎師": jockey,
            "練馬師":trainer,
            "頭馬距離": distance_to_first,
            "賠率":win_odds,
            "賽際負磅":weight, 
            "沿途走位":running_position, 
            "完成時間":finish_time, 
            "排位體重":act_weight
            }
    dict1 =  ["賽次","場次", "日期","時間","日夜","路途","路況","馬號","馬名","名次","檔位","騎師","練馬師","頭馬距離","賠率","賽際負磅","沿途走位","完成時間",
              "排位體重", "六壬天馬", "六壬丁馬",
              "六壬日馬檔位", "六壬日馬馬號", "六壬日課三傳檔位", "六壬時盤三傳檔位", 
              "六壬時盤三傳馬號", "六壬神煞", "日家奇門檔位", "時家奇門檔位"]
    dict3 =  [raceid, raceno,racedate,time,dnn,ground_dist,ground_status, horseno,name,racerank,place,jockey,trainer,distance_to_first,win_odds,weight, running_position, finish_time, 
              act_weight, liuren_mhorse, liuren_dinhorse,
              liuren_dhorse, liuren_dhoresno , liuren_place_day, liuren_place, liuren_horseno, 
              general, ggolden, getqimenh]

    return dict(zip(dict1,dict3))

def gethorseracerow(date, racecourse, raceno):
    horses = []
    for y in range(1,20):
        try:
            b = getrow(date, racecourse, raceno, str(y))
            horses.append(b)
        except NoSuchElementException:
            pass
    return horses

def getdaymatches(date, racecourse):
    horses = []
    for i in range(1,12):
        try:
            c = gethorseracerow(date, racecourse, str(i))
            horses.append(c)
        except (NoSuchElementException, TypeError):
            pass
    return horses

def getliurend(d, hour, minute):
    dated = d.split("/")
    jieqi = Qimen(int(dated[0]), int(dated[1]), int(dated[2]), hour).find_jieqi()
    gz = gangzhi(int(dated[0]), int(dated[1]), int(dated[2]), int(hour), int(minute))
    liuren = kinliuren.Liuren(jieqi, gz[2], gz[3]).result(0)
    return liuren

def getliuren(d, hour, minute):
    dated = d.split("/")
    jieqi = Qimen(int(dated[0]), int(dated[1]), int(dated[2]), hour).find_jieqi()
    gz = gangzhi(int(dated[0]), int(dated[1]), int(dated[2]), int(hour), int(minute))
    liuren = kinliuren.Liuren(jieqi, gz[3], gz[4]).result(0)
    return liuren

def tiandid(d, hour, minute):
    tiandi = getliurend(d, hour, minute).get("地轉天盤")
    a = dict(zip(dizhi, range(1,13)))
    c = dict(zip(list(tiandi.values()), [a.get(i) for i in list(tiandi.keys())]))
    return c

def tiandi(d, hour, minute):
    tiandi = getliuren(d, hour, minute).get("地轉天盤")
    a = dict(zip(dizhi, range(1,13)))
    c = dict(zip(list(tiandi.values()), [a.get(i) for i in list(tiandi.keys())]))
    return c

def dhorse(d, hour, minute):
    #2021/06/06
    dhorsep = getliurend(d, hour, minute).get("日馬")
    return tiandid(d, hour, minute).get(dhorsep)

def three(d, hour,  minute):
    getthree = [i[0]for i in list(getliuren(d, hour, minute).get("三傳").values())]
    return [tiandi(d, hour, minute).get(y) for y in getthree]
    
def daythree(d, hour,  minute):
    getthree = [i[0]for i in list(getliurend(d, hour, minute).get("三傳").values())]
    return [tiandid(d, hour, minute).get(y) for y in getthree]

def threemix(d, hour, minute):
    getthree = [i[0]for i in list(getliurend(d, hour, minute).get("三傳").values())]
    return [tiandi(d, hour, minute).get(y) for y in getthree]
    
def getgeneral(d, hour, minute, place):
    #2021/06/06
    tiandi = getliuren(d, hour, minute).get("天地盤").get("地盤")
    general = getliuren(d, hour, minute).get("天地盤").get("天將")
    zdict = dict(zip(range(1,13), tiandi))
    gdict = dict(zip(range(1,13), general))
    #return dict(zip(range(1,13), earth)).get(place)
    return generals_zhi.get(gdict.get(place)+zdict.get(int(place)))

def moonhorse(d, hour, minute):
    moonhorsedict = {tuple(list("寅申")):"午", tuple(list("卯酉")):"申", tuple(list("辰戌")):"戌", tuple(list("巳亥")):"子", tuple(list("午子")):"寅", tuple(list("丑未")):"辰"}
    dated = d.split("/")
    gz = gangzhi(int(dated[0]), int(dated[1]), int(dated[2]), int(hour), int(minute))
    getmhorse = multi_key_dict_get(moonhorsedict, gz[1][1])
    tiandi = getliuren(d, hour, minute).get("天地盤").get("地盤")
    zdict = dict(zip(tiandi,range(1,13)))
    return zdict.get(getmhorse)

def dinhorse(d, hour, minute):
    dinhorsedict = {"甲子":"卯", "甲戌":"丑", "甲申":"亥", "甲午":"酉", "甲辰":"未", "甲寅":"巳"}
    liujiashun_dict = {tuple(jiazi()[0:10]):'甲子', tuple(jiazi()[10:20]):"甲戌", tuple(jiazi()[20:30]):"甲申", tuple(jiazi()[30:40]):"甲午", tuple(jiazi()[40:50]):"甲辰",  tuple(jiazi()[50:60]):"甲寅"  }
    dated = d.split("/")
    dayganzhi = gangzhi(int(dated[0]), int(dated[1]), int(dated[2]), int(hour), int(minute))[3]
    shun =  multi_key_dict_get(liujiashun_dict, dayganzhi)
    getdinhorese = multi_key_dict_get(dinhorsedict, shun)
    tiandi = getliuren(d, hour, minute).get("天地盤").get("地盤")
    zdict = dict(zip(tiandi,range(1,13)))
    return zdict.get(getdinhorese)

def golden(d, hour, minute, place):
    dd = d.split("/")
    a = list(Qimen(int(dd[0]), int(dd[1]), int(dd[2]), int(hour)).g.get("星").keys())
    d = list(Qimen(int(dd[0]), int(dd[1]), int(dd[2]), int(hour)).g.get("星").values())
    b = {"坎":(1,10),
        "坤":(2,11),
        "震":(3,12),
        "巽":(4,13),
        "中":(5,14),
        "乾":(6,15),
        "兌":(7,16),
        "艮":(8,17),
        "離":(9,18)}
    e = [b.get(i) for i in a]
    c = dict(zip( ['太乙','攝提', '軒轅', '招搖','天符', '青龍', '咸池','太陰','天乙'], list("吉凶凶凶吉吉凶吉吉")))
    return multi_key_dict_get(dict(zip([b.get(i) for i in a],[ c.get(y) for y in d])), place)

def qimenh(d, hour, minute, place):
    dd = d.split("/")
    b = {"坎":(1,10),
        "坤":(2,11),
        "震":(3,12),
        "巽":(4,13),
        "中":(5,14),
        "乾":(6,15),
        "兌":(7,16),
        "艮":(8,17),
        "離":(9,18)}
    tk = list(Qimen(int(dd[0]), int(dd[1]), int(dd[2]), int(hour)).p.get("天盤")[0].keys())
    tv = list(Qimen(int(dd[0]), int(dd[1]), int(dd[2]), int(hour)).p.get("天盤")[0].values())
    t1 = [b.get(i) for i in tk]
    t = dict(zip(t1, tv))
    dk = list(Qimen(int(dd[0]), int(dd[1]), int(dd[2]), int(hour)).p.get("地盤").keys())
    dv = list(Qimen(int(dd[0]), int(dd[1]), int(dd[2]), int(hour)).p.get("地盤").values())
    d1 = [b.get(i) for i in dk]
    d = dict(zip(d1, dv))
    td = multi_key_dict_get(t, int(place)) + multi_key_dict_get(d, int(place))
    return db_shigankeying.find_one({"天地":td}).get(td)[1]

for y in range(1,11):
    for i in range(1,13):
        try:
            db_matches.insert_one(getrow("2021/06/09", "HV",y, i, 3))
            print("done")
        except (IndexError, TypeError, NoSuchElementException):
            pass
