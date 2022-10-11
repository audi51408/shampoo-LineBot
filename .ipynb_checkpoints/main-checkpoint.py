from selenium import webdriver
import pyautogui
from bs4 import BeautifulSoup
import json
import pandas as pd
import time
import requests
import re
import warnings
timer = 1 #


user_name = 'b24051236@gs.ncku.edu.tw'
user_password = 'ctpsshampoo'


driver = webdriver.Chrome(r'chromedriver.exe')
driver.get('https://www.webnode.tw/ctpsxifajing/orders/')

name = driver.find_element_by_xpath('/html/body/div[1]/div/main/div/div/form/div[1]/div[2]/div[2]/input')
name.send_keys(user_name)
time.sleep(timer)

password = driver.find_element_by_xpath('/html/body/div[1]/div/main/div/div/form/div[1]/div[2]/div[3]/input')
password.send_keys(user_password)
time.sleep(timer)

driver.find_element_by_xpath('/html/body/div[1]/div/main/div/div/form/div[1]/div[2]/div[5]/button').click()
time.sleep(3)

def take_order(https):
    tb =pd.read_html(https)
    tb[0] = tb[0].drop(['Unnamed: 0','訂單狀態','付款'], axis=1)

    warnings.filterwarnings('ignore')

    for k in range(len(tb[0])):
        text = tb[0]['顧客'][k]
        text_split = re.split('已付款|尚未付款|尚未完成:', text)
        tb[0]['顧客'][k] = text_split[0]

    tb[0]['日期'] = pd.to_datetime(tb[0]['日期'])
    tb[0].set_index(keys = ['訂單'],inplace = True)
    return tb[0]

tb = take_order(driver.page_source)
print(tb)


def crawlpandas(Order_number):
    driver.get('https://www.webnode.tw/ctpsxifajing/order/' + str(Order_number) + '/')
    time.sleep(1)
    while True:
        try:
            df = pd.read_html(driver.page_source)
            break
        except:
            time.sleep(1)
            print('錯誤重新執行')

    df[0] = df[0].drop(['商品號碼'], axis=1)
    df[0] = df[0].dropna()
    df[0]['訂單編號'] = Order_number
    df[0]['顧客'] = tb['顧客'][Order_number]
    df[0]['下單時間'] = tb['日期'][Order_number]
    df[0]['總金額'] = tb['總計'][Order_number]
    for i in range(len(df[0])):
        df[0]['價格'][i] = df[0]['價格'][i].replace('.00 TWD', '')
        df[0]['價格'][i] = df[0]['價格'][i].replace(',', '')
        df[0]['總計'][i] = df[0]['總計'][i].replace('.00 TWD', '')
        df[0]['總計'][i] = df[0]['總計'][i].replace(',', '')
        df[0]['總金額'][i] = df[0]['總金額'][i].replace('.00 TWD', '')
        df[0]['總金額'][i] = df[0]['總金額'][i].replace(',', '')

    df[0]['總金額'] = df[0]['總金額'].astype('int')
    df[0]['數量'] = df[0]['數量'].astype('int')
    df[0]['價格'] = df[0]['價格'].astype('int')
    df[0]['總計'] = df[0]['總計'].astype('int')

    df[0].set_index(keys=['顧客', '訂單編號', '總金額', '下單時間', '商品'], inplace=True)
    df[0] = df[0][['價格', '數量', '總計']]
    # df[0] = df[0].groupby('訂單編號')
    # df[0].get_group(tb[0].index[0])
    return df[0]


def df_merge(number_to_merge):
    for i in range(number_to_merge):
        warnings.filterwarnings('ignore')
        while True:
            try:
                locals()['df_'+str(i)] = crawlpandas (tb.index[i])
                break
            except:
                time.sleep(1)
                print('錯誤重新執行')
        if i ==0:
            df = locals()['df_'+str(i)]
        else:
            df = df.append(locals()['df_'+str(i)])
    return df

df = df_merge(len(tb.index))
print(df)

count = 1
while True:
    driver.get('https://www.webnode.tw/ctpsxifajing/orders/')
    ta = take_order(driver.page_source)
    if len(ta) > len(tb):
        new_order_name = []
        new_order_num = []
        diff = len(ta) - len(tb)
        for i in range(diff):
            new_order_name.append(tb.iloc[i]['顧客'])
            new_order_num.append(tb.index[i])
        tb = ta
        df_new_order = df_merge(diff)
        print(df_new_order)  # 訂單全部資訊
        # print(new_order_name)  #下單人名字的list
        # print(new_order_num)   #訂單編號的list

        #這裡寫詢問訂單是否正確的function--------


        #----------------------------------------

    if len(ta) <= len(tb):
        time.sleep(1)
        print('\r', '沒有新訂單，第' + str(count) + '次重新爬取',end="")
        count += 1
        if count > 50:
            count = 1
        continue
# if __name__ == '__main__':
#     print_hi('PyCharm')

