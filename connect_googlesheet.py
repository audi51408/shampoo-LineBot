from bs4 import BeautifulSoup
import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
import pandas as pd
import collections
import numpy as np
import datetime
import pygsheets
import time
from gspread_dataframe import set_with_dataframe
from oauth2client.service_account import ServiceAccountCredentials as SAC
import time
# import safety_margin




auth_json_path = './spreedsheet/arimino-c952a6160f63.json'
gss_scopes = ['https://spreadsheets.google.com/feeds']
# 連線
credentials = ServiceAccountCredentials.from_json_keyfile_name(auth_json_path, gss_scopes)
gss_client = gspread.authorize(credentials)

Json = './spreedsheet/arimino-c952a6160f63.json'  # Json 的單引號內容請改成妳剛剛下載的那個金鑰
Url = ['https://spreadsheets.google.com/feeds']
Connect = SAC.from_json_keyfile_name(Json, Url)
GoogleSheets = gspread.authorize(Connect)





def find_order(text):
    #讀檔案
    if text == 'new':
        new_path = "./orders/check_orders.xlsx"
        old_path = './spreedsheet/order_information.json'
    elif text =='cancel':
        new_path = "./orders/delet_order.xlsx"
        old_path = './spreedsheet/cancel_order.json'
    
    df_new = pd.read_excel(new_path)
    with open(old_path, 'r', encoding='utf-8') as f0:
        df_old = pd.DataFrame(json.load(f0))
    #比對
    list_old = set(list(df_old['訂單編號']))
    list_new = set(list(df_new['訂單編號']))
    new_order_list = list(list_new.difference(list_old))
    #寫入新的訂單
    with open(old_path, "w", encoding='utf-8') as f:  # 寫成一個json檔
        df_new.to_json(f, force_ascii=False)
    #取出最新的訂單
    new_table = pd.DataFrame({})
    for i in list(new_order_list):
        tb = df_new[df_new['訂單編號']==i]
        new_table = pd.concat([tb,new_table])
    return new_table


def upload_num(new,text):
    month = []
    for i in range(len(new)):
        month.append(str(new['訂單編號'][i])[2:4])
    month = sorted(list(set(month)))
    for k in range(len(month)):
        df_template = pd.DataFrame(GoogleSheets.open_by_key('16mrBpmV5chH4pOhf86ejbpS7ewFl0bWCViVAtpQ8F7o').worksheet(str(int(month[k]))+'月出貨').get_all_records())
        for i in range(len(new)):
            df_month = int(str(new.iloc[i]['訂單編號'])[2:4])
            if df_month==int(month[k]):
                code = str(new.iloc[i]['商品號碼'])
                for j in range(len(df_template)):
                    if str(df_template['商品編號'][j])==code:
                        print('a')
                        if text =='new':
                            df_template['數量'][j]+=int(new.iloc[i]['數量'])
                        elif text =='cancel':
                            df_template['數量'][j]-=int(new.iloc[i]['數量'])
        googlesheet = GoogleSheets.open_by_key('16mrBpmV5chH4pOhf86ejbpS7ewFl0bWCViVAtpQ8F7o').worksheet(str(int(month[k]))+'月出貨')
        print('a')
        set_with_dataframe(googlesheet,df_template)
        print('修改'+str(int(month[k]))+'出貨表')


if __name__ == '__main__':
    new_order = find_order('new') #取得新確認的訂單
    cancel_order = find_order('cancel') #取得新取消的訂單
    print('new_order:',new_order)
    print('cancel_order:',cancel_order)
    upload_num(new_order,'new') #加上新訂單商品的數量
    upload_num(cancel_order,'cancel') #減掉新訂單商品的數量
    
    #print(upload_num(new))

