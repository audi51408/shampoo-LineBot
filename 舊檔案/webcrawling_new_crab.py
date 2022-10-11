from selenium import webdriver
import pyautogui
from bs4 import BeautifulSoup
import json
import pandas as pd
import time
import requests
import re
import warnings
import os

from queue import Queue, SimpleQueue
import threading

from werkzeug.datastructures import ImmutableDict

driver = webdriver.Chrome(r'C:\Program Files (x86)\Google\Chrome\Application\chromedriver.exe')

def sing_in():  # 登入後台
    user_name = 'b24051236@gs.ncku.edu.tw'
    user_password = 'ctpsshampoo'
    timer = 1
    driver.get('https://www.webnode.tw/ctpsxifajing/orders/')
    name = driver.find_element_by_xpath('/html/body/div[1]/main/div/div/form/div[1]/div[2]/div[2]/input')
    name.send_keys(user_name)
    time.sleep(timer)

    password = driver.find_element_by_xpath('/html/body/div[1]/main/div/div/form/div[1]/div[2]/div[3]/input')
    password.send_keys(user_password)
    time.sleep(timer)

    driver.find_element_by_xpath('/html/body/div[1]/main/div/div/form/div[1]/div[2]/div[5]/button').click()
    time.sleep(3)

def take_order(crab_time):  # 不斷更新網頁抓訂單資料跟編號 
    driver.get('https://www.webnode.tw/ctpsxifajing/orders/')
    driver.refresh()
    for i in range(crab_time):
        driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
        time.sleep(1.2)
        
    soup=BeautifulSoup(driver.page_source,'html.parser')
    order_num = []
    for titles in soup.find_all(attrs={"data-th": "訂單"}):
        order_num.append(titles.text)
    date = []
    for titles in soup.find_all(attrs={"data-th": "日期"}):
        date.append(titles.text)
    customer = []
    for titles in soup.find_all(attrs={"data-th": "顧客"}):
        customer.append(titles.text.replace('尚未付款尚未完成',''))
    total = []
    for titles in soup.find_all(attrs={"data-th": "總計"}):
        total.append(titles.text)
    # print(len(order_num),len(date),len(customer),len(total))
    dic={"訂單" : order_num,
        "日期" : date,
        '顧客':customer,
        '總計':total}
    tb=pd.DataFrame(dic)
    tb['訂單'] = tb['訂單'].astype('int')
    tb = tb.set_index('訂單')
    tb['日期'] = pd.to_datetime(tb['日期'])
    return tb,order_num

def crawlpandas(Order_number,tb):  # 抓取訂單詳細資料
    driver.get('https://www.webnode.tw/ctpsxifajing/order/' + str(Order_number) + '/')
    time.sleep(1)
    while True:
        try:
            df = pd.read_html(driver.page_source)
            break
        except:
            time.sleep(1)
            print('crawlpandas錯誤重新執行,訂單編號:',str(Order_number),end='')

    df[0] = df[0].dropna()
    df_order = df[0]
    df_order['訂單編號'] = Order_number
    df_order['顧客名稱'] = tb['顧客'][Order_number]
    df_order['下單時間'] = tb['日期'][Order_number]
    df_order =df_order[['訂單編號', '顧客名稱','下單時間', '商品號碼', '商品', '價格', '數量', '總計']]
    df_order['價格'] = df_order['價格'].str.replace('.00 TWD', '', regex=True).astype('int')
    df_order['數量'] = df_order['數量'].astype('int')
    df_order['總計'] = df_order['總計'].str.replace('.00 TWD', '', regex=True).astype('int')

    return df_order

def df_merge(number_to_merge,tb):
    for i in range(number_to_merge):
        warnings.filterwarnings('ignore')
        while True:
            try:
                locals()['df_'+str(i)] = crawlpandas (tb.index[i],tb)
                break
            except:
                time.sleep(1)
                print('df_merge錯誤重新執行,訂單編號:',tb.index[i],end='')
        if i ==0:
            df = locals()['df_'+str(i)]
        else:
            df = df.append(locals()['df_'+str(i)])
    return df

exitFlag=False
class Take_Neworder(threading.Thread):  # 開一個網路抓新訂單執行續
    def __init__(self, name, queue):
        threading.Thread.__init__(self, name=name)
        self.name = name
        self.queue = queue

    def run(self):
        sing_in()
        crab_time = 2
        count = 1
        df_old = pd.read_excel(r'訂單.xlsx').set_index('訂單')

        while True:
            print('子執行緒: {}'.format(self.name))
            (df_new,order_num) = take_order(crab_time)
            if str(df_old.index[0]) not in order_num:
                print('重新爬取')
                crab_time+=1
                continue
            elif df_new.index[0] == df_old.index[0]:
                print('沒有新訂單，第'+str(count)+'次重新爬取,最後一筆訂單號碼:'+str(df_old.index[0]), end="\r")
                time.sleep(1)
                count+=1
                if count>50:
                    count = 1
                continue
            elif str(df_old.index[0]) in order_num and df_new.index[0] != df_old.index[0]:
                tb_new = df_new[(df_new.index > df_old.index[0])]
                diff = len(tb_new)
                print('發現'+str(diff)+'筆新訂單')
                for i in range(diff):
                    tb_new_detailed = crawlpandas(tb_new.index[i],tb_new)
                    #print(tb_new_detailed)
                    self.queue.put(tb_new_detailed)  # 將新的dataframe放進queue(列隊)   
                    #df_old = tb_new.append(df_old)
                    #df_old.to_excel(r'webcrawling\訂單.xlsx')
                    time.sleep(1)
                continue

class Get_Neworder(threading.Thread):  # 抓出訂單詳細資料以做處理
    def __init__(self, name, queue):
        threading.Thread.__init__(self, name=name)
        self.name = name
        self.queue = queue
    def run(self):
        while self.queue.qsize() >= 0:
            print('子執行緒: {}'.format(self.name))
            order = self.queue.get()  # 將新的dataframe抓出queue(列隊)
            print(order['訂單編號'])
            #print('訂單資訊:{}'.format(order))
            time.sleep(1)

def main():
    orders = Queue()
    takeorder = Take_Neworder(name='takeorder', queue=orders)
    getorder = Get_Neworder(name='getorder', queue=orders)

    takeorder.setDaemon(True)  # 設定等待主執行續結束就結束子執行續
    getorder.setDaemon(True)

    takeorder.start()
    getorder.start()
    
    takeorder.join()  # 等待子執行續結束再繼續執行主執行續
    getorder.join()

if __name__ == '__main__':
    main()

    