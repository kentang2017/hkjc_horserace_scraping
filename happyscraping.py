from selenium import webdriver
from selenium.webdriver.support.select import Select
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
import os, selenium, shlex, datetime
import pandas as pd

chrome_options = Options()
chrome_options.add_argument("--headless")
browser = webdriver.Chrome(chrome_options=chrome_options)



class Horse():
    #找馬會歷場記錄之日期
    def getracedates(self):
        url = 'https://racing.hkjc.com/racing/info/meeting/Results/Chinese/Local/'
        browser.get(url)
        racedate = [shlex.split(str(datetime.datetime.strptime(i, '%d/%m/%Y')))[0].replace("-", "") for i in shlex.split(browser.find_element_by_xpath(".//html/body/div").text)[4:-7]]
        return racedate

    def findraceresults(self, date):
        racenum = []
        for i in range(0,15):
            url = 'https://racing.hkjc.com/racing/info/meeting/Results/Chinese/Local/'+date+"/"+ str(i)
            browser.get(url)
            content = browser.find_element_by_xpath(".//html/body/div").text[8982:].replace("\n", " ")
            if content[0] == "第":
                raceresult = content
            elif content[0] != "第":
                raceresult = 0
            racenum.append(raceresult)
        race_num =  [x for x in racenum if x != 0]
        if race_num[0] ==  race_num[1]:
            del race_num[0]
        return race_num
    
     def matchresults(self, date):
        data = findraceno(date)
        matches = []
        for r in data:
            horsedata = shlex.split(r[r.index("賠率"):r.index("備註")])[2:]
            matches.append(horsedata)
        horselist = []
        for h in matches:
            b = [x for x in g if len(x) > 7]
            horselist.append(b)
        return horselist
