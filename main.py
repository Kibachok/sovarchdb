from flask import Flask

app = Flask(__name__)


@app.route('/')
@app.route("/index")
def index():
    return open('static/html/index.html', encoding='utf-8', mode='r')


if __name__ == "__main__":
    app.run(port=8080, host='127.0.0.1')
