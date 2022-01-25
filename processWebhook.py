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





api = Api(app)
db_username = 'adveneerice'
db_password = 'adveneerice123'
db_name = 'adveneericeDB'
cluster = MongoClient(
    'mongodb+srv://adveneerice:adveneerice123@cluster0.blq7j.mongodb.net/myFirstDatabase?retryWrites=true&w=majority')
db = cluster['Hikaya']
user_collection = db['Report']





class Testing(Resource):

    def get(self):
        # Note: the uidk is just a default value when searchBy identifier is not provided
        # Note: some identifiers may be not unique...
        profile = user_collection.find_one({'name':'ali'})



        return json.loads(json_util.dumps(profile))








api.add_resource(Testing, '/get_random_story')






if __name__ == "__main__":
    app.secret_key = 'ItIsASecret'
    app.debug = True
    app.run()