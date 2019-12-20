import os
from flask import Flask, render_template, request
import dotenv
import requests
import base64
import json
import re
import time
# import pprint

dotenv.load_dotenv()

app = Flask(__name__)


def request_to_gcp(image):
    context = base64.b64encode(image.read()).decode()
    img_requests = [{
        'image': {
            'content': context
        },
        'features': [{
            'type': 'TEXT_DETECTION',
            'maxResults': 1
        }]
    }]
    response = requests.post(os.environ.get("GOOGLE_ENDPOINT"),
                             data=json.dumps({'requests': img_requests}).encode(),
                             params={'key': os.environ.get("GOOGLE_API_KEY")},
                             headers={'Content-Type': 'application/json'}).json()
    return response


def extract_jan(response_text):
    jans = re.findall('[0-9]{13}', response_text)
    if not jans:
        digested_text = response_text.replace('\"', '').replace(' ', '').replace('l', '')
        jans = re.findall('[0-9]{13}', digested_text)
    return jans


def request_to_rakuten(jans):
    item_list = []
    for jan in jans:
        payload = {'applicationId': os.environ.get("RAKUTEN_APPLICATION_ID"), 'keyword': jan, 'hits': 1}
        response = requests.get(os.environ.get("RAKUTEN_ENDPOINT"), params=payload).json()
        try:
            item_list.append(response['Items'][0]['Item'])
        except IndexError:
            pass
        time.sleep(1)
    return item_list


def request_to_yahoo(jans):
    item_list = []
    for jan in jans:
        payload = {'appid': os.environ.get("YAHOO_CLIENT_ID"), 'jan': jan, 'hits': 1}
        response = requests.get(os.environ.get("YAHOO_ENDPOINT"), params=payload).json()
        item = response['ResultSet']['0']['Result']['0']
        if item == {'_attributes': {'index': '0'}}:
            pass
        else:
            item_list.append(item)
    #     try:
    #         item_list.append(item)
    #     except IndexError:
    #         pass
    #     time.sleep(1)
    # item_list = [item for i, item in enumerate(item_list) if i % 2 == 0]
    return item_list


@app.route('/', methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if not request.files['image'].filename:
            return render_template('index.html', message='エラー！ファイルを選択してください')
        response = request_to_gcp(request.files['image'])
        jans = extract_jan(response['responses'][0]['textAnnotations'][0]['description'])
        item_list = request_to_rakuten(jans)
        item_list2 = request_to_yahoo(jans)
        if item_list or item_list2:
            message = '解析できました！'
        else:
            message = '解析できませんでした...'
        return render_template('index.html', item_list=item_list, item_list2=item_list2, message=message)
    else:
        return render_template('index.html')


if __name__ == '__main__':
    app.debug = True
    app.run()
