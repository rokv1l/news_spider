from flask import Flask
from flask_restful import Api

from resources.news import GetNews


app = Flask(__name__)
api = Api(app)

api.add_resource(GetNews, '/get_news')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
