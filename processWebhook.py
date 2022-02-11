import flask
import os
from flask import request,send_from_directory,render_template
from bson import json_util, ObjectId
from flask_restful import Api, Resource, reqparse
from pymongo import MongoClient
import json
import datetime
from hashlib import sha256


# these are necessary decorations , do not tech them please
app = flask.Flask(__name__)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/favicon.png')
@app.route('/')
@app.route('/home')
def home():
    return render_template('endpoints.html')


# the fun starts here .....





api = Api(app)
db_username = 'adveneerice'
db_password = 'adveneerice123'
db_name = 'adveneericeDB'
cluster = MongoClient(
    'mongodb+srv://adveneerice:adveneerice123@cluster0.blq7j.mongodb.net/myFirstDatabase?retryWrites=true&w=majority')


db = cluster['adveneerice']
user_collection = db['User']
service_provider = db['Service_Provider']




class CreateUser(Resource):
    # creating a new user
    # Note: sex types are 'male', 'female' and 'undetermined'
    # Note: status are 'active', 'banned'
    # Note: read later title is going to be customized in frontend


    def put(self):

        # check if email is unique
        if ( not IsEmailUnique(request.json['email'])):
            response = {
                "message": 'The email is not unique,please choose another email',
                "messageAr": "البريد الالكتروني موجود من قبل، رجاء حاول استخدام بريد الكتروني اخر"
            }
            return response, 400


        user_info_profile = {
            # Commented feilds may be used later
            # "uid": request.json['uid'], may be used for auth
            # "username": request.json['username'],
            "fname": request.json['name'],
            "lname": request.json['name'],
            "email": request.json['email'],
            'password' : SHA256(request.json['password']),
            "bio": '',
            "sex": 'undetermined',
            'isActive':True,
            # "profileImage": request.json['profileImage'],
            # 'birthDate': request.json['birthDate'],
            "createdAt": str(datetime.datetime.utcnow()),
            "regestred_activities": None
        }

        uid = user_collection.insert_one(user_info_profile).inserted_id
        print(uid)

        return  {"user_id": f'{uid}'},201





class Login(Resource):

    def put(self):
        email =  request.json['email']


        user = getUserProfile(user_collection.find_one({'email':email}))

        if user and user['password'] == SHA256(request.json['password']):
            user_id = str(user["_id"]["$oid"])
            return {"status": "granted","user_id":user_id},200

        else:
            return {"status":"email or password invalid, try again"},400




class Profile(Resource):


    def get(self):
        # note that getting a user profile  can be done by user id or email (unique params)
        search_by = request.args['searchBy']
        value = request.args[search_by]
        profile = None
        if search_by == 'email':
         profile = getUserProfile(user_collection.find_one({search_by:value}))

        if search_by == 'user_id' and ObjectId.is_valid(value) :
            profile = getUserProfile(user_collection.find_one({"_id": ObjectId(value)}))

        if profile:
            profile.pop('password',None)
            return profile,200

        else:
            response = {
                "message": 'The profile does not exist',
                "messageAr": "الحساب غير موجود"
            }
            return response, 400




class CreateUserProvider(Resource):


    def put(self):

        # check if email is unique
        if ( not IsEmailUnique(request.json['email'])):
            response = {
                "message": 'The email is not unique,please choose another email',
                "messageAr": "البريد الالكتروني موجود من قبل، رجاء حاول استخدام بريد الكتروني اخر"
            }
            return response, 400


        user_info_profile = {

            "company_name": request.json['company_name'],
            "email": request.json['email'],
            'password' : SHA256(request.json['password']),
            "bio": '',
            "sex": 'undetermined',
            'isActive':True,
            # "profileImage": request.json['profileImage'],
            # 'birthDate': request.json['birthDate'],
            "createdAt": str(datetime.datetime.utcnow()),
            "provided_activities": [{
                "name":"",
                "description":"",
                "image":""
            }]
        }

        uid = user_collection.insert_one(user_info_profile).inserted_id
        print(uid)

        return  {"user_id": f'{uid}'},201






api.add_resource(CreateUser, '/create_user')
api.add_resource(Login, '/login')
api.add_resource(Profile,'/get_user_profile')







def SHA256(password):
    return sha256(password.encode('utf-8')).hexdigest()

def IsEmailUnique(email):
    not_unique_email = None
    not_unique_email = user_collection.find_one({'email': email})


    if not_unique_email:
        return False
    else:
        return True

def getUserProfile(mongo_user):
    return json.loads(json_util.dumps(mongo_user))








if __name__ == "__main__":
    app.run(debug=True)