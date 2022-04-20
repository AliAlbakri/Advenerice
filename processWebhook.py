import flask
import os
from flask import request, send_from_directory, render_template
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
notification_collection = db['Notification']
category_collection = db['category']



class CreateUser(Resource):
    # creating a new user
    # Note: sex types are 'male', 'female' and 'undetermined'
    # Note: status are 'active', 'banned'
    # Note: read later title is going to be customized in frontend

    def put(self):
        # check if email is unique
        if (not IsEmailUnique(request.json['email'])):
            response = {
                "status": 'Error.The email is not unique,please choose another email'
            }

            return response, 400

        user_info_profile = {
            "username": request.json['username'],
            "email": request.json['email'],
            'password': SHA256(request.json['password']),
            "bio": '',
            "sex": 'undetermined',
            'isActive': True,
            "createdAt": str(datetime.datetime.utcnow()),
            "regestred_activities": None
        }

        uid = user_collection.insert_one(user_info_profile).inserted_id

        return {"user_id": f'{uid}'}, 201


class LoginUser(Resource):

    def post(self):
        email = request.json['email']

        user = getJsonProfile(user_collection.find_one({'email': email}))

        if user and user['password'] == SHA256(request.json['password']):
            user_id = str(user["_id"]["$oid"])
            profile = getJsonProfile(user_collection.find_one({'email': email}))

            return profile, 201

        else:
            return {"status": "email or password invalid, try again"}, 400


class Profile(Resource):

    def get(self):
        # note that getting a user profile  can be done by user id or email (unique params)
        search_by = request.args['searchBy']
        value = request.args[search_by]
        profile = None
        if search_by == 'email':
            profile = getJsonProfile(user_collection.find_one({search_by: value}))

        if search_by == 'user_id' and ObjectId.is_valid(value):
            profile = getJsonProfile(user_collection.find_one({"_id": ObjectId(value)}))

        if profile:
            profile.pop('password', None)
            return profile, 200

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
        if request.json['email'] != profile['email']:
            if not IsEmailUnique(request.json['email']):
                notUniqueEmail = True
                response = {'status': 'email not updated, choose a unique email '}

        updated_profile = {"username": request.json['username'], "bio": request.json['bio'],
                           "sex": request.json['sex'], "profileImage": request.json['profileImage']}

        if not notUniqueEmail:
            updated_profile['email'] = request.json['email']
            response = {'status': "profile updated"}

        user_collection.update_one(
            {'_id': ObjectId(request.json['user_id'])},
            {'$set': updated_profile}
        )
        profile = getJsonProfile(user_collection.find_one({"_id": ObjectId(request.json["user_id"])}))
        profile.pop('password', None)

        return profile, 200


class SerivceProvider(Resource):

    # put is creating a new service provider
    def post(self):
        # check if email is unique
        if (not IsEmailUnique(request.json['email'])):
            response = {
                "status": 'Error.The email is not unique,please choose another email'
            }
            return response, 400

        provider_info_profile = {
            ################# change is active here to false later on
            "company_name": request.json['company_name'],
            "email": request.json['email'],
            'password': SHA256(request.json['password']),
            "bio": '',
            "sex": 'undetermined',
            'isActive': True,
            "logo":"",
            # 'birthDate': request.json['birthDate'],
            "createdAt": str(datetime.datetime.utcnow()),
            "provided_activities": []
        }

        uid = service_provider_collection.insert_one(provider_info_profile).inserted_id
        print(uid)

        return {"user_id": f'{uid}'}, 201



    def put(self):
        update_body = request.get_json()
        provider_id = str(request.json['activity_provider_id'])
        del request.json['activity_provider_id']
        res = {'status': 'updated'}

        print(update_body)


        if 'email' in update_body:
            if service_provider_collection.find_one({'email': update_body['email']}):
                del update_body['email']

        service_provider_collection.update_one(
            {"_id":ObjectId(provider_id)},
            {"$set":update_body}
        )


        return res,200


class LoginProvider(Resource):

    def post(self):
        email = request.json['email']

        provider = getJsonProfile(service_provider_collection.find_one({'email': email}))

        if provider and provider['password'] == SHA256(request.json['password']):
            if  provider['isActive']:
                return provider, 201
            else:
                return {"status":"admin will verify your account soon"},400

        else:
            return {"status": "email or password invalid, try again"}, 400


class Activity(Resource):

    # Note: ratings needs to be calculated as an average. comments need to be updated

    def get(self):
        activity = getJsonProfile(activity_collection.find_one({"_id": ObjectId(request.args.get('activity_id'))}))

        return activity, 200

    def post(self):
        activity = {
            "activity_provider_id": request.json["activity_provider_id"],
            "title": request.json['title'],
            "description": request.json['description'],
            "picture": request.json['picture'],
            "city": request.json['city'],
            "date": request.json['date'],
            "category": request.json['category'],
            "price": request.json['price'],
            "comments_Ids": [],
            "rating": ""
        }

        activity_collection.insert_one(activity).inserted_id

        #
        activities = getJsonProfile(
            activity_collection.find({"activity_provider_id": request.json["activity_provider_id"]}))

        activities = list(activities)

        return activities, 200

    def delete(self):
        activity_collection.delete_one({"_id": ObjectId(request.json['activity_id'])})

        return 200


    def put(self):
        activity_update =  request.get_json()
        activity_id = str(request.json['activity_id'])
        del activity_update['activity_id']
        activity_collection.update_one(
            {'_id':ObjectId(activity_id)},
            {'$set':activity_update}
        )

        return 200






