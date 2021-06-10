def getrow(date, racecourse, raceno, i):
    #2021/06/06
    url = "https://racing.hkjc.com/racing/information/Chinese/Racing/LocalResults.aspx?RaceDate="+date+"&Racecourse="+racecourse+"&RaceNo="+raceno
    browser.get(url)
    horses = []
    name = browser.find_element_by_xpath(".//html/body/div/div[5]/table/tbody/tr["+i+"]/td[3]").text.split("(")[0]
    raceid = browser.find_element_by_xpath(".//html/body/div/div[4]/table/thead/tr/td[1]").text.split("(")[1].replace(")", "")
    racedate = date
    horseid = browser.find_element_by_xpath(".//html/body/div/div[5]/table/tbody/tr["+i+"]/td[3]").text.split("(")[1][:-1]
    ground_status  = browser.find_element_by_xpath(".//html/body/div/div[4]/table/tbody/tr[2]/td[3]").text
    horseid = browser.find_element_by_xpath(".//html/body/div/div[5]/table/tbody/tr["+i+"]/td[3]").text.split("(")[1][:-1]
    racerank = browser.find_element_by_xpath(".//html/body/div/div[5]/table/tbody/tr["+i+"]/td[1]").text
    horseno = browser.find_element_by_xpath(".//html/body/div/div[5]/table/tbody/tr["+i+"]/td[2]").text
    horsen = browser.find_element_by_xpath(".//html/body/div/div[5]/table/tbody/tr["+i+"]/td[3]/a").text
    jockey = browser.find_element_by_xpath(".//html/body/div/div[5]/table/tbody/tr["+i+"]/td[4]").text
    ground_dist = browser.find_element_by_xpath(".//html/body/div/div[4]/table/tbody/tr[2]/td[1]").text.split(" ")[2]
    trainer = browser.find_element_by_xpath(".//html/body/div/div[5]/table/tbody/tr["+i+"]/td[5]").text
    weight = browser.find_element_by_xpath(".//html/body/div/div[5]/table/tbody/tr["+i+"]/td[6]").text
    act_weight = browser.find_element_by_xpath(".//html/body/div/div[5]/table/tbody/tr["+i+"]/td[7]").text
    place = browser.find_element_by_xpath(".//html/body/div/div[5]/table/tbody/tr["+i+"]/td[8]").text
    distance_to_first = browser.find_element_by_xpath(".//html/body/div/div[5]/table/tbody/tr["+i+"]/td[9]").text
    running_position = browser.find_element_by_xpath(".//html/body/div/div[5]/table/tbody/tr["+i+"]/td[10]").text
    finish_time = browser.find_element_by_xpath(".//html/body/div/div[5]/table/tbody/tr["+i+"]/td[11]").text
    win_odds = browser.find_element_by_xpath(".//html/body/div/div[5]/table/tbody/tr["+i+"]/td[12]").text
    trainer=browser.find_element_by_xpath(".//html/body/div/div[5]/table/tbody/tr["+i+"]/td[5]").text
    jockey=browser.find_element_by_xpath(".//html/body/div/div[5]/table/tbody/tr["+i+"]/td[4]").text
    dict2 = {
            "賽次":raceid,
            "日期":racedate,
            "時間": "未知",
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
    dict3 =  [raceid,racedate,ground_dist,ground_status, "未知",name,racerank,place,jockey,trainer,distance_to_first,win_odds,weight, running_position, finish_time, act_weight]
    return pd.DataFrame(list(dict2.values())).transpose()
    #return dict3
    
def gethorseracerow(date, racecourse, raceno):
    horses = []
    for y in range(1,20):
        try:
            b = getrow(date, racecourse, raceno, str(y))
            horses.append(b)
        except NoSuchElementException:
            pass
    return pd.concat(horses)

def getdaymatches(date, racecourse):
    horses = []
    for i in range(1,12):
        try:
            c = gethorseracerow(date, racecourse, str(i))
            horses.append(c)
        except (NoSuchElementException, TypeError):
            pass
    return horses
            
