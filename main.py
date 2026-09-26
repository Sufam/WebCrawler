import bs4
import requests
import json


def change():
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


def update(datas):
    API_token = ""
    url = 'https://api.line.me/v2/bot/message/broadcast'
    token = API_token

    update_Date = ""
    message = ""
    for i in datas:
        update_Date = i
        message = i
        message = "\n".join(datas[i])

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }

    data = {
        "messages": [
            { "type": "text",
                "text": f'各縣市目前停班停課資訊:\n更新日期:{update_Date}\n{message}'
            } ]
    }

    requests.post(url, headers = headers, data = json.dumps(data))
 
if __name__ == "__main__":
    data = change()
    update(data)
 