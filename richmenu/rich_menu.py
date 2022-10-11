from flask import Flask, request, abort

from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (RichMenu, RichMenuArea,
                            RichMenuBounds, RichMenuSize, URIAction, MessageAction, PostbackAction, Action)

import configparser

import json
import os

app = Flask(__name__)  # 建立 Flask 物件

config = configparser.ConfigParser()
config.read('config.ini')

line_bot_api = LineBotApi(config.get('line-bot', 'channel-access-token'))
handler = WebhookHandler(config.get('line-bot', 'channel-secret'))

rich_menu_list = line_bot_api.get_rich_menu_list()
for data in rich_menu_list:
    #print(data.rich_menu_id)
    line_bot_api.delete_rich_menu(data.rich_menu_id)


#接收LINE資訊
@app.route("/callback", methods=['POST'])#裝飾器
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

rich_menu_start = RichMenu(
    size=RichMenuSize(width=2500, height=843),
    selected=True,
    name="開始使用",#圖文選單名字(不顯示)
    chat_bar_text="打開選單",#聊天室按鈕
    areas=[
        RichMenuArea(
        bounds=RichMenuBounds(x=0, y=0, width=2500, height=843),
        action=MessageAction(label='開始使用', text='開始使用')
        )
        ]#回覆訊息 p29 https://readthedocs.org/projects/line-bot-sdk-python/downloads/pdf/latest/
    )
rich_menu_id_start = line_bot_api.create_rich_menu(rich_menu=rich_menu_start)
with open(r'richmenu\start.png', 'rb') as f:
    line_bot_api.set_rich_menu_image(rich_menu_id_start, 'image/jpeg', f)

rich_menu_registing = RichMenu(
    size=RichMenuSize(width=2500, height=843),
    selected=True,
    name="註冊",#圖文選單名字(不顯示)
    chat_bar_text="打開選單",#聊天室按鈕
    areas=[
        RichMenuArea(
        bounds=RichMenuBounds(x=0, y=0, width=2500, height=843),
        action=MessageAction(label='註冊', text='註冊')
        )
        ]#回覆訊息 p29 https://readthedocs.org/projects/line-bot-sdk-python/downloads/pdf/latest/
    )
rich_menu_id_registing = line_bot_api.create_rich_menu(rich_menu=rich_menu_registing)
with open(r'richmenu\registing.png', 'rb') as f:
    line_bot_api.set_rich_menu_image(rich_menu_id_registing, 'image/jpeg', f)

rich_menu_normal = RichMenu(
    size=RichMenuSize(width=2500, height=1686),
    selected=True,
    name="註冊",#圖文選單名字(不顯示)
    chat_bar_text="打開選單",#聊天室按鈕
    areas=[
        RichMenuArea # x,y=0在圖文選單左上角
        (
        bounds=RichMenuBounds(x=0, y=843, width=850, height=843),
        action=MessageAction(label='左下', text='刪除訂單')
        ),
        RichMenuArea(
        bounds=RichMenuBounds(x=850 , y=843, width=800, height=843),
        #action種類:https://developers.line.biz/en/docs/messaging-api/actions/
        action=MessageAction(label='中下', text='查詢訂單')
        ),
        RichMenuArea
        (
        bounds=RichMenuBounds(x=1650, y=843, width=850, height=843),
        action=MessageAction(label='右下', text='修改資料')
        #action=PostbackAction(label='修改註冊資料',data='action=change_registed_data')   
        ),
        RichMenuArea(
        bounds=RichMenuBounds(x=0, y=0, width=800, height=843),
        #action種類:https://developers.line.biz/en/docs/messaging-api/actions/
        action=URIAction(label='左上商品', uri= 'https://ctpsxifajing.webnode.tw/%e7%94%b7%e6%80%a7/', alt_uri='https://www.google.com/')
        ),
        RichMenuArea
        (
        bounds=RichMenuBounds(x=850, y=0, width=850, height=843),
        action=URIAction(label='中上官網', uri= 'https://www.arimino-taiwan.tw/index.aspx', alt_uri='https://www.google.com/')
        ),
        RichMenuArea
        (
        bounds=RichMenuBounds(x=1650, y=0, width=850, height=843),
        action=URIAction(label='右上提問', uri= 'https://line.me/ti/p/2qhyfwQRwx', alt_uri='https://www.google.com/')
        #action=PostbackAction(label='修改註冊資料',data='action=change_registed_data')   
        )
        ]#回覆訊息 p29 https://readthedocs.org/projects/line-bot-sdk-python/downloads/pdf/latest/
    )
rich_menu_id_normal = line_bot_api.create_rich_menu(rich_menu=rich_menu_normal) 
with open(r'richmenu\normal.png', 'rb') as f:
    line_bot_api.set_rich_menu_image(rich_menu_id_normal, 'image/jpeg', f)

if __name__ == "__main__":
    if not os.path.isfile('./registered_data.json'):
        with open('registered_data.json', 'w', encoding='utf-8') as file:
            json.dump({}, file, ensure_ascii=False, indent=4)
    app.run()