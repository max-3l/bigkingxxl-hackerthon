from flask import Flask
from flask_cors import CORS
from lorem_text import lorem
import time

app = Flask(__name__)
CORS(app)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route('/stream')
def generate_large_json():
    response = lorem.paragraph()
    def generate():
        for el in response:
            yield el
            print(el, end='')
            time.sleep(0.01)
        print()
    return app.response_class(generate(), mimetype='text/text')
