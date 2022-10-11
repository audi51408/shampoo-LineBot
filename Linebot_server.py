from queue import Queue
from flask import Flask, request, abort
import flask

from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (FollowEvent, UnfollowEvent, MessageEvent, TextMessage, TextSendMessage, PostbackEvent, QuickReply, QuickReplyButton)
from linebot.models.actions import (MessageAction)

import configparser
import json
import os
import pandas as pd
import threading
import time
import datetime
from selenium import webdriver

# import main

from richmenu.rich_menu import rich_menu_id_start, rich_menu_id_registing, rich_menu_id_normal
from webcrawling.new_crab import Take_Neworder

### 完整linebot api參考(善用ctrl+f):https://github.com/line/line-bot-sdk-python/blob/master/examples/flask-kitchensink/app.py

app = Flask(__name__)  # 建立 Flask 物件

config = configparser.ConfigParser()
config.read('config.ini')

line_bot_api = LineBotApi(config.get('line-bot', 'channel-access-token'))
handler = WebhookHandler(config.get('line-bot', 'channel-secret'))

RegisteredData_path = './registered_data.json'
with open(RegisteredData_path, 'r', encoding='utf-8') as file:
    registered_data = json.load(file)

# 接收LINE資訊
@app.route("/callback", methods=['POST'])  # 裝飾器
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'


@handler.add(FollowEvent)  # 加入帳號
def Follow(event):
    reply = '歡迎使用本linebot，提醒您使用前要先註冊喔!'
    line_bot_api.reply_message(event.reply_token,TextSendMessage(text=reply))


@handler.add(UnfollowEvent)  # 封鎖帳號
def Unfollow(event):
    user_id = event.source.user_id
    try:
        del registered_data[user_id]
        with open(RegisteredData_path, 'w', encoding='utf-8') as file:
            json.dump(registered_data, file, ensure_ascii=False, indent=4)
    except:
        pass
    line_bot_api.unlink_rich_menu_from_user(user_id)


@handler.add(PostbackEvent)  # line回傳EVENT
def Postback(event):
    user_id = event.source.user_id
    print(user_id)


