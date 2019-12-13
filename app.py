import os
from flask import Flask, render_template, request
import dotenv
import requests
import base64
import json
import re

dotenv.load_dotenv()

app = Flask(__name__)


def get_str(image):
    context = base64.b64encode(image.read()).decode()   # decode()する必要ある？
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
                             }).encode(),   # .encode()？
                             params={'key': os.environ.get("GOOGLE_API_KEY")},
                             headers={'Content-Type': 'application/json'}).json()
    # print(response['responses'][0]['fullTextAnnotation']['text'])
    return response


def extract_jan(response_text):
    digested_text = response_text.replace('\"', '').replace(' ', '').replace('\n', '')
    print(digested_text)
    result = re.findall('\d{13}', digested_text)
    print(result)
    return result


@app.route('/', methods=["GET", "POST"])
def index():
    if request.method == "POST":
        response = get_str(request.files['image'])
        # print(response['responses'][0]['fullTextAnnotation']['text'])
        # response_text = process_str(response['responses'][0]['fullTextAnnotation']['text'])
        response_text = extract_jan(response['responses'][0]['textAnnotations'][0]['description'])
        return render_template('capture.html', response_text=response_text)
    else:
        return render_template('capture.html')


if __name__ == '__main__':
    app.debug = True
    app.run()
