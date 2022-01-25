import flask

import datetime
import json
import pymongo
from bson import json_util, ObjectId
from flask import Flask, request
from flask_restful import Api, Resource, reqparse
from pymongo import MongoClient
import os
from flask import send_from_directory


app = flask.Flask(__name__)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/favicon.png')

@app.route('/')
@app.route('/home')
def home():

    return "Hello World,awesome API is being built ..."






if __name__ == "__main__":
    app.debug = True
    app.run()