class ActivityByProvider(Resource):

    def get(self):
        activities = getJsonProfile(
            activity_collection.find({"activity_provider_id": request.args.get('activity_provider_id')}))
        activities = list(activities)

        return activities, 200


class Activities(Resource):
    #
    def get(self):
        activities = getJsonProfile(activity_collection.find({}))
        activities = list(activities)

        return activities, 200


class Comment(Resource):

    # Note: get all comments for an activity ...
    def get(self):
        cursorComments = getJsonProfile(comment_collection.find({"activity_id": request.args.get('activity_id')}))

        return cursorComments, 200

    def post(self):
        commenter_obj = user_collection.find_one({"_id": ObjectId(request.json['commenter_id'])})

        comment = {
            'commenter_id': request.json['commenter_id'],
            'activity_id': request.json['activity_id'],
            'comment': request.json['comment'],
            'rating': request.json['rating'],
            "commenter_name": commenter_obj['username'],
            'created_at': str(datetime.datetime.now().strftime("%x"))
        }
        comment_id = comment_collection.insert_one(comment).inserted_id

        avg_rating = getActivityRating(request.json['activity_id'])
        # updating the activity average rating
        activity_collection.update_one(
            {"_id":ObjectId(request.json['activity_id'])},
            {"$set":{'rating':avg_rating}}
        )


        return {"comment_id": str(comment_id)}, 201

    def delete(self):
        comment_collection.delete_one({"_id": ObjectId(request.json["comment_id"])})
        return 200


class JoinActivity(Resource):

    def get(self):
        current_joined_activity = activity_collection.find(
            {'registered_participants': request.args.get('participant_id')})
        current_joined_activity = list(current_joined_activity)
        current_joined_activity = getJsonProfile(current_joined_activity)

        return current_joined_activity, 200

    def post(self):
        participant_id = request.json['participant_id']
        activity_details = {
            "activity_id": request.json['activity_id'],
            "total_price": request.json['total_price'],
            "qty": request.json['qty']
        }

        activity_collection.update_one(
            {"_id": ObjectId(request.json['activity_id'])},
            {"$addToSet": {'registered_participants': participant_id}}
        )

        # get the provider id to add the price of this ticket to total sales
        provider_id_obj = activity_collection.find_one({"_id": ObjectId(request.json['activity_id'])},
                                                       {'activity_provider_id': 1})

        service_provider_collection.update_one(
            {"_id": ObjectId(provider_id_obj['activity_provider_id'])},
            {"$push": {"total_sales": request.json['total_price']}}
        )

        user_collection.update_one(
            {"_id": ObjectId(participant_id)},
            {"$addToSet": {'registered_activities': activity_details}}
        )

        current_joined_activity = activity_collection.find({'registered_participants': participant_id})
        current_joined_activity = list(current_joined_activity)
        current_joined_activity = getJsonProfile(current_joined_activity)

        return current_joined_activity, 200


class ProviderSales(Resource):

    def get(self):
        sales = 0
        total_purshases = 0
        provider_obj = service_provider_collection.find_one({"_id": ObjectId(request.args.get('provider_id'))},
                                                            {'total_sales': 1})
        if 'total_sales' in provider_obj:
            for sale in provider_obj['total_sales']:
                sales += sale
            total_purshases = len(provider_obj['total_sales'])

        return {'sales': sales, 'orders': total_purshases}, 200



class Notification(Resource):

    def post(self):

        noti_obj = {
            "provider_id": request.json['provider_id'],
            "title": request.json['title'],
            "body": request.json['body'],
            "created_at": str(datetime.datetime.utcnow())
        }

        id = notification_collection.insert_one(noti_obj).inserted_id

        return str(id),200


    def get(self):
        notifications = notification_collection.find({})

        notidications_arr = []
        if notifications:
            for notification in notifications:
               logo_cname = service_provider_collection.find_one(
                    {'_id':ObjectId(notification['provider_id'])}
                )

               customed_notification = {
                   "logo": logo_cname['logo'],
                   "title":notification['title'],
                   "body": notification['body'],
                   "created_at":notification['created_at']
               }
               notidications_arr.append(customed_notification)



        return notidications_arr,200




