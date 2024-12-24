from flask_restful import Resource,reqparse
from flask_restful import fields,marshal_with
from application.database import db
from application.models import *
from application.validation import *

customer_output_fields = {
    'customer_id':fields.Integer,
    'email_id' : fields.String,
    'password' : fields.String,
    'address' : fields.String,
    'pincode' : fields.Integer,
    'name' : fields.String,
    'city' : fields.String,
    'phone_no' : fields.Integer,
    'rating' : fields.Float,
    'login_status' : fields.Integer,
    'status' : fields.String
}

create_customer_parser = reqparse.RequestParser()
create_customer_parser.add_argument('customer_id')
create_customer_parser.add_argument('email_id')
create_customer_parser.add_argument('password')
create_customer_parser.add_argument('address')
create_customer_parser.add_argument('pincode')
create_customer_parser.add_argument('name')
create_customer_parser.add_argument('city')
create_customer_parser.add_argument('phone_no')
create_customer_parser.add_argument('rating')
create_customer_parser.add_argument('status')
create_customer_parser.add_argument('login_status')

professional_output_fields = {
    'professional_id' : fields.Integer,
    'email_id' : fields.String,
    'password' : fields.String,
    'name' : fields.String,
    'service_id' : fields.Integer,
    'experience' : fields.Integer,
    'resume' : fields.String,
    'address' : fields.String,
    'pincode' : fields.Integer,
    'city' : fields.String,
    'phone_no' : fields.Integer,
    'rating' : fields.Float,
    'status' : fields.String,
    'login_status' : fields.Integer
}

create_professional_parser = reqparse.RequestParser()
create_professional_parser.add_argument('professional_id')
create_professional_parser.add_argument('email_id')
create_professional_parser.add_argument('password')
create_professional_parser.add_argument('name')
create_professional_parser.add_argument('service_id')
create_professional_parser.add_argument('experience')
create_professional_parser.add_argument('resume')
create_professional_parser.add_argument('address')  
create_professional_parser.add_argument('pincode')
create_professional_parser.add_argument('city')
create_professional_parser.add_argument('phone_no')
create_professional_parser.add_argument('rating')
create_professional_parser.add_argument('status')
create_professional_parser.add_argument('login_status')

