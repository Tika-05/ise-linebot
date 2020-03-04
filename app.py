#-*- coding: utf-8 -*-

#  Licensed under the Apache License, Version 2.0 (the "License"); you may
#  not use this file except in compliance with the License. You may obtain
#  a copy of the License at
#
#       https://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#  WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#  License for the specific language governing permissions and limitations
#  under the License.


# インポートするライブラリ
from flask import Flask, request, abort, render_template, jsonify

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    FollowEvent, MessageEvent, TextMessage, TextSendMessage, ImageMessage,
    ImageSendMessage, TemplateSendMessage, ButtonsTemplate, PostbackTemplateAction,
    MessageTemplateAction, URITemplateAction, VideoMessage, AudioMessage, StickerMessage,
    URIAction, RichMenu, DatetimePickerTemplateAction, PostbackEvent, LocationMessage, LocationSendMessage, CarouselColumn, CarouselTemplate
)
import os
import sys
import requests
import json
import random
import datetime

# 軽量なウェブアプリケーションフレームワーク:Flask
# flaskの定義をする
app = Flask(__name__)

#環境変数からLINE Access Tokenを設定
LINE_CHANNEL_ACCESS_TOKEN = os.environ["LINE_CHANNEL_ACCESS_TOKEN"]
#環境変数からLINE Channel Secretを設定
LINE_CHANNEL_SECRET = os.environ["LINE_CHANNEL_SECRET"]
# webhookURL
BOT_SERVER_URL = "https://ise-linebot.herokuapp.com/"
# グルナビAPI
# GNAVI_API_KEY = os.environ["GNAVI_API_KEY"]
GNAVI_API_KEY = "7df810893c166d344a1d660a15d8f294"
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

if GNAVI_API_KEY is None:
    print('GNAVI_API_KEYがないっすよ')
    sys.exit(1)

# ぐるなびAPI URL
RESTSEARCH_URL = "https://api.gnavi.co.jp/RestSearchAPI/v3/"
DEF_ERR_MESSAGE = """
申し訳ありません、データを取得できませんでした。
少し時間を空けて、もう一度試してみてください。
"""
NO_HIT_ERR_MESSAGE = "お近くにぐるなびに登録されている喫茶店はないようです" + chr(0x100017)
LINK_TEXT = "ぐるなびで見る"
IMAGE_URL = "a.png"


# ぐるなびAPI利用１　（全部見る）
def call_restsearch():
    # ぐるなびAPIに接続して取得
    # params = {
    #     "keyid": GNAVI_API_KEY,
    #     "latitude": latitude,
    #     "longitude": longitude,
    #     "range": 5
    # }
    # response = requests.get(RESTSEARCH_URL, params)
    # result = response.json()
    # # print(result)
    # if "error" in result:
    #     if "message" in result:
    #         raise Exception("{}".format(result["message"]))
    #     else:
    #         raise Exception(DEF_ERR_MESSAGE)
    # # ヒットする飲食店がなかったら
    # total_hit_count = result.get("total_hit_count", 0)
    # if total_hit_count < 1:
    #     raise Exception(NO_HIT_ERR_MESSAGE)

    f = open("gunavi.json", 'r')
    result =  json.load(f) #JSON形式で読み込む

    # 取得したい飲食店データのみにする
    response_json_list = []
    for (count, rest) in enumerate(result.get("rest")):
        # 店舗名
        name = rest.get("name", "")
        # 店舗名かな
        # カテゴリー
        category = rest.get("category", "")
        # サイトurl
        url = rest.get("url", "")
        # url = rest.get("url_mobile", "")
        # 店舗画像
        image_url = rest.get("image_url", {})
        if image_url.get("shop_image1", "") != "":
            image = image_url.get("shop_image1", "")
        elif image_url.get("shop_image2", "") != "":
            image = image_url.get("shop_image2", "")
        else:
            image = BOT_SERVER_URL + "/static/{}".format(IMAGE_URL)
        # アドレス
        # address = "住所: {}".format(rest.get("address", ""))
        # 電話番号
        # tell = "電話番号: {}".format(rest.get("tell", ""))
        # 開店時間
        opentime = "営業時間: {}".format(rest.get("opentime", ""))
        # 定休日
        holiday = "定休日: {}".format(rest.get("holiday", ""))
        # アクセス
        access = rest.get("access", {})
        access_info = "{0}  {1}分".format(access.get("station", ""), access.get("walk", ""))
        # 平均予算
        # budget = "平均予算: {}".format(rest.get("budget", ""))
        # PR文
        # pr = rest.get("pr", "")
        # pr_short = pr.get("pr_short", "")

        result_text = category + "\n" + opentime + "\n" + holiday + "\n" + access_info
        if len(result_text) > 60:
            result_text = result_text[:56] + "..."

        result_dict = {
            "thumbnail_image_url": image,
            "title": name,
            "text": result_text,
            "actions": {
                "label": "ぐるなびで見る",
                "uri": url
            }
        }
        response_json_list.append(result_dict)

    return response_json_list