@handler.add(MessageEvent, message=TextMessage)  # 回復訊息
def Start(event):
    text = event.message.text
    user_id = event.source.user_id
    reply = '功能尚未完成'

    if registered_data.get(user_id) == None:
        registered_data[user_id] = {}
        registered_data[user_id]['State'] = 'newcome'
        reply = '歡迎使用本linebot，提醒您使用前要先註冊喔!'
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=reply))
        line_bot_api.link_rich_menu_to_user(user_id, rich_menu_id_registing)
        with open(RegisteredData_path, 'w', encoding='utf-8') as file:
            json.dump(registered_data, file, ensure_ascii=False, indent=4)


    elif registered_data[user_id].get('State') == 'newcome':  # 新加入
        line_bot_api.link_rich_menu_to_user(user_id, rich_menu_id_registing)    
        if text == '註冊':
            registered_data[user_id]['State'] = 'registing'
            reply = '{}'.format('點擊左下角的小鍵盤輸入您的姓名(將作為收件人名稱)')
        else:
            reply = '您還沒有註冊喔!請點選下方註冊按鈕進行註冊'
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))
        with open(RegisteredData_path, 'w', encoding='utf-8') as file:
            json.dump(registered_data, file, ensure_ascii=False, indent=4)


    elif registered_data[user_id].get('State') == 'registing':  # 註冊中
        data_need = ['姓名', '電話', '地址']
        str_list = ['註冊','修改資料','查詢訂單','刪除訂單','哈哈哈','開始使用','是','否']#防呆
        if text in str_list:
            reply = '請點擊左下方鍵盤輸入對應的資料'
        else:
            for i in range(len(data_need)):
                if registered_data[user_id].get(data_need[i]) is None  and i < len(data_need)-1:# i=0=姓名 > 回傳需要i=1=電話,i=1=電話 > 回傳需要i=2=地址
                    registered_data[user_id][data_need[i]] = text
                    reply = '請輸入您的{}'.format(data_need[i+1])
                    break
                elif i == len(data_need)-1:  # i=2=地址
                    registered_data[user_id][data_need[i]] = text
                    registered_data[user_id]['State'] = 'normal'
                    reply = '註冊成功！提醒您於下訂單時，訂單資料務必與註冊資料相同！\n您的註冊資料為:\n姓名:{}\n電話:{}\n收件地址:{}'.format(
                        registered_data[user_id]['姓名'],registered_data[user_id]['電話'],registered_data[user_id]['地址'])
                    break 
            line_bot_api.link_rich_menu_to_user(user_id,rich_menu_id_normal)  # 啟用正常圖文選單
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))
        with open(RegisteredData_path, 'w', encoding='utf-8') as file:
            json.dump(registered_data, file, ensure_ascii=False, indent=4)


    elif registered_data[user_id].get('State') == 'normal':  # 開始使用正常功能
        line_bot_api.link_rich_menu_to_user(user_id, rich_menu_id_normal)
        if text == '修改資料':
            reply = '確定要修改資料嗎?'
            registered_data[user_id]['State'] = 'changedata'
            with open(RegisteredData_path, 'w', encoding='utf-8') as file:
                json.dump(registered_data, file, ensure_ascii=False, indent=4)
            line_bot_api.reply_message(
                event.reply_token, 
                TextSendMessage(
                    text=reply,
                    quick_reply=QuickReply(
                        items=[
                            QuickReplyButton(action=MessageAction(label='是', text='是')),
                            QuickReplyButton(action=MessageAction(label='否', text='否'))
                        ]
                    )
                )
            )
        elif text == '查詢訂單':
            df_col = ['顧客名稱','訂單編號','下單時間','商品號碼','商品','價格','數量','總金額','備註']
            shiftday = pd.to_datetime(datetime.date.today()-datetime.timedelta(days=3)) #三天前的時間
            order_col = ['商品', '價格', '數量']
            df = pd.read_excel('orders/check_orders.xlsx')[df_col]
            df_returnable = df[df['下單時間']>shiftday]
            df_returnlist_num = sorted(list(set(list(df_returnable[ df_returnable['顧客名稱']==registered_data[user_id]['姓名']]['訂單編號']))))
            if len(df_returnlist_num)==0:
                reply = '您尚無可取消的訂單!'
            else:
                reply = '可取消的訂單為:\n'
                for k in range (len(df_returnlist_num)):
                    if k!=0:
                        reply+='----------------------\n'
                    df_returnable= df[df['訂單編號']==int(df_returnlist_num[k])][['下單時間','商品','價格','數量','總金額']]
                    reply+='訂單編號:{}\n下單時間:{}\n總金額:{}\n'.format(str(df_returnlist_num[k]),str(df_returnable.iloc[0]['下單時間']),str(df_returnable.iloc[0]['總金額']))
                    for i in range(len(df_returnable)):
                        for j in order_col:
                            if j=='商品' and '色度:' in df_returnable.iloc[i][j]:
                                df_split = df_returnable.iloc[i][j].split('色')
                                string = str(j)+':'+str(df_split[0])+'\n色'+str(df_split[1])+'\n'
                            else:    
                                string = str(j)+':'+str(df_returnable.iloc[i][j])+'\n'
                            if j=='數量':
                                string+='\n'
                            reply+=string
                reply = reply[:-2]
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))
        elif text == '刪除訂單':
            df_col = ['顧客名稱','訂單編號','下單時間','商品號碼','商品','價格','數量','總金額','備註']
            shiftday = pd.to_datetime(datetime.date.today()-datetime.timedelta(days=3)) #三天前的時間
            order_col = ['商品', '價格', '數量']
            df = pd.read_excel('orders/check_orders.xlsx')[df_col]
            df_returnable = df[df['下單時間']>shiftday]
            df_returnlist_num = sorted(list(set(list(df_returnable[ df_returnable['顧客名稱']==registered_data[user_id]['姓名']]['訂單編號']))))
            if len(df_returnlist_num) == 0:
                reply_message = '尚未有您下單的紀錄喔!'
            else:
                reply_message = '您要取消哪筆訂單呢?請輸入訂單編號!'
                registered_data[user_id]['State'] = 'delorder'
                with open(RegisteredData_path, 'w', encoding='utf-8') as file:
                    json.dump(registered_data, file, ensure_ascii=False, indent=4)
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_message))
        elif '笑話' in text:
            with open('.\joke.json', 'r', encoding='utf-8') as file:
                joker = json.load(file)
            import random
            num = random.randrange(len(joker['笑話']))
            reply = joker['笑話'][num ]
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))
        else:
            reply = '目前沒有此項功能喔，請重新輸入'
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))

        
    elif registered_data[user_id].get('State') == 'changedata':  # 修改資料
        data_need = ['姓名', '電話', '地址']
        if  text == '是':
            reply = '請輸入您的{}'.format(data_need[0])
            registered_data[user_id]['State'] = 'registing'
            for data in data_need:
                del registered_data[user_id][data]
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))
        elif text == '否':
            reply = '取消修改資料'
            registered_data[user_id]['State'] = 'normal'
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))
        else:
            reply = '輸入錯誤，請重新輸入(是/否)'
            line_bot_api.reply_message(
                event.reply_token, 
                TextSendMessage(
                    text=reply,
                    quick_reply=QuickReply(
                        items=[
                            QuickReplyButton(action=MessageAction(label='是', text='是')),
                            QuickReplyButton(action=MessageAction(label='否', text='否'))
                        ]
                    )
                )
            )
        with open(RegisteredData_path, 'w', encoding='utf-8') as file:
            json.dump(registered_data, file, ensure_ascii=False, indent=4)


    elif registered_data[user_id].get('State') == 'checkorder':  # 確認訂貨
        order_num = registered_data[user_id].get('Order')  # 抓取發出訊息訂單號碼
        order_path = 'uncheck_orders/'+str(order_num)+'.xlsx'
        if not os.path.isfile(order_path):
            reply = '系統未儲存到此筆訂單，麻煩請重新下單'
            registered_data[user_id]['State'] = 'normal'
            registered_data[user_id]['Order'] = ''
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))
        else:
            if text == '是':
                reply = ['訂單已確認','請輸入希望的到貨時間: 早上/中午/晚上/不指定']
                registered_data[user_id]['State'] = 'checktime'
                df = pd.read_excel(order_path)[['顧客名稱', '訂單編號', '下單時間', '商品號碼', '商品', '價格', '數量', '總計']]  # 訂單詳細資料(df)
                df.insert(8,'總金額',df['總計'].sum(0))
                df.to_excel(order_path)

                line_bot_api.reply_message(
                    event.reply_token, 
                    messages=[
                        TextSendMessage(text=reply[0]),
                        TextSendMessage(
                            text=reply[1],
                            quick_reply=QuickReply(
                                items=[
                                    QuickReplyButton(action=MessageAction(label='早上',text='早上')),
                                    QuickReplyButton(action=MessageAction(label='中午',text='中午')),
                                    QuickReplyButton(action=MessageAction(label='晚上',text='晚上')),
                                    QuickReplyButton(action=MessageAction(label='不指定',text='不指定'))
                                ]
                            )
                        )
                    ]   
                )
            elif text == '否':
                reply = '將取消訂單，請重新下單'
                registered_data[user_id]['State'] = 'normal'
                registered_data[user_id]['Order'] = ''
                os.remove(order_path)  # 刪除暫存訂單
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))
            else:
                reply = '輸入錯誤，請重新輸入(是/否)'
                line_bot_api.reply_message(
                    event.reply_token, 
                    TextSendMessage(
                        text=reply,
                        quick_reply=QuickReply(
                            items=[
                                QuickReplyButton(action=MessageAction(label='是', text='是')),
                                QuickReplyButton(action=MessageAction(label='否', text='否'))
                            ]
                        )
                    )
                )
        with open(RegisteredData_path, 'w', encoding='utf-8') as file:
                json.dump(registered_data, file, ensure_ascii=False, indent=4)  


    elif registered_data[user_id].get('State') == 'checktime':  # 確認到貨時間
        order_num = registered_data[user_id]['Order']  # 抓取發出訊息訂單號碼
        order_path = 'uncheck_orders/'+str(order_num)+'.xlsx'
        df = pd.read_excel(order_path)[['顧客名稱', '訂單編號', '下單時間', '商品號碼', '商品', '價格', '數量', '總計', '總金額']]  # 訂單詳細資料(df)
        df_a = pd.read_excel('orders/check_orders.xlsx')[['顧客名稱','訂單編號','下單時間','商品號碼','商品','價格','數量','總計','總金額','備註']]
        remind = '!如欲刪除訂單，請於訂單確認後3天內取消訂單。當您收到出貨通知，便無法取消訂單。'
        if text == '早上':
            df.insert(9,'備註','早上送達')
            df_a = pd.concat([df, df_a])
            reply = '我們將於早上為您送到{}'.format(remind)
            reply_message=TextSendMessage(text=reply)
            registered_data[user_id]['State'] = 'normal'
            registered_data[user_id]['Order'] = ''
            os.remove(order_path)  # 刪除暫存訂單
        elif text == '中午':
            df.insert(9,'備註','中午送達')
            df_a = pd.concat([df, df_a])
            reply = '我們將於中午為您送到{}'.format(remind)
            reply_message=TextSendMessage(text=reply)
            registered_data[user_id]['State'] = 'normal'
            registered_data[user_id]['Order'] = ''
            os.remove(order_path)  # 刪除暫存訂單
        elif text == '晚上':
            df.insert(9,'備註','晚上送達')
            df_a = pd.concat([df, df_a])
            reply = '我們將於晚上為您送到{}'.format(remind)
            reply_message=TextSendMessage(text=reply)
            registered_data[user_id]['State'] = 'normal'
            registered_data[user_id]['Order'] = ''
            os.remove(order_path)  # 刪除暫存訂單
        elif text == '不指定':
            df.insert(9,'備註','不指定送貨時間')
            df_a = pd.concat([df, df_a])
            reply = '我們將會為您安排合適的時間寄出{}'.format(remind)
            reply_message=TextSendMessage(text=reply)
            registered_data[user_id]['State'] = 'normal'
            registered_data[user_id]['Order'] = ''
            os.remove(order_path)  # 刪除暫存訂單
        else:
            reply = '請重新輸入希望的到貨時間: 早上/中午/晚上/不指定'
            reply_message=TextSendMessage(
                text=reply,
                quick_reply=QuickReply(
                    items=[
                        QuickReplyButton(action=MessageAction(label='早上',text='早上')),
                        QuickReplyButton(action=MessageAction(label='中午',text='中午')),
                        QuickReplyButton(action=MessageAction(label='晚上',text='晚上')),
                        QuickReplyButton(action=MessageAction(label='不指定',text='不指定'))
                    ]
                )
            )
        df_a.to_excel('orders/check_orders.xlsx')
        line_bot_api.reply_message(event.reply_token, messages=reply_message)  
        with open(RegisteredData_path, 'w', encoding='utf-8') as file:
                json.dump(registered_data, file, ensure_ascii=False, indent=4)  

             
    elif registered_data[user_id].get('State') =='delorder':  # 刪除訂單
        df_col = ['顧客名稱','訂單編號','下單時間','商品號碼','商品','價格','數量','總金額','備註']
        shiftday = pd.to_datetime(datetime.date.today()-datetime.timedelta(days=3)) #三天前的時間
        order_col = ['商品', '價格', '數量']
        df = pd.read_excel('orders/check_orders.xlsx')[df_col]
        df_returnable = df[df['下單時間']>shiftday]
        try:
            df_returnlist_num = sorted(list(set(list(df_returnable[ df_returnable['顧客名稱']==registered_data[user_id]['姓名']]['訂單編號']))))
            if int(text) in df_returnlist_num:
                df = df[df['訂單編號']==int(text)]
                reply = '您要刪除的訂單如下:\n訂單編號:{}\n下單時間:{}\n總金額:{}\n'.format(str(text),str(df.iloc[0]['下單時間']),str(df.iloc[0]['總金額']))
                for i in range(len(df)):
                    for j in order_col:
                        if j=='商品' and '色度:' in df.iloc[i][j]:
                            df_split = df.iloc[i][j].split('色')
                            string = str(j)+':'+str(df_split[0])+'\n色'+str(df_split[1])+'\n'
                        else:    
                            string = str(j)+':'+str(df.iloc[i][j])+'\n'
                        if j=='數量':
                            string+='\n'
                        reply+=string
                reply = reply[:-2]
                registered_data[user_id]['State'] = 'delorder_check'
                registered_data[user_id]['delet_order'] = int(text)
                reply_message=[
                    TextSendMessage(text=reply),
                    TextSendMessage(
                        text='確認要取消此筆訂單嗎?🤔請輸入(是/否)',
                        quick_reply=QuickReply(
                            items=[
                                QuickReplyButton(action=MessageAction(label='是',text='是')),
                                QuickReplyButton(action=MessageAction(label='否',text='否'))
                                    ]
                        )
                    )
                ]
                line_bot_api.reply_message(event.reply_token, messages=reply_message)
            else:
                reply = '您的訂單編號輸入錯誤!您可取消的訂單如下:\n'
                for i in df_returnlist_num:
                    reply +=str(i)+'\n'
                reply+='請重新輸入欲取消的訂單編號'
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))
        except:
            reply = '您的訂單編號輸入錯誤!您可取消的訂單如下:\n'
            for i in df_returnlist_num:
                reply +=str(i)+'\n'
            reply+='請重新輸入欲取消的訂單編號'
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))
        with open(RegisteredData_path, 'w', encoding='utf-8') as file:
            json.dump(registered_data, file, ensure_ascii=False, indent=4)
       

    elif registered_data[user_id].get('State') =='delorder_check':  # 刪除訂單確認
        if text == '是':
            reply = '訂單已取消'
            df = pd.read_excel('orders/check_orders.xlsx')
            df_fillter =df[df['訂單編號']!=registered_data[user_id]['delet_order']]
            df_fillter.to_excel('orders/check_orders.xlsx')
            df_delet = pd.read_excel('orders/delet_order.xlsx')[['顧客名稱','訂單編號','下單時間','商品號碼','商品','價格','數量','總計','總金額','備註']]
            df_delet_filter = pd.concat([df[df['訂單編號']==registered_data[user_id]['delet_order']], df_delet])
            df_delet_filter.to_excel('orders/delet_order.xlsx')
            registered_data[user_id]['State'] = 'normal'
            registered_data[user_id]['delet_order'] = ''
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply)) 
        elif text == '否':
            reply_1 = '好的😊'
            reply_2 = '提醒您，如欲取消訂單，請於訂單確認後3天內取消訂單!'
            reply_message=[
                TextSendMessage(text=reply_1),
                TextSendMessage(text=reply_2)
            ]
            registered_data[user_id]['State'] = 'normal'
            registered_data[user_id]['delet_order'] = ''
            line_bot_api.reply_message(event.reply_token, messages=reply_message)
        else:
            reply = '輸入錯誤，請重新輸入(是/否)'
            line_bot_api.reply_message(
                event.reply_token, 
                TextSendMessage(
                    text=reply,
                    quick_reply=QuickReply(
                        items=[
                            QuickReplyButton(action=MessageAction(label='是', text='是')),
                            QuickReplyButton(action=MessageAction(label='否', text='否'))
                        ]
                    )
                )
            )
        with open(RegisteredData_path, 'w', encoding='utf-8') as file:
            json.dump(registered_data, file, ensure_ascii=False, indent=4)  


