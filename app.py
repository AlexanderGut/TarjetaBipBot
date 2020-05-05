import os

from flask import Flask
from flask_restful import Api
from saldobip import init_routes

app = Flask(__name__)

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

api = Api(app)
init_routes(api)

if os.getenv('PROJECT_ENV') == 'dev':
    app.run(host="0.0.0.0")
