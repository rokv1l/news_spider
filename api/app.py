from flask import Flask
from flask_restful import Api

from resources.news import News, NewsEntities, NewsTags


app = Flask(__name__)
api = Api(app)

api.add_resource(News, '/get_news')
api.add_resource(NewsEntities, '/get_entities')
api.add_resource(NewsTags, '/get_tags')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=False)
