from application.database import db

class Customer(db.Model):
    __tablename__ = 'customer'

    customer_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email_id = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    address = db.Column(db.String, nullable=False)
    pincode = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String,nullable=False)
    phone_no = db.Column(db.Integer, nullable=False)
    rating = db.Column(db.Float ,default=0.0)
    login_status = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String,nullable=False)
    ratings = db.relationship('CustomerRating')
    professional_ratings = db.relationship('ProfessionalRating')
    requests = db.relationship('ServiceRequest', back_populates='customer')

class Professional(db.Model):
    __tablename__ = 'professional'

    professional_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email_id = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    name = db.Column(db.String, nullable=False)
    service_id = db.Column(db.Integer,db.ForeignKey('service.service_id'), nullable=False)
    experience = db.Column(db.Integer, nullable=False)
    resume = db.Column(db.LargeBinary, nullable=False)
    address = db.Column(db.String, nullable=False)
    pincode = db.Column(db.Integer, nullable=False)
    city = db.Column(db.String,nullable=False)
    phone_no = db.Column(db.Integer, nullable=False)
    rating = db.Column(db.Float ,default=0.0)
    status = db.Column(db.String, nullable=False)
    login_status = db.Column(db.Integer, nullable=False)
    service = db.relationship('Service',back_populates='professionals')
    ratings = db.relationship('ProfessionalRating')
    customer_ratings = db.relationship('CustomerRating')
    requests = db.relationship('ProfessionalRequest', back_populates='professional')

class Admin(db.Model):
    __tablename__ = 'admin'
    admin_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email_id = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    name = db.Column(db.String, nullable=False)
    login_status = db.Column(db.Integer, nullable=False)

class Service(db.Model):
    __tablename__ = 'service'

    service_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.Text, nullable=False)
    base_price = db.Column(db.Integer, nullable=False)
    time_required = db.Column(db.Integer, nullable=False)
    type = db.Column(db.String,nullable=False)
    professionals = db.relationship('Professional', back_populates='service')

class ServiceRequest(db.Model):
    __tablename__ = 'service_requests'
    
    request_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    req_customer_id = db.Column(db.Integer, db.ForeignKey('customer.customer_id'), nullable=False)
    req_service_id = db.Column(db.Integer, db.ForeignKey('service.service_id'), nullable=False)
    request_date = db.Column(db.String, nullable=False)
    request_status = db.Column(db.String(50), nullable=False)
    customer = db.relationship('Customer',back_populates='requests')
    service = db.relationship('Service')
    prof_details = db.relationship('ProfessionalRequest', back_populates='details')

class ProfessionalRequest(db.Model):
    __tablename__ = 'professional_requests'
    prof_request_id = db.Column(db.Integer,primary_key=True, autoincrement=True)
    request_id = db.Column(db.Integer, db.ForeignKey('service_requests.request_id'), nullable=False)
    professional_id = db.Column(db.Integer, db.ForeignKey('professional.professional_id'), nullable=False)
    details = db.relationship('ServiceRequest',back_populates='prof_details')
    professional = db.relationship('Professional', back_populates='requests')

class CustomerRating(db.Model):
    __tablename__ = 'customer_rating'

    rating_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    rcustomer_id = db.Column(db.Integer, db.ForeignKey('customer.customer_id'), nullable=False)
    rprofessional_id = db.Column(db.Integer, db.ForeignKey('professional.professional_id'), nullable=False)
    rrequest_id = db.Column(db.Integer, db.ForeignKey('service_requests.request_id'), nullable=False)
    stars = db.Column(db.Integer, nullable=False)
    comments = db.Column(db.Text, nullable=True)

class ProfessionalRating(db.Model):
    __tablename__ = 'professional_rating'

    rating_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    rprofessional_id = db.Column(db.Integer, db.ForeignKey('professional.professional_id'), nullable=False)
    rcustomer_id = db.Column(db.Integer, db.ForeignKey('customer.customer_id'), nullable=False)
    rrequest_id = db.Column(db.Integer, db.ForeignKey('service_requests.request_id'), nullable=False)
    stars = db.Column(db.Integer, nullable=False)
    comments = db.Column(db.Text, nullable=True)