# カルーセルテンプレート作成
def carouselTemplate(j):
    columns = [
        CarouselColumn(
            thumbnail_image_url=column["thumbnail_image_url"],
            title=column["title"],
            text=column["text"],
            actions=[
                URITemplateAction(
                    label=column["actions"]["label"],
                    uri=column["actions"]["uri"],
                )
            ]
        )
        for column in j
    ]

    messages = TemplateSendMessage(
        alt_text="飲食店の情報をお伝えします。",
        template=CarouselTemplate(columns=columns),
    )
    print("messages is: {}".format(messages))
    return messages




# ぐるなびAPI利用２　（ランダムで一つ）
def call_restsearch2():
    # ぐるなびAPIに接続して取得
    # params = {
    #     "keyid": GNAVI_API_KEY,
    #     "latitude": latitude,
    #     "longitude": longitude,
    #     "range": 5
    # }
    # response = requests.get(RESTSEARCH_URL, params)
    # result = response.json()
    # # print(result)
    # if "error" in result:
    #     if "message" in result:
    #         raise Exception("{}".format(result["message"]))
    #     else:
    #         raise Exception(DEF_ERR_MESSAGE)
    # # ヒットする飲食店がなかったら
    # total_hit_count = result.get("total_hit_count", 0)
    # if total_hit_count < 1:
    #     raise Exception(NO_HIT_ERR_MESSAGE)

    f = open("gunavi.json", 'r')
    result =  json.load(f) #JSON形式で読み込む


    # 取得したい飲食店データのみにする
    r = result.get("rest")
    i = random.randint(0,len(r)-1)
    # 店舗名
    name = r[i].get("name", "")
    # 店舗名かな
    # カテゴリー
    category = r[i].get("category", "")
    # サイトurl
    url = r[i].get("url", "")
    # url = r[i].get("url_mobile", "")
    # 店舗画像
    image_url = r[i].get("image_url", {})
    if image_url.get("shop_image1", "") != "":
        image = image_url.get("shop_image1", "")
    elif image_url.get("shop_image2", "") != "":
        image = image_url.get("shop_image2", "")
    else:
        image = BOT_SERVER_URL + "/static/{}".format(IMAGE_URL)
    # 開店時間
    opentime = "営業時間: {}".format(r[i].get("opentime", ""))
    # 定休日
    holiday = "定休日: {}".format(r[i].get("holiday", ""))
    # アクセス
    access = r[i].get("access", {})
    access_info = "{0}  {1}分".format(access.get("station", ""), access.get("walk", ""))
    result_text = category + "\n" + opentime + "\n" + holiday + "\n" + access_info
    if len(result_text) > 60:
        result_text = result_text[:56] + "..."

    result_dict = {
        "thumbnail_image_url": image,
        "title": name,
        "text": result_text,
        "actions": {
            "label": "ぐるなびで見る",
            "uri": url
        }
    }
    return result_dict

