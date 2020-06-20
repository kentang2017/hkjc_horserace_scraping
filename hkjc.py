from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
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

def testfindrace(date, racecourse, raceno):
    url = 'https://racing.hkjc.com/racing/info/meeting/Results/Chinese/Local/'+date+"/"+racecourse+"/"+str(raceno)
    browser.get(url)
    return browser.find_element_by_xpath(".//html/body/div").text

def findsinglerace(date, racecourse, raceno):
    raw_no = testfindrace(date, racecourse, raceno).index("第")
    return testfindrace(date, racecourse, raceno)[raw_no:]


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

def findraces2(date, racecourse):
    racenum = []
    for i in range(0, 18):
        url = 'https://racing.hkjc.com/racing/info/meeting/Results/Chinese/Local/'+date+"/"+racecourse+"/"+str(i)
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

def daymatchresults(date):
    if date[0:4] == "2020":
        if len(findraces(date, "HV")) > len(findraces(date, "ST")):
            data = findraces(date, "HV")
        elif len(findraces(date, "HV")) < len(findraces(date, "ST")):
            data = findraces(date, "ST")
    elif date[0:4] != "2020":
        try:
            data = findraces2(date, "HV")
        except IndexError:
            data = findraces2(date, "ST")
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
            horse_nn = {int(raceno):d}
            matches.append(horse_nn)
        except ValueError:
            pass
    return pd.concat([pd.DataFrame(matches[i], index=["第一名", "第二名", "第三名", "第四名"]).transpose() for i in range(0, len(matches))]).sort_index(ascending=True)


def daymatchresults2(date, racecourse):
    data = []
    for i in range(0,15):
        try:
            d = findsinglerace(date, racecourse, i)
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
            horse_nn = {int(raceno):d}
            matches.append(horse_nn)
        except ValueError:
            pass
    return pd.concat([pd.DataFrame(matches[i], index=["第一名", "第二名", "第三名", "第四名"]).transpose() for i in range(0, len(matches))]).sort_index(ascending=True)


def getallresults():
    datelist = getracedate()[1:]
    alldata = []
    for i in datelist:
        try:
            data = {i:daymatchresults(i).transpose().to_dict()}
            alldata.append(data)
        except (ValueError, UnboundLocalError):
            pass
    return alldata

def getdayresult(date):
    try:
        result = {date:daymatchresults2(date, "HV").transpose().to_dict()}
    except (ValueError, NoSuchElementException):
         result = {date:daymatchresults2(date, "ST").transpose().to_dict()}
    return result
    
