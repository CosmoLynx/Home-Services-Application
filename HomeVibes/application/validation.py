from werkzeug.exceptions import HTTPException
from flask import make_response
import json

class NotFoundError(HTTPException):
    def __init__(self,status_code,error_message):
        self.response = make_response(error_message,status_code)

class BusinessValidationError(HTTPException):
    def __init__(self,status_code,error_code,error_message):
        dump = {
            "error_code": error_code,
            "error_message": error_message
        }
        self.response = make_response(json.dumps(dump),status_code)

class DuplicateError(HTTPException):
    def __init__(self, status_code,error_message):
        self.response = make_response(error_message, status_code)