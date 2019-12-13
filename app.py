import os
from flask import Flask, render_template, request
import dotenv
import requests
import base64
import json
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
                             }).encode(),   # .encode()がわからない？
                             params={'key': os.environ.get("GOOGLE_API_KEY")},
                             headers={'Content-Type': 'application/json'}).json()
    # print(response['responses'][0]['fullTextAnnotation']['text'])
    return response


@app.route('/', methods=["GET", "POST"])
def index():
    if request.method == "POST":
        response = get_str(request.files['image'])
        print(response['responses'][0]['fullTextAnnotation']['text'])   # fullTextAnnotationはDOCUMENT_TEXT_DETECTIONの要素では？
        return render_template('capture.html', response=response)
    else:
        return render_template('capture.html')


if __name__ == '__main__':
    app.debug = True
    app.run()
