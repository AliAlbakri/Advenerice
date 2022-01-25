import flask
import os
from flask import send_from_directory

from bson import json_util, ObjectId
from flask_restful import Api, Resource, reqparse
from pymongo import MongoClient
import json

app = flask.Flask(__name__)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/favicon.png')

@app.route('/')
@app.route('/home')
def home():
    return "Hello World new API"







if __name__ == "__main__":
    app.secret_key = 'ItIsASecret'
    app.debug = True
    app.run()