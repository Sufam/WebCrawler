import bs4
import datetime
import time
import json
import requests
import keyboard




datas = {}
date = datetime.date.today()

def change():
    global datas
    global date
    global information

    url = "https://alerts.ncdr.nat.gov.tw/RssAtomFeed.ashx?AlertType=33"
    data = requests.get(url)

    root = bs4.BeautifulSoup(data.text, "xml")
    information = root.find_all("entry")
    print(date)

    for i in information:
        date = i.find('updated').get_text().replace('-','/',3)[:10]
        if date in datas:
            datas[date].append(i.find('summary',type="html").get_text()[8:].strip("行政院人事行政總處。如有任何問題請撥1999(縣市內直撥)08-7320415#6530、6535。03-5513522#334~"))
        else:
            datas = {}
            datas[date] = []
            datas[date].append(i.find('summary',type="html").get_text()[8:].strip("行政院人事行政總處。如有任何問題請撥1999(縣市內直撥)08-7320415#6530、6535。03-5513522#334~"))
    #print(datas)


def update():
    global length
    global datas
        
    url = 'https://api.line.me/v2/bot/message/broadcast'
    token = 'API_Token'

    message = ""
    for i in datas:
        message = "".join(i)
        message = "\n".join(datas[i])

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }

    data = {
        "messages": [
            { "type": "text",
                "text": f'各縣市目前停班停課資訊：{date}\n{message}'
            } ]
    }
    print(message)

    requests.post(url, headers = headers, data = json.dumps(data))
    #if res.status_code in (200, 204):
    #    print(f"Request fulfilled with response: {res.text}")
    #else:
    #    print(f"Request failed with response: {res.status_code}-{res.text}")
    




while True:
    change()
    update()
    time.sleep(10)
    if keyboard.read_key() == "p":
        break
    
    

