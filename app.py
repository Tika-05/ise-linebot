#-*- coding: utf-8 -*-
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
    URIAction, RichMenu, DatetimePickerTemplateAction, PostbackEvent
)
import os
import json
import datetime

# 軽量なウェブアプリケーションフレームワーク:Flask
# flaskの定義をする
app = Flask(__name__)

#環境変数からLINE Access Tokenを設定
LINE_CHANNEL_ACCESS_TOKEN = os.environ["LINE_CHANNEL_ACCESS_TOKEN"]
#環境変数からLINE Channel Secretを設定
LINE_CHANNEL_SECRET = os.environ["LINE_CHANNEL_SECRET"]
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# ボタン押したらurlに飛ぶやつ
def make_button_template(Ctext, Ctitle, Cimageurl, Curl, Clabel):
    message_template = TemplateSendMessage(
        # 代替テキスト（何らかの原因でテンプレートが表示できなかった場合に代わりに表示されるテキスト）
        alt_text="ボタンテンプレート",
        template=ButtonsTemplate(
            text = Ctext,
            title = Ctitle,
            # cover：画像領域全体に画像を表示します。contain：画像領域に画像全体を表示します。
            image_size="contain",
            # 任意の画像
            thumbnail_image_url = Cimageurl,
            # urlに飛ぶ
            actions=[
                URIAction(
                    uri = Curl,
                    label = Clabel
                )
            ]
        )
    )
    return message_template


# "/"にGETリクエストを送ると、index.htmlを返す  (ルートのアドレスに以下のものを配置することを明言)
@app.route('/', methods=['GET'])
def index():
    return 'ise'

# @app.route('/imageup', methods=['GET'])
# def imageup():
#     return render_template('image.php')


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
    else:
    	line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='「' + text + '」って何？')
         )

#日時選択アクションの返信
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
