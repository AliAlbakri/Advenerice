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
activity_collection = db['Activity']
comment_collection = db['Comment']






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
        activity = getJsonProfile(activity_collection.find_one({"_id":ObjectId(request.json["activity_id"])}))


        return activity,200




    def post(self):
        activity = {
            "activity_provider_id":request.json["activity_provider_id"],
            "title":request.json['title'],
            "description":request.json['description'],
            "picture":request.json['picture'],
            "city":request.json['city'],
            "date":request.json['date'],
            "category":request.json['category'],
            "price":request.json['price'],
            "comments_Ids":[],
            "rating":""
        }


        activity_collection.insert_one(activity).inserted_id



        #
        activities = getJsonProfile(activity_collection.find({"activity_provider_id":request.json["activity_provider_id"]}))

        activities = list(activities)


        return activities, 200

    def delete(self):

        activity_collection.delete_one({"_id":ObjectId(request.json['activity_id'])})

        return 200


class ActivityByProvider(Resource):

    def get(self):
        activities = getJsonProfile(activity_collection.find({"activity_provider_id": request.args.get('activity_provider_id')}))
        activities = list(activities)


        return activities,200


class Activities(Resource):
#
    def get(self):
        activities = getJsonProfile(activity_collection.find({}))
        activities = list(activities)




        return activities,200



class Comment(Resource):

    #Note: get all comments for an activity ...
    def get(self):
        cursorComments = getJsonProfile(comment_collection.find({"activity_id":request.args.get('activity_id')}))


        return cursorComments,200


    def post(self):
        comment = {
            'commenter_id': request.json['commenter_id'],
            'activity_id': request.json['activity_id'],
            'comment': request.json['comment'],
            'rating' : request.json['rating']
        }
        comment_id = comment_collection.insert_one(comment).inserted_id



        return {"comment_id":str(comment_id)}, 201


    def delete(self):
        comment_collection.delete_one({"_id":ObjectId(request.json["comment_id"])})
        return 200





class JoinActivity(Resource):

    def get(self):
        current_joined_activity = activity_collection.find({'registered_participants': request.args.get('participant_id')})
        current_joined_activity = list(current_joined_activity)
        current_joined_activity = getJsonProfile(current_joined_activity)

        return current_joined_activity,200

    def post(self):
        participant_id = request.json['participant_id']
        activity_details = {
            "activity_id": request.json['activity_id'],
            "total_price": request.json['total_price'],
            "qty": request.json['qty']
        }

        activity_collection.update_one(
            {"_id":ObjectId(request.json['activity_id'])},
            {"$addToSet":{'registered_participants':participant_id}}
        )

        # get the provider id to add the price of this ticket to total sales
        provider_id_obj = activity_collection.find_one({"_id":ObjectId( request.json['activity_id'])},
                                     {'activity_provider_id':1})

        service_provider_collection.update_one(
            {"_id":ObjectId(provider_id_obj['activity_provider_id'])},
            {"$push":{"total_sales":request.json['total_price']}}
        )



        user_collection.update_one(
            {"_id":ObjectId(participant_id)},
            {"$addToSet": {'registered_activities': activity_details}}
        )


        current_joined_activity = activity_collection.find({'registered_participants':participant_id})
        current_joined_activity = list(current_joined_activity)
        current_joined_activity = getJsonProfile(current_joined_activity)



        return current_joined_activity,200






class ProviderSales(Resource):

    def get(self):
        sales = 0
        total_purshases = 0
        provider_obj = service_provider_collection.find_one({"_id":ObjectId(request.args.get('provider_id'))},{'total_sales':1})
        if 'total_sales' in  provider_obj:
            for sale in provider_obj['total_sales']:
                sales += sale
            total_purshases = len(provider_obj['total_sales'])

        return {'sales':sales,'orders':total_purshases},200







api.add_resource(JoinActivity,'/join_activity','/get/join_activity')
api.add_resource(ProviderSales,'/get/total_sales')


api.add_resource(Comment,'/get/comments','/post/comment','/delete/comment')
api.add_resource(ActivityByProvider,'/get/provider/activities')




api.add_resource(Activities,'/get/activities')
api.add_resource(Activity,'/Activity/add','/get/activity','/delete/activity')



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