class Category(Resource):


    def get(self):
        categories_pointer = category_collection.find({})
        categories_arr = []
        for category in categories_pointer :
            categories_arr.append(getJsonProfile(category))



        return categories_arr,200

    def post(self):

        category_obj = {
            "name": request.json['category_name']
        }

        category_collection.insert_one(category_obj)

        return {"msg":"category added"},200




    def delete(self):

        category_collection.delete_one({"_id":ObjectId(request.json['category_id'])})

        return {'msg':'category deleted'}




class UnActiveProviders(Resource):

    # getting not active provs
    def get(self):

        pointers = service_provider_collection.find({'isActive':False})
        not_active_providers_arr = []
        for not_active_provider in pointers:
            not_active_providers_arr.append(getJsonProfile(not_active_provider))

        return not_active_providers_arr,200




class ActiveProviders(Resource):

    # activiate provider
    def post(self):

        provider_id = request.json['provider_id']

        service_provider_collection.update_one(
            {'_id':ObjectId(provider_id)},
            {"$set":{"isActive":True}}
        )

        return {"msg":'Activated successfully'},200

class ForgotPassword(Resource):

    def post(self):


        if not ( user_collection.find_one({'email':request.json['email']})
                 or service_provider_collection.find_one({'email':request.json['email']}) ) :
            return {'status':'no such email'}

        encrypted_pass = SHA256(request.json['new-password'])
        if request.json['type'] == 'activity_provider':
            print('here')
            service_provider_collection.update_one(
                {'email':request.json['email']},
                {"$set":{'password':encrypted_pass}}
            )
        else:
            user_collection.update_one(
                {'email': request.json['email']},
                {"$set": {'password': encrypted_pass}}
            )



        return 200




class filterA(Resource):
    # ,
    # {"category": request.args.get('category')},
    # {"date": request.args.get('date')}
        def get(self):
            global filtered_activity
            if request.args.get('date') and request.args.get('city') and request.args.get('category') :

                filtered_activity = activity_collection.find({"$and": [
                   {"city": request.args.get('city')},
                    {"category": request.args.get('category')},
                    {"date": request.args.get('date')}
                ]})


            elif request.args.get('city') and request.args.get('category') :
                filtered_activity = activity_collection.find({"$and": [
                    {"city": request.args.get('city')},
                    {"category": request.args.get('category')}
                ]})

            elif request.args.get('city') and request.args.get('date') :
                filtered_activity = activity_collection.find({"$and": [
                    {"city": request.args.get('city')},
                    {"date": request.args.get('date')}
                ]})

            elif request.args.get('category') and request.args.get('date') :
                filtered_activity = activity_collection.find({"$and": [
                    {"category": request.args.get('category')},
                    {"date": request.args.get('date')}
                ]})

            else:
                if request.args.get('category'):
                    filtered_activity = activity_collection.find({'category':request.args.get('category')})
                elif request.args.get('date'):
                    filtered_activity = activity_collection.find({'date':request.args.get('date')})
                elif request.args.get('city'):
                    filtered_activity = activity_collection.find({'city':request.args.get('city')})
                else:
                    filtered_activity = activity_collection.find({})







            filtered_activity = getJsonProfile(list(filtered_activity))

            return filtered_activity,200








api.add_resource(filterA, '/filter_activity')

api.add_resource(ForgotPassword, '/forgot_password')


api.add_resource(ActiveProviders, '/activate_provider')

api.add_resource(UnActiveProviders, '/get_unactive_providers')

api.add_resource(Category, '/admin/add_category', '/admin/delete_category','/admin/get_categories')


api.add_resource(Notification, '/send_notification', '/get/notification')


api.add_resource(JoinActivity, '/join_activity', '/get/join_activity')
api.add_resource(ProviderSales, '/get/total_sales')

api.add_resource(Comment, '/get/comments', '/post/comment', '/delete/comment')
api.add_resource(ActivityByProvider, '/get/provider/activities')

api.add_resource(Activities, '/get/activities')
api.add_resource(Activity, '/Activity/add', '/get/activity', '/delete/activity','/edit/activity')

api.add_resource(SerivceProvider, '/provider/signup','/edit/provider_account')
api.add_resource(LoginProvider, '/provider/signin')

api.add_resource(CreateUser, '/signup')
api.add_resource(LoginUser, '/signin')
api.add_resource(Profile, '/get_user_profile', '/edit_profile')


def SHA256(password):
    return sha256(password.encode('utf-8')).hexdigest()


def IsEmailUnique(email):
    if user_collection.find_one({'email': email}) or service_provider_collection.find_one({'email': email}):
        return False
    else:
        return True


def getJsonProfile(mongo_user):
    return json.loads(json_util.dumps(mongo_user))



def getActivityRating(activity_id):
    comments = comment_collection.find({'activity_id': activity_id})
    comments = list(comments)
    total_ratings = 0
    average_ratings = None

    if comments:
        print(comments)
        for comment in comments:
            total_ratings += int(comment['rating'])
        average_ratings = total_ratings / len(comments)

        return float("{:.1f}".format(average_ratings))


if __name__ == "__main__":
    app.run(debug=True)

# https://backend-advenerice.herokuapp.com/
