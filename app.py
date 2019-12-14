import os
from flask import Flask, render_template, request
import dotenv
import requests
import base64
import json
import re
import time

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
            # 'maxResults': 5
            'maxResults': 1
        }]
    }]
    response = requests.post(os.environ.get("GOOGLE_ENDPOINT"),
                             data=json.dumps({
                                 'requests': img_requests
                             }).encode(),   # .encode()
                             params={'key': os.environ.get("GOOGLE_API_KEY")},
                             headers={'Content-Type': 'application/json'}).json()
    print(response['responses'][0]['fullTextAnnotation']['text'])
    return response


def extract_jan(response_text):
    # digested_text = response_text.replace('\"', '').replace(' ', '').replace('\n', '')
    # jans = re.findall('\d{13}', digested_text)
    jans = re.findall('\d{13}', response_text)
    print(jans)
    if not jans:
        """バーコードがlに認識されることがあるため"""
        digested_text = response_text.replace('\"', '').replace(' ', '').replace('l', '')
        jans = re.findall('\d{13}', digested_text)
        print(jans)
    return jans


def request_to_rakuten(jans):
    item_list = []
    for jan in jans:
        payload = {'applicationId': os.environ.get("RAKUTEN_APPLICATION_ID"), 'keyword': jan, 'hits': 1}
        response = requests.get(os.environ.get("RAKUTEN_ENDPOINT"), params=payload).json()
        if len(response['Items']) > 0:
            item = response['Items'][0]['Item']
            print(item['itemName'])
            item_list.append(item)
            time.sleep(1)
    print(item_list)
    return item_list


@app.route('/', methods=["GET", "POST"])
def index():
    if request.method == "POST":
        response = request_to_gcp(request.files['image'])
        # print(response['responses'][0]['fullTextAnnotation']['text'])
        # response_text = process_str(response['responses'][0]['fullTextAnnotation']['text'])
        jans = extract_jan(response['responses'][0]['textAnnotations'][0]['description'])
        item_list = request_to_rakuten(jans)
        if item_list:
            message = '解析できました！'
        else:
            message = '解析できませんでした...'
        return render_template('capture.html', item_list=item_list, message=message)
    else:
        return render_template('capture.html')


if __name__ == '__main__':
    app.debug = True
    app.run()
