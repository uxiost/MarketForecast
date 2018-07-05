# -*- coding: utf-8 -*-
"""
Created on Tue Jul  3 19:36:05 2018

@author: Uxío
"""

import json
import requests
import urllib
import os
import time
import string
import pandas as pd
import steam.webauth as wa
import matplotlib.pyplot as plt

def getItemsList(url_items = None):
    if url_items == None:
        with open(r".\data\pubg.txt", "r") as read_file:
            response = json.load(read_file)
    else:
        try:
            response = json.loads(requests.get(url_items).text)
        except:
            print("Error: Can't get items list")
    return response

def getQuerryURL(itemDataBase, country='ES', currency=3, appid = 578080):
   
    #payload = {"country" = "ES",      # two letter ISO country code
    #    "currency"= 3,       # 1 is USD, 3 is EUR, not sure what others are  
    #    "appid"   = 578080,     # this is the application id.  753 is for steam cards  
    #    "market_hash_name"  ="322330-Shadows and Hexes" # this is the name of the item in the steam market.  
    #}
    url_base =r'http://steamcommunity.com/market/pricehistory/'
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    for item in itemDataBase:
        item['url'] =( url_base +'?country='+country+'&currency='+str(currency)+
        '&appid='+str(appid)+'&market_hash_name='+
        urllib.parse.quote(item['market_hash_name']) )
        filename = item['market_hash_name']
        filename = ''.join(c for c in filename if c in valid_chars)
        item['path'] = os.getcwd()+'\\data\\items\\'+filename+'.json'
    return

def login(username, password):
    # LOGIN
    user = wa.WebAuth(username, password)
    try:
        session = user.login()
    except wa.CaptchaRequired:
        print(user.captcha_url)
        # ask a human to solve captcha
        session = user.login(captcha=input("Insert captcha: "))
    except wa.EmailCodeRequired:
        session = user.login(email_code=input("Check code in e-mail: "))
    except wa.TwoFactorCodeRequired:
        session = user.login(twofactor_code=input("Check Two Factor Auth Code: "))
    return session

def fetchData(itemDataBase, n_items = 2):
    time0 = time.time()
    for i in range(n_items):
        time1 = time.time()
        deltatime = time1-time0
        if i % 20 == 0 and (deltatime)<60 and i!=0:
            print('Time to perform 20 requests [s]: ',deltatime)
            print('Waiting for [s]: ',60-deltatime )
            time.sleep(60-deltatime)
            time0 = time1
            
        dato = json.loads(session.get(itemDataBase[i]['url']).text)
        with open(itemDataBase[i]['path'],'w+') as outfile:
            json.dump(dato, outfile, indent=4)
        
def loadJSON2pandas(data, item_name):
    df = pd.DataFrame(data['prices'],columns = ["date", item_name, "volume"], dtype='float64')
    # Format date
    df['date'] = pd.to_datetime(df['date'], format='%b %d %Y %H: +%M')
    df.index = df['date']
    del df['date']
    df_volume = df.copy()
    del df_volume[item_name]
    del df['volume']
    df_volume.columns = [item_name]

    
    return df, df_volume


if __name__ == "__main__":
    itemDataBase = getItemsList() # https://skinsurveys.com/api/pubg
    getQuerryURL(itemDataBase)
    online_update = False
    if online_update:
        session = login('username','password') # Change these to your real ones
        fetchData(itemDataBase, n_items = len(itemDataBase))
        
    for item in itemDataBase:    
        with open(item['path'], "r") as read_file:
            data = json.load(read_file)
            item['df_value'],item['df_volume'] = loadJSON2pandas(data, item['market_hash_name'])
    
    values = pd.concat([item['df_value'] for item in itemDataBase], axis=1)
    volumes = pd.concat([item['df_volume'] for item in itemDataBase], axis=1)
    
    # 20 items with largest value at last timestep
    most_value = values.iloc[-2].nlargest(20)
    most_sell = volumes.iloc[-2].nlargest(20)
    
    plt.figure()
    most_sell.plot(kind='bar')
    plt.figure()
    most_value.plot(kind='bar')
#   values.nlargest(10, 2018-07-05 17:00:00)
#    values.plot()
    
    
    