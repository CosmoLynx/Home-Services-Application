import os
from flask import Flask
from flask_restful import Resource,Api
from application import config
from flask_cors import CORS
from application.config import LocalDevelopmentConfig
from application.database import db

app = None
api = None

def create_app():
    app = Flask(__name__,template_folder="templates")
    if os.getenv('ENV','development') == 'production':
        raise Exception("Currently no production config is setup.")
    else:
        print("Starting Local Development")
        app.config.from_object(LocalDevelopmentConfig)
    db.init_app(app)
    api = Api(app)
    CORS(app)
    app.app_context().push()
    return app,api

app,api = create_app()
app.secret_key = os.urandom(24)

from application.controllers import *
from application.api import *

api.add_resource(CustomerAPI,'/api/customer','/api/customer/<int:customer_id>')
api.add_resource(ProfessionalAPI,'/api/professional','/api/professional/<int:professional_id>')

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5000)