class Get_Neworder(threading.Thread):  # 抓出訂單詳細資料以做處理
    
    def __init__(self, name, queue):
        threading.Thread.__init__(self, name=name)
        self.__running = threading.Event()   # 用於停止執行緒的標識
        self.__running.set()   # 將running設定為True
        self.name = name
        self.queue = queue
        
    def run(self):
        while self.__running.isSet():
            print(threading.current_thread())
            order = self.queue.get()  # 將新的dataframe抓出queue(列隊)
            print('訂單資訊:{}\n'.format(order))
            time.sleep(1)
            name = order['顧客名稱'][0]
            order_num = order['訂單編號'][0]
            order_total = order['總計'].sum()
            order_col = ['商品', '價格', '數量']
            order_detail = order[order_col]
            order_data = ''
            for i in range(len(order_detail)):
                for j in order_col:
                    if j=='商品' and '色度:' in order_detail.iloc[i][j]:
                        order_detail_split = order_detail.iloc[i][j].split('色')
                        string = str(j)+':'+str(order_detail_split[0])+'\n色'+str(order_detail_split[1])+'\n'
                    else:    
                        string = str(j)+':'+str(order_detail.iloc[i][j])+'\n'
                    if j=='數量':
                        string+='\n'
                    order_data+=string
            order_data = order_data[:-2]
            reply = '還未完成'
            for user_id,values in registered_data.items():
                if name ==  values.get('姓名'):
                    order.to_excel('uncheck_orders/'+str(order_num)+'.xlsx')
                    registered_data[user_id]['State'] = 'checkorder'
                    registered_data[user_id]['Order'] = str(order_num)
                    with open(RegisteredData_path, 'w', encoding='utf-8') as file:
                        json.dump(registered_data, file, ensure_ascii=False, indent=4)

                    reply = '訂單編號:{} \n訂購人姓名:{} \n訂單總金額:{} \n訂單資訊:\n{}'.format(order_num, name,order_total ,order_data )
                    reply_message=[
                        TextSendMessage(text='接收到一筆訂單，請確認後回覆(是/否)'),
                        TextSendMessage(
                            text=reply,
                            quick_reply=QuickReply(
                                items=[
                                    QuickReplyButton(action=MessageAction(label='是', text='是')),
                                    QuickReplyButton(action=MessageAction(label='否', text='否'))
                                ]
                            )
                        )
                    ]   
                    line_bot_api.push_message(user_id, messages=reply_message)
                    break
                else:
                    continue
            time.sleep(1)
    def stop(self):
        self.__running.clear()    # 設定為False  
        print(threading.current_thread())

class FlaskThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.__flag = threading.Event()   # 用於暫停執行緒的標識
        self.__flag.set()    # 設定為True
        self.__running = threading.Event()   # 用於停止執行緒的標識
        self.__running.set()   # 將running設定為True
    def run(self):
        while self.__running.isSet():
            self.__flag.wait()   # 為True時立即返回, 為False時阻塞直到內部的標識位為True後返回
            app.run()
            print(threading.current_thread())
    def pause(self):
        self.__flag.clear()   # 設定為False, 讓執行緒阻塞
        print(threading.current_thread())
    def resume(self):
        self.__flag.set()  # 設定為True, 讓執行緒停止阻塞
        print(threading.current_thread())
    def stop(self):
        self.__running.clear()    # 設定為False  
        print(threading.current_thread())

def OpenFlask():
    app.run()

if __name__ == "__main__": 
    line_bot_api.set_default_rich_menu(rich_menu_id_start) 
    if not os.path.isfile('orders/check_orders.xlsx'):
        df_order = pd.DataFrame(columns=['顧客名稱','訂單編號','下單時間','商品號碼','商品','價格','數量','總計','總金額','備註'])
        df_order.to_excel('orders/check_orders.xlsx')
    if  not os.path.isfile('orders/delet_order.xlsx'):
        df_delet = pd.DataFrame(columns=['顧客名稱','訂單編號','下單時間','商品號碼','商品','價格','數量','總計','總金額','備註'])
        df_delet.to_excel('orders/delet_order.xlsx')
    if not os.path.isfile('./registered_data.json'):
        with open('registered_data.json', 'w', encoding='utf-8') as file:
            json.dump({}, file, ensure_ascii=False, indent=4)
    orders = Queue()
    takeorder = Take_Neworder(name='takeorder', queue=orders)
    getorder = Get_Neworder(name='getorder', queue=orders)
    flaskthread = threading.Thread(target=OpenFlask, args=())
    flaskthread.start()
    print(threading.current_thread())
    while True:
        command = input()
        if command == 'Start':  # 開啟webcrawling thread
            takeorder.start()
            getorder.start()
        elif command == 'Pause': # 暫停webcrawling thread
            takeorder.pause()
        elif command == 'Resume': # 繼續webcrawling thread
            takeorder.resume()
        elif command == 'Stop': # 停止webcrawling thread
            takeorder.stop()
            getorder.stop()
            break
    flaskthread.join()
    print(threading.current_thread())


    
    
    

    
