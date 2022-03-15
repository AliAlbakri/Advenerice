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
service_provider_collection = db['Service_Provider']




class CreateUser(Resource):
    # creating a new user
    # Note: sex types are 'male', 'female' and 'undetermined'
    # Note: status are 'active', 'banned'
    # Note: read later title is going to be customized in frontend


    def put(self):

        # check if email is unique
        if ( not IsEmailUnique(request.json['email'])):
            response = {
                "status": 'Error.The email is not unique,please choose another email'
            }

            return response, 400


        user_info_profile = {
            "username": request.json['username'],
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

        return  {"user_id": f'{uid}'},201





class LoginUser(Resource):

    def post(self):
        email = request.json['email']


        user = getJsonProfile(user_collection.find_one({'email':email}))

        if user and user['password'] == SHA256(request.json['password']):
            user_id = str(user["_id"]["$oid"])
            profile = getJsonProfile(user_collection.find_one({'email': email}))

            return profile, 201

        else:
            return {"status":"email or password invalid, try again"},400




class Profile(Resource):


    def get(self):
        # note that getting a user profile  can be done by user id or email (unique params)
        search_by = request.args['searchBy']
        value = request.args[search_by]
        profile = None
        if search_by == 'email':
         profile = getJsonProfile(user_collection.find_one({search_by:value}))

        if search_by == 'user_id' and ObjectId.is_valid(value) :
            profile = getJsonProfile(user_collection.find_one({"_id": ObjectId(value)}))

        if profile:
            profile.pop('password',None)
            return profile,200

        else:
            response = {
                "message": 'The profile does not exist',
                "messageAr": "الحساب غير موجود"
            }
            return response, 400


    def put(self):
        profile = getJsonProfile(user_collection.find_one({"_id": ObjectId(request.json["user_id"])}))
        response = {}
        notUniqueEmail = None
        if request.json['email'] != profile['email'] :
            if  not IsEmailUnique(request.json['email']) :
                notUniqueEmail = True
                response = {'status':'email not updated, choose a unique email '}


        updated_profile = { "username": request.json['username'], "bio": request.json['bio'],
                           "sex": request.json['sex'], "profileImage":request.json['profileImage']}

        if not notUniqueEmail:
            updated_profile['email'] = request.json['email']
            response = {'status':"profile updated"}




        user_collection.update_one(
            {'_id': ObjectId(request.json['user_id'])},
            {'$set': updated_profile}
        )
        profile = getJsonProfile(user_collection.find_one({"_id": ObjectId(request.json["user_id"])}))
        profile.pop('password', None)

        return profile,200



class SerivceProvider(Resource):



    # put is creating a new service provider
    def put(self):

        # check if email is unique
        if ( not IsEmailUnique(request.json['email'])):
            response = {
                "status": 'Error.The email is not unique,please choose another email'
            }
            return response, 400


        provider_info_profile = {

            "company_name": request.json['company_name'],
            "email": request.json['email'],
            'password' : SHA256(request.json['password']),
            "bio": '',
            "sex": 'undetermined',
            'isActive':True,
            # "profileImage": request.json['profileImage'],
            # 'birthDate': request.json['birthDate'],
            "createdAt": str(datetime.datetime.utcnow()),
            "provided_activities": []
        }

        uid = service_provider_collection.insert_one(provider_info_profile).inserted_id
        print(uid)

        return  {"user_id": f'{uid}'},201



class LoginProvider(Resource):

    def post(self):
        email = request.json['email']


        provider = getJsonProfile(service_provider_collection.find_one({'email':email}))

        if provider and provider['password'] == SHA256(request.json['password']):
            provider_id = str(provider["_id"]["$oid"])

            return provider, 201

        else:
            return {"status":"email or password invalid, try again"},400





class Activity(Resource):

    # Note: ratings needs to be calculated as an average. comments need to be updated

    def get(self):
        activities = getJsonProfile(service_provider_collection.find_one({"_id": ObjectId(request.json["activity_provider_id"])}))["provided_activities"]

        return activities,200




    def put(self):
        activity = {
            "title":request.json['title'],
            "description":request.json['description'],
            "picture":request.json['picture'],
            "city":request.json['city'],
            "date":request.json['date'],
            "category":request.json['category'],
            "price":request.json['price'],
            "comments":[],
            "rating":""
        }

        service_provider_collection.update_one(
            {"_id":ObjectId(request.json['activity_provider_id'])},
            {"$push":{"provided_activities":activity}}
        )

        activities = getJsonProfile(service_provider_collection.find_one({"_id": ObjectId(request.json["activity_provider_id"])}))["provided_activities"]


        return activities, 200


class Activities(Resource):
#
    def get(self):
        activities = getJsonProfile(service_provider_collection.find({},{"provided_activities":1,"_id":0}))

        seperated_activities = []
        for act in activities :
            seperated_activities.append(act["provided_activities"])



        concatenated_activities = []
        for act in seperated_activities:
            concatenated_activities = concatenated_activities+act








        return concatenated_activities,200





api.add_resource(Activities,'/get/activities')

api.add_resource(Activity,'/Activity/add','/get/provider/activities')



api.add_resource(SerivceProvider,'/provider/signup')
api.add_resource(LoginProvider,'/provider/signin')

api.add_resource(CreateUser, '/signup')
api.add_resource(LoginUser, '/signin')
api.add_resource(Profile,'/get_user_profile','/edit_profile')







def SHA256(password):
    return sha256(password.encode('utf-8')).hexdigest()

def IsEmailUnique(email):

    if  user_collection.find_one({'email': email}) or service_provider_collection.find_one({'email': email}):
        return False
    else:
        return True

def getJsonProfile(mongo_user):
    return json.loads(json_util.dumps(mongo_user))









if __name__ == "__main__":
    app.run(debug=True)


#https://backend-advenerice.herokuapp.com/