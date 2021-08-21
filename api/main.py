import flask

import links
import my_json

app = flask.Flask(__name__)


@app.route("/", type=['POST'])
def hello_world():
    if flask.request.content_type != 'application/json':
        flask.abort(400)
    else:
        data = flask.request.json
        if data['type'] == 'link':
            links.process(data['data'].split(';'))
        else:
            my_json.process(data['data'])


app.run(host='0.0.0.0')
