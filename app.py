# from flask_restful import reqparse
# from controllers.Helloworld import *
from flask_restful import Api
from flask import Flask 
from dotenv import load_dotenv
load_dotenv()
import sys
import os
cwd = str(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(os.path.join(cwd,'/controllers/'))
from controllers.Helloworld import *

app = Flask(__name__) 
api = Api(app)

api.add_resource(HelloWorld, '/')
api.add_resource(Register,'/user/register/','/user/manage/')
# api.add_resource(Register,'/user/manage/')
api.add_resource(Login,'/user/login/')
# api.add_resource(AllUsers,'/users/')

if __name__ == '__main__': 
	app.run(debug=True) 