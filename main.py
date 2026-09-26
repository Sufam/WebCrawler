import os
import sys
import json
import bs4
import requests
from flask import Flask, request, abort

from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

app = Flask(__name__)

#Read Token and Secret from env
channelAccessToken = os.getenv("API_token")
channelSecret = os.getenv("secret")

line_bot_api = LineBotApi(channelAccessToken)
handler = WebhookHandler(channelSecret)

def getData():
    datas = {}
    url = "https://alerts.ncdr.nat.gov.tw/RssAtomFeed.ashx?AlertType=33"
    
    try:
        require = requests.get(url, timeout=5)
        root = bs4.BeautifulSoup(require.text, "xml")
        information = root.find_all("entry")

        for i in information:
            date = i.find('updated').get_text().replace('-', '/', 3)[:10]
            summary_text = i.find('summary', type="html").get_text()[8:].strip(
                "行政院人事行政總處。如有任何問題請撥1999(縣市內直撥)08-7320415#6530、6535。03-5513522#334~"
            )
            
            if date not in datas:
                datas[date] = []
            datas[date].append(summary_text)
    except Exception as e:
        print(f"爬蟲抓取失敗: {e}")
        
    return datas

@app.route("/", methods=['GET', 'POST'])
def callback():
    if request.method == 'GET':
        return 'Line Bot Server is running!', 200

    signature = request.headers.get('X-Line-Signature', '')
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)
    except Exception as e:
        print(f"Error handling request: {e}")

    return 'OK', 200

# Message process
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_msg = event.message.text
    
    if "停班停課" in user_msg:
        datas = getData()
        if datas:
            message_list = []
            for date, contents in datas.items():
                content_text = "\n".join(contents)
                message_list.append(f"更新日期: {date}\n{content_text}")
            
            reply_text = f"近期停班停課資訊:\n\n" + "\n---\n".join(message_list)
        else:
            reply_text = "目前無相關停班停課更新資訊。"
            
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply_text)
        )
    else:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="該訊息非指定訊息")
        )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=True)
