from flask import Flask, request, render_template, jsonify
import requests

api_url = "http://127.0.0.1:5000/post"
app = Flask(__name__)

@app.route('/')
def home():
    return render_template("index.html")


@app.route('/', methods=['POST'])
def post_routes():
    routes = None
    data = {'destination': request.form['destination'], 'source': request.form['source']}
    r = requests.post(api_url, data=data)
    return render_template('index.html', routes = r.content)


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=8080)
