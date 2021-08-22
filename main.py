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
            return {'results': links.process(data['data'])}
        else:
            return {'results': my_json.process(flask.request.file)}


app.run(host='127.0.0.1')
