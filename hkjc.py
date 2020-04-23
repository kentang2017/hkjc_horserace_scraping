from selenium import webdriver
from selenium.webdriver.support.select import Select
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
import os
import re
import selenium
import shlex
import pandas as pd
import datetime

chrome_options = Options()
chrome_options.add_argument("--headless")
browser = webdriver.Chrome(chrome_options=chrome_options)


def getracedate():
    url = 'https://racing.hkjc.com/racing/info/meeting/Results/Chinese/Local/'
    browser.get(url)
    #racedate = [shlex.split(str(datetime.datetime.strptime(i, '%d/%m/%Y')))[0].replace("-", "") for i in shlex.split(browser.find_element_by_xpath(".//html/body/div").text)[4:-300]]
    racedate = shlex.split(browser.find_element_by_xpath(".//html/body/div").text)[4:]
    datelist = [str(x) for x in racedate if len(x) == 10 and x.count("/") == 2]
    return [shlex.split(str(datetime.datetime.strptime(g, '%d/%m/%Y')))[0].replace("-", "") for g in datelist]


def findraces(date, racecourse):
    racenum = []
    for i in range(0, 18):
        url = 'https://racing.hkjc.com/racing/info/meeting/Results/Chinese/Local/'+date+"/"+racecourse+"/"+str(i)
        browser.get(url)
        if racecourse == "HV":
            content = (browser.find_element_by_xpath(".//html/body/div").text[9029:]).replace("\n", " ")
            racenum.append(content)
        elif racecourse == "ST":
            content = (browser.find_element_by_xpath(".//html/body/div").text[9031:]).replace("\n", " ")
            racenum.append(content)
    race_num = [x for x in racenum if len(x) > 281]
    return list(set(race_num))

def daymatchresults(date, racecourse):
    data = findraces(date, racecourse)
    matches = []
    for r in data:
        horsedata = shlex.split(r[r.index("賠率"):r.index("備註")])[2:]
        raceno = r[:r.index("場")]
        b = [x for x in horsedata if len(x) > 7][0:4]
        c = [horsedata[horsedata.index(horse)-1] for horse in b][0:4]
        horse_nn = {raceno:dict(zip(b, c))}
        matches.append(horse_nn)
    return matches
    