class CustomerAPI(Resource):

    @marshal_with(customer_output_fields)
    def get(self,customer_id):
        customer = Customer.query.filter_by(customer_id=customer_id).first()
        if not customer:
            raise NotFoundError(status_code=404,error_message='Customer Not Found')
        return customer
    
    @marshal_with(customer_output_fields)
    def put(self,customer_id):
        args = create_customer_parser.parse_args()
        email_id = args.get('email_id')
        password = args.get('password')
        address = args.get('address')
        pincode = args.get('pincode')
        name = args.get('name')
        city = args.get('city')
        phone_no = args.get('phone_no')
        rating = args.get('rating')
        status = args.get('status')
        login_status = args.get('login_status')
        customer = Customer.query.filter_by(customer_id=customer_id).first()
        if not customer:
            raise NotFoundError(status_code=404,error_message='Customer Not Found')
        else:
            if email_id is None:
                raise BusinessValidationError(status_code=400,error_code='CUSTOMER001',error_message='Email Id is required')
            if password is None:
                raise BusinessValidationError(status_code=400,error_code='CUSTOMER002',error_message='Password is required')
            if address is None:
                raise BusinessValidationError(status_code=400,error_code='CUSTOMER003',error_message='Address is required')
            if pincode is None:
                raise BusinessValidationError(status_code=400,error_code='CUSTOMER004',error_message='Pincode is required')
            if name is None:
                raise BusinessValidationError(status_code=400,error_code='CUSTOMER005',error_message='Name is required')
            if city is None:
                raise BusinessValidationError(status_code=400,error_code='CUSTOMER006',error_message='City is required')
            if phone_no is None:    
                raise BusinessValidationError(status_code=400,error_code='CUSTOMER007',error_message='Phone Number is required')
            if status is None:
                raise BusinessValidationError(status_code=400,error_code='CUSTOMER009',error_message='Status is required')
            if login_status is None:
                raise BusinessValidationError(status_code=400,error_code='CUSTOMER010',error_message='Login Status is required')
            customer.email_id = email_id
            customer.password = password
            customer.address = address  
            customer.pincode = pincode
            customer.name = name
            customer.city = city
            customer.phone_no = phone_no
            customer.rating = rating    
            customer.status = status
            customer.login_status = login_status
            db.session.commit()
            return customer,200

    def delete(self,customer_id):
        customer = Customer.query.filter_by(customer_id=customer_id).first()
        if not customer:
            raise NotFoundError(status_code=404,error_message='Customer Not Found')
        for rating in customer.ratings:
            db.session.delete(rating)
        for rating in customer.professional_ratings:
            db.session.delete(rating)
        for req in customer.requests:
            for prof in req.prof_details:
                db.session.delete(prof)
            db.session.delete(req)
        db.session.delete(customer)
        db.session.commit()
        return 'Successfully Deleted',200

    @marshal_with(customer_output_fields)
    def post(self):
        args = create_customer_parser.parse_args()
        email_id = args.get('email_id')
        password = args.get('password')
        address = args.get('address')
        pincode = args.get('pincode')
        name = args.get('name')
        city = args.get('city')
        phone_no = args.get('phone_no')
        if email_id is None:
            raise BusinessValidationError(status_code=400,error_code='CUSTOMER001',error_message='Email Id is required')
        if password is None:
            raise BusinessValidationError(status_code=400,error_code='CUSTOMER002',error_message='Password is required')
        if address is None:
            raise BusinessValidationError(status_code=400,error_code='CUSTOMER003',error_message='Address is required')
        if pincode is None:
            raise BusinessValidationError(status_code=400,error_code='CUSTOMER004',error_message='Pincode is required')
        if name is None:
            raise BusinessValidationError(status_code=400,error_code='CUSTOMER005',error_message='Name is required')
        if city is None:
            raise BusinessValidationError(status_code=400,error_code='CUSTOMER006',error_message='City is required')
        if phone_no is None:    
            raise BusinessValidationError(status_code=400,error_code='CUSTOMER007',error_message='Phone Number is required')
        customer = Customer.query.filter_by(email_id=email_id).first()
        if customer:
            raise DuplicateError(status_code=409,error_message='Customer already exists')
        new_customer = Customer(email_id=email_id,password=password,address=address,pincode=pincode,name=name,city=city,phone_no=phone_no,login_status=0,status='active',rating=0.0)
        db.session.add(new_customer)
        db.session.commit()
        return new_customer,201