# テンプレートメッセージ
def template(j):
    message_template = TemplateSendMessage(
        # 代替テキスト（何らかの原因でテンプレートが表示できなかった場合に代わりに表示されるテキスト）
        alt_text="ボタンテンプレート",
        template=ButtonsTemplate(
            text = j["text"],
            title = j["title"],
            # cover：画像領域全体に画像を表示します。contain：画像領域に画像全体を表示します。
            image_size="contain",
            # 任意の画像
            thumbnail_image_url = j["thumbnail_image_url"],
            # urlに飛ぶ
            actions=[
                URIAction(
                    uri = j["actions"]["url"],
                    label = j["actions"]["label"]
                )
            ]
        )
    )
    return message_template



# "/"にGETリクエストを送ると、index.htmlを返す  (ルートのアドレスに以下のものを配置することを明言)
@app.route('/', methods=['GET'])
def index():
    return 'ise'


# 送られてきたメッセージがくる場所　処理する場所？
@app.route("/callback", methods=['POST'])
def callback():
     # get X-Line-Signature header value
    # LINE側が送ってきたメッセージが正しいか検証する  (リクエストヘッダーに含まれる署名を検証して、リクエストがLINEプラットフォームから送信されたことを確認)
    signature = request.headers['X-Line-Signature']

    # ログ表示
    # get request body as text
    body = request.get_data(as_text=True)
    # プログラムの通常の操作中に発生したイベントの報告
    app.logger.info("Request body: " + body)
    # handle webhook body
    try:
        # 署名を検証し、問題なければhandleに定義されている関数を呼び出す
        handler.handle(body, signature)
    except InvalidSignatureError:
        # 署名検証で失敗したときは例外をあげる
        abort(400)

    #return 'OK'
    return jsonify({"state": 200})


# MessageEvent　テキストメッセージ受け取った時
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    text = event.message.text
    if 'こんにちは' in text:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='Hello World')
         )
    elif '日付' in text:
        date_picker = TemplateSendMessage(
            alt_text='予定日を設定',
            template=ButtonsTemplate(
                text='予定日を設定',
                title='YYYY-MM-dd',
                actions=[
                    DatetimePickerTemplateAction(
                        label='設定',
                        data='action=buy&itemid=1',
                        mode='date',
                        initial='2017-04-01',
                        min='2017-04-01',
                        max='2099-12-31'
                    )
                ]
            )
        )
    elif '近く' in text:
        f = call_restsearch2()
        m = template(f)
        line_bot_api.reply_message(
            event.reply_token,
            messages=m
        )
    elif 'どこか' in text:
        f = call_restsearch()
        m = carouselTemplate(f)
        line_bot_api.reply_message(
            event.reply_token,
            messages=m
        )
    else:
    	line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='「' + text + '」って何？')
         )


# 位置情報を受け取った時
@handler.add(MessageEvent, message=LocationMessage)
def handle_location_message(event):
    # ユーザーの緯度経度取得
    user_lat = event.message.latitude
    user_longit = event.message.longitude
    # ぐるなびAPIで探す
    # result = call_restsearch(user_lat, user_longit)
    # print("call_search_result is: {}".format(result))
    # m = carouselTemplate(result)
    m = "緯度：{0}  /  経度：{1}".format(user_lat, user_longit)
    line_bot_api.reply_message(
        event.reply_token,
        messages=m
    )


# 日時選択アクションの返信
@handler.add(PostbackEvent)
def handle_postback(event):
    print("選択した日付 "+ event.postback.params['date'])



# 画像、ビデオ、音声受け取った時
@handler.add(MessageEvent, message=(ImageMessage, VideoMessage, AudioMessage))
def handle_content_message(event):
    line_bot_api.reply_message(
           event.reply_token,
           TextSendMessage(text='あ、気に入ったので保存してサーバに上げときます笑')
    )

# スタンプ受け取った時
@handler.add(MessageEvent, message=StickerMessage)
def handle_sticker_message(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text='遊ばず働け！！！'),
        # StickerSendMessage(package_id=event.message.package_id,sticker_id=event.message.sticker_id)
    )


if __name__ == "__main__":
    port = int(os.getenv("PORT",8080))
    app.run(host="0.0.0.0", port=port)
