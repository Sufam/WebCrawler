import bs4, requests, json, os, sys
from flask import Flask, request

# 載入 LINE Message API 相關函式庫
from linebot import LineBotApi, WebhookHandler
from linebot.models import TextSendMessage

sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

def getData():
    global information

    datas = {}

    url = "https://alerts.ncdr.nat.gov.tw/RssAtomFeed.ashx?AlertType=33"
    require = requests.get(url)

    root = bs4.BeautifulSoup(require.text, "xml")
    information = root.find_all("entry")

    for i in information:
        date = i.find('updated').get_text().replace('-','/',3)[:10]
        if date in datas:
            datas[date].append(i.find('summary',type="html").get_text()[8:].strip("行政院人事行政總處。如有任何問題請撥1999(縣市內直撥)08-7320415#6530、6535。03-5513522#334~"))
        else:    
            datas = {}
            datas[date] = []
            datas[date].append(i.find('summary',type="html").get_text()[8:].strip("行政院人事行政總處。如有任何問題請撥1999(縣市內直撥)08-7320415#6530、6535。03-5513522#334~"))
    return datas

app = Flask(__name__)

@app.route("/", methods=['POST'])
def sendMessage():
    token = os.getenv("API_token")
    channel_Secret =os.getenv("secret")

    datas = getData()
    message = ""
    updateData = ""
    for i in datas:
        updateData = i
        message = "\n".join(datas[i])

    body = request.get_data(as_text=True)# 取得收到的訊息內容
    try:
        json_data = json.loads(body)# json 格式化訊息內容
        access_token = token
        secret = channel_Secret

        line_bot_api = LineBotApi(access_token)
        handler = WebhookHandler(secret)

        signature = request.headers['X-Line-Signature']# 加入回傳的 headers
        handler.handle(body, signature)# 綁定訊息回傳的相關資訊

        msg = json_data['events'][0]['message']['text']# 取得 LINE 收到的文字訊息
        tk = json_data['events'][0]['replyToken']# 取得回傳訊息的 Token

        if "停班停課" in msg:
            line_bot_api.reply_message(tk,TextSendMessage(f"近期停班停課資訊:\n更新日期:{updateData}\n{message}"))
        else:
            line_bot_api.reply_message(tk, TextSendMessage("該訊息非指定訊息"))
        print(msg, tk)
    except:
        print(body)

    return 'OK', 200
 
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=True)
