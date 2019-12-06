import os
from flask import Flask, render_template, request
import dotenv
import requests
import base64
import json
dotenv.load_dotenv()

app = Flask(__name__)


@app.route('/', methods=["GET", "POST"])
def hello_world():
    if request.method == "GET":
        print(os.environ.get("GOOGLE_API_KEY"))
        return render_template('capture.html')
    else:
        image = request.files['image']
        context = base64.b64encode(image.read()).decode()
        img_requests = [{
            'image': {
                'content': context
            },
            'features': [{
                'type': 'TEXT_DETECTION',
                'maxResults': 5
            }]
        }]
        response = requests.post(os.environ.get("GOOGLE_ENDPOINT"),
                                 data=json.dumps({
                                     'requests': img_requests
                                 }).encode(),
                                 params={'key': os.environ.get("GOOGLE_API_KEY")},
                                 headers={'Content-Type': 'application/json'}).json()
        print(response['responses'][0]['fullTextAnnotation']['text'])

        return render_template('show.html', image=image)


if __name__ == '__main__':
    app.debug = True
    app.run()
