from flask_restful import reqparse
from flask_restful import Resource
import json
from flask import request
import jwt
# from utilities.validater import *
import hashlib
import uuid
import sys 
import os
cwd = str(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(os.path.join(cwd,'../config'))
sys.path.append(os.path.join(cwd,'../utilities'))
from connection import *
from validater import *
users = []

def verifyKey(func):
    def innerFunc(*args,**kwargs):
        key = request.headers.get('Authorization',None)
        if key is None:
            return {"message":"please provide auth key"} 
        else:    
            if(request.headers["Authorization"] == 'secretkey'):
                return func(*args,**kwargs)
            else:
                return {"message":"Auth key is invalid"}       
    return innerFunc  

def verifyKeys(func):
    def innerFunc(*n,**kwargs):
        parser = reqparse.RequestParser()
        parser.add_argument('Authorization', type=str , required=True, location = 'headers', help = "please provide auth key")
        keys = parser.parse_args()
        if((keys["Authorization"] is None) or (keys["Authorization"] != 'secretkey')):
            return {"message":"invalid auth key"} 
        else:    
            return func(*n,**kwargs)     
    return innerFunc      

class HelloWorld(Resource):
    @verifyKeys
    def get(self):
        return {'hello': 'world'}
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('value', help='value is required',required=True)
        parser.add_argument('type', choices=('email', 'mobile'),help='invalid type',required=True)
        args = parser.parse_args()
        print(type(args))
        if(validate(args)):
            return args
        else:
            return {'error' : 'values cannot be empty'},400 
    def put(self):
        pass 
    def delete(self):
        pass    

class Register(Resource):
    @verifyKeys
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('Value', help='value is required',required=True)
        parser.add_argument('Type', choices=('email', 'mobile'),help='invalid type',required=True,location='json')
        parser.add_argument('Password',help='password is required',required=True,location='json')
        parser.add_argument('FirstName',help='firstname is required',required=True,location='json')
        parser.add_argument('LastName',help='lastname is required',required=True,location='json')
        parser.add_argument('Country',help='country is required',required=True,location='json')
        parser.add_argument('City',help='city is required',required=True,location='json')
        args = parser.parse_args()
        if(validate(args)):
            m = hashlib.md5()
            m.update(args['Password'].encode())
            password = m.hexdigest()
            args['Password'] = password
            args["Id"] = str(uuid.uuid4())
        else:
            return {'error' : 'values cannot be empty'},400   
        print(args)     
        try:
            mycursor = user_db.cursor()
            if(args['Type'] == 'email'):
                query = "SELECT * FROM Users WHERE EMAIL = '{}'".format(args['Value'])
                val = (args['Id'],args['FirstName'],args['LastName'],args['Value'],'',args['Country'],args['City'],args['Password'])               
            if(args['Type'] == 'mobile'):
                query = "SELECT * FROM Users WHERE MOBILE = '{}'".format(args['Value'])
                val = (args['Id'],args['FirstName'],args['LastName'],'',args['Value'],args['Country'],args['City'],args['Password'])          
            mycursor.execute(query)
            userExists = mycursor.fetchone()
            if(userExists is None):
                sql = "INSERT INTO Users (Id,LastName,FirstName,Email,Mobile,Country,City,Password) VALUES (%s, %s,%s, %s,%s, %s, %s, %s)"
                insert_cur = user_db.cursor()
                insert_cur.execute(sql,val)
                user_db.commit()
                message = {"code":1200,"message":"User registered successfully",
                "details":args}
                status_code = 200
                return message,status_code
            else:
                message = {"message":"User already exists with {}".format(args["Value"])}
                status_code = 400
                return message,status_code    
        except Exception as e:
            return {'error':'error occurred due to {}'.format(e)}         
    def put(self):
        parser = reqparse.RequestParser()
        parser.add_argument('Id', help='User ID is required',required=True,location='json')
        parser.add_argument('Email', help='email is required',location='json')
        parser.add_argument('Mobile', help='mobile is required',location='json')
        parser.add_argument('Password',help='password is required',location='json')
        parser.add_argument('FirstName',help='firstname is required',location='json')
        parser.add_argument('LastName',help='lastname is required',location='json')
        parser.add_argument('Country',help='country is required',location='json')
        parser.add_argument('City',help='city is required',location='json')
        args = parser.parse_args()
        data = parser.parse_args()
        Id = data["Id"]
        updt = False
        if Id is None:
            message={"message":"Invalid ID"} 
            status_code=400
            return message,status_code
        else:
            print(data)
            userExists,userData = check_if_userExists_By_UserId(str(Id))
            userData = create_user_obj_from_dbrecord(userData)
            if(not userExists):
                message={"message":"User not Found with this UserId"}
                status_code=400
                return message,status_code
            if(data['Email'] is not None):
                if(check_if_Login_already_inuse_by_other_user(data['Id'],'email',data['Email'])):
                    message={"message":"Email is already in use"}
                    status_code=400
                    return message,status_code
                else:
                    updt = True       
            if(data['Mobile'] is not None):    
                if(check_if_Login_already_inuse_by_other_user(data['Id'],'mobile',data['Mobile'])):
                    message={"message":"Mobile number is already in use"}
                    status_code=400
                    return message,status_code
                else:
                    updt = True    
            if(updt == True):        
                print("reached")
                m = hashlib.md5()
                m.update(data['Password'].encode())
                password = m.hexdigest()
                data['Password'] = password
                db_object = updateObject(data,userData)
                del db_object['Id']
                update_query = create_update_query("Users",data["Id"],db_object)
                print(update_query)
                mycursor = user_db.cursor()
                try:
                    print(mycursor.execute(update_query))
                    user_db.commit()
                    message={"message":"successfully updated"}
                    status_code=200
                    return message,status_code 
                except Exception as e:
                    message={"error":"error occurred due to {}".format(e)}
                    status_code=500
                    return message,status_code   
    def delete(self):
        pass          
class Login(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('Value', help='value is required',required=True)
        parser.add_argument('Type', choices=('email', 'mobile'),help='invalid type',required=True,location='json')
        parser.add_argument('Password',help='password is required',required=True,location='json')
        args = parser.parse_args()
        flag = False
        Type = args['Type']
        Value = args['Value']
        Password = args['Password']
        if(Value is None or Value == ''):
            message={"message":"{} is invalid".format(Value)}
            status_code=400
            return message,status_code  
        elif(Type is None or Type == ''):
            message={"message":"{} is invalid".format(Type)}
            status_code=400
            return message,status_code
        elif(Password is None or Password == ''):
            message={"message":"{} is invalid".format(Password)}
            status_code=400
            return message,status_code
        else:
            try:
                mycursor = user_db.cursor()
                if(Type == 'email'):
                    query = "SELECT * FROM Users WHERE EMAIL = '{}'".format(Value)             
                if(Type == 'mobile'):
                    query = "SELECT * FROM Users WHERE MOBILE = '{}'".format(Value)         
                mycursor.execute(query)
                userData = mycursor.fetchone()
                if(userData is None):
                    message = {"message":"{} is not registered"}
                    status_code = 404
                    return message,status_code
                else:
                    m = hashlib.md5()
                    m.update(Password.encode())
                    Password = m.hexdigest()
                    DbPassword = userData[7]
                    if(str(Password) == str(DbPassword)):
                        userData = create_user_obj_from_dbrecord(userData)
                        encoded_jwt = jwt.encode(userData, os.getenv('JWT_AUTH_KEY'), algorithm='HS256')
                        encoded_jwt = encoded_jwt.decode("utf-8")
                        message = {"token":encoded_jwt}
                        status_code = 200
                        return message,status_code
                    else:    
                        message = {"message":"Email or Password combination is incorrect!"}
                        status_code = 400
                        return message,status_code
            except Exception as e:
                return {'error':'error occurred due to {}'.format(e)} 



     