class ProfessionalAPI(Resource):

    @marshal_with(professional_output_fields)
    def get(self,professional_id):
        professional = Professional.query.filter_by(professional_id=professional_id).first()
        if not professional:
            raise NotFoundError(status_code=404,error_message='Professional not found')
        return professional

    @marshal_with(professional_output_fields)   
    def put(self,professional_id):
        args = create_professional_parser.parse_args()
        email_id = args.get('email_id')
        password = args.get('password')
        name = args.get('name')
        service_id = args.get('service_id')
        experience = args.get('experience')
        address = args.get('address')
        pincode = args.get('pincode')
        city = args.get('city')
        phone_no = args.get('phone_no')
        rating = args.get('rating')
        status = args.get('status')
        login_status = args.get('login_status')
        professional = Professional.query.filter_by(professional_id=professional_id).first()
        if not professional:
            raise NotFoundError(status_code=404,error_message='Professional Not Found')
        else:
            if email_id is None:
                raise BusinessValidationError(status_code=400,error_code='PROFESSIONAL001',error_message='Email Id is required')
            if password is None:
                raise BusinessValidationError(status_code=400,error_code='PROFESSIONAL002',error_message='Password is required')
            if name is None:
                raise BusinessValidationError(status_code=400,error_code='PROFESSIONAL003',error_message='Name is required')
            if service_id is None:
                raise BusinessValidationError(status_code=400,error_code='PROFESSIONAL004',error_message='Service Id is required')
            if experience is None:
                raise BusinessValidationError(status_code=400,error_code='PROFESSIONAL005',error_message='Experience is required')
            if address is None:
                raise BusinessValidationError(status_code=400,error_code='PROFESSIONAL006',error_message='Address is required')
            if pincode is None:
                raise BusinessValidationError(status_code=400,error_code='PROFESSIONAL007',error_message='Pincode is required')
            if city is None:
                raise BusinessValidationError(status_code=400,error_code='PROFESSIONAL008',error_message='City is required')
            if phone_no is None:
                raise BusinessValidationError(status_code=400,error_code='PROFESSIONAL009',error_message='Phone Number is required')
            if rating is None:
                raise BusinessValidationError(status_code=400,error_code='PROFESSIONAL010',error_message='Rating is required')
            if status is None:
                raise BusinessValidationError(status_code=400,error_code='PROFESSIONAL011',error_message='Status is required')
            if login_status is None:
                raise BusinessValidationError(status_code=400,error_code='PROFESSIONAL012',error_message='Login Status is required')
            professional.email_id = email_id
            professional.password = password
            professional.name = name
            professional.service_id = service_id
            professional.experience = experience
            professional.address = address
            professional.pincode = pincode
            professional.city = city
            professional.phone_no = phone_no
            professional.rating = rating
            professional.status = status
            professional.login_status = login_status
            db.session.commit()
            return professional,201

    def delete(self,professional_id):
        professional = Professional.query.filter_by(professional_id=professional_id).first()
        if not professional:
            raise NotFoundError(status_code=404,error_message='Professional Not Found')
        for rating in professional.ratings:
            db.session.delete(rating)
        for rating in professional.customer_ratings:
            db.session.delete(rating)
        for req in professional.requests:
            db.session.delete(req)
        db.session.delete(professional)
        db.session.commit()
        return 'Successfully Deleted',200

    @marshal_with(professional_output_fields)
    def post(self):
        args = create_professional_parser.parse_args()
        email_id = args.get('email_id')
        password = args.get('password')
        name = args.get('name')
        service_id = args.get('service_id')
        experience = args.get('experience')
        resume = args.get('resume')
        address = args.get('address')
        pincode = args.get('pincode')
        city = args.get('city')
        phone_no = args.get('phone_no')
        if email_id is None:
            raise BusinessValidationError(status_code=400,error_code='PROFESSIONAL001',error_message='Email Id is required')
        if password is None:
            raise BusinessValidationError(status_code=400,error_code='PROFESSIONAL002',error_message='Password is required')
        if name is None:
            raise BusinessValidationError(status_code=400,error_code='PROFESSIONAL003',error_message='Name is required')
        if service_id is None:
            raise BusinessValidationError(status_code=400,error_code='PROFESSIONAL004',error_message='Service Id is required')
        if experience is None:
            raise BusinessValidationError(status_code=400,error_code='PROFESSIONAL005',error_message='Experience is required')
        if address is None:
            raise BusinessValidationError(status_code=400,error_code='PROFESSIONAL006',error_message='Address is required')
        if pincode is None:
            raise BusinessValidationError(status_code=400,error_code='PROFESSIONAL007',error_message='Pincode is required')
        if city is None:
            raise BusinessValidationError(status_code=400,error_code='PROFESSIONAL008',error_message='City is required')
        if phone_no is None:
            raise BusinessValidationError(status_code=400,error_code='PROFESSIONAL009',error_message='Phone Number is required')
        if resume is None:
            raise BusinessValidationError(status_code=400,error_code='PROFESSIONAL013',error_message='Resume is required')
        professional = Professional.query.filter_by(email_id=email_id).first()
        if professional:
            raise DuplicateError(status_code=409,error_message='Professional already exist')
        new_professional = Professional(email_id=email_id,password=password,name=name,service_id=service_id,experience=experience,address=address,pincode=pincode,city=city,phone_no=phone_no,rating=0.0,status='under-verification',login_status=0,resume=bytes(resume,'utf-8'))
        db.session.add(new_professional)
        db.session.commit()
        return new_professional,201
