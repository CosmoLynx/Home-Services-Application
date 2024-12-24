from flask import request, render_template, redirect, url_for,flash,Response
from flask import current_app as app
from application.models import *
from application.database import db
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/customer/login',methods=["GET","POST"])
def customer_login():
    if request.method == "GET":
        return render_template('customer_login.html')
    elif request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        customer = Customer.query.filter_by(email_id=email).first()
        if not customer:
            flash("User not found")
            return redirect(url_for('customer_login'))
        if customer.password != password:
            flash("Invalid password")
            return redirect(url_for('customer_login'))
        customer.login_status = 1
        db.session.commit()
        return redirect(url_for('customer_dashboard',customer_id=customer.customer_id))

@app.route('/customer/sign_up',methods=["GET","POST"])
def customer_signup():
    if request.method == "GET":
        return render_template('customer_signup.html')
    elif request.method == "POST":
        name = request.form.get("name")
        address = request.form.get("address")
        phone_no = request.form.get("phone_no")
        city = request.form.get("city")
        pincode = request.form.get("pincode")
        email = request.form.get("email")
        password = request.form.get('password')
        emails = [email[0] for email in db.session.query(Customer.email_id).all()]
        if email in emails:
            flash("Email already exists")
            return redirect(url_for('customer_signup'))
        new_customer = Customer(name=name, address=address, phone_no=phone_no, city=city, pincode=pincode, email_id=email, password=password, login_status=0,status='active')
        db.session.add(new_customer)
        db.session.commit()
        flash("Successfully registered !!!!")
        flash("HomeVibes awaits you. Login now !!!")
        return redirect(url_for('customer_login'))
    
@app.route('/customer/<customer_id>')
def customer(customer_id):
    customer = Customer.query.filter_by(customer_id=customer_id).first()
    if  not customer:
        return render_template('dne.html',field='Customer')
    return render_template('customer.html',customer=customer)

@app.route('/customer/dashboard/<customer_id>')
def customer_dashboard(customer_id):
    customer = Customer.query.filter_by(customer_id=customer_id).first()
    if not customer:
        return render_template('dne.html',field = 'Customer')
    if customer.login_status != 1:
        flash("You need to login first.")
        return redirect(url_for('customer_login'))
    pending_requests = ServiceRequest.query.filter_by(req_customer_id=customer_id,request_status='Requested').order_by(ServiceRequest.request_date).all()
    all_requests = ServiceRequest.query.filter_by(req_customer_id=customer_id).order_by(ServiceRequest.request_date).all()
    requests = [req for req in all_requests if req.request_status=='Accepted']
    completed = [req for req in all_requests if req.request_status in ['Completed','Closed']]
    return render_template('customer_dashboard.html',customer=customer,pending_requests = pending_requests,requests=requests,completed=completed)
        
    
@app.route('/customer/bookservice/<customer_id>', methods=['GET','POST'])
def book_service(customer_id):
    customer = Customer.query.filter_by(customer_id=customer_id).first()
    if not customer:
        return render_template('dne.html',field = 'Customer')
    if customer.login_status != 1:
        flash("You need to login first.")
        return redirect(url_for('customer_login'))
    if request.method=='GET':
        type = request.args.get('type')
        services = Service.query.join(Professional).filter(Service.type == type,Professional.city == customer.city,Professional.status=='active').all()
        return render_template('book_service.html',customer=customer,services=services,service_type=type)
    elif request.method=='POST':
        service_id = request.form.get('service_id')
        date = request.form.get('request_date')
        new_request = ServiceRequest(req_service_id=service_id,req_customer_id=customer_id,request_date = date,request_status='Requested')
        db.session.add(new_request)
        db.session.commit()
        service_req = ServiceRequest.query.filter_by(req_service_id=service_id, req_customer_id=customer_id, request_date=date, request_status='Requested')\
        .order_by(ServiceRequest.request_id.desc()).first()
        professionals = Professional.query.join(Service).filter(Service.service_id == service_id,Professional.city == customer.city,Professional.status == 'active').all()
        for professional in professionals:
            profrequest = ProfessionalRequest(request_id=service_req.request_id,professional_id=professional.professional_id)
            db.session.add(profrequest)
        db.session.commit()
        flash("Service booked successfully")
        return redirect(url_for('customer_dashboard',customer_id=customer_id))
    
@app.route('/service_request/<request_id>')
def service_request(request_id):
    service_request = ServiceRequest.query.filter_by(request_id=request_id).first()
    if not service_request:
        return render_template('dne.html',field = 'Service Request')
    return render_template('service_request.html',service_req=service_request)
@app.route('/customer/cancelrequest/<customer_id>')
def cancel_service(customer_id):
    customer = Customer.query.filter_by(customer_id=customer_id).first()
    if not customer:
        return render_template('dne.html',field='Customer')
    if customer.login_status != 1:
        flash("You need to login first.")
        return redirect(url_for('customer_login'))
    request_id = request.args.get('request_id')
    service_req = ServiceRequest.query.filter_by(request_id=request_id).first()
    for prof in service_req.prof_details:
        db.session.delete(prof)
    db.session.delete(service_req)
    db.session.commit()
    flash("Service cancelled successfully")
    return redirect(url_for('customer_dashboard',customer_id=customer_id))

@app.route('/customer/editrequest/<customer_id>',methods=['GET','POST'])
def edit_request(customer_id):
    customer = Customer.query.filter_by(customer_id=customer_id).first()
    if not customer:
        return render_template('dne.html',field = 'Customer')
    if customer.login_status != 1:
        flash("You need to login first.")
        return redirect(url_for('customer_login'))
    request_id = request.form.get('request_id')
    date = request.form.get('request_date')
    req = ServiceRequest.query.filter_by(request_id=request_id).first()
    req.request_date = date
    db.session.commit()
    flash("Request updated successfully")
    return redirect(url_for('customer_dashboard',customer_id=customer_id))

@app.route('/customer/completerequest/<customer_id>',methods=['GET','POST'])
def complete_request(customer_id):
    customer = Customer.query.filter_by(customer_id=customer_id).first()
    if not customer:
        return render_template('dne.html',field = 'Customer')
    if customer.login_status != 1:
        flash("You need to login first.")
        return redirect(url_for('customer_login'))
    request_id = request.form.get('rrequest_id')
    professional_id = request.form.get('professional_id')
    stars = request.form.get('rating')
    comments = request.form.get('comments')
    service_req = ServiceRequest.query.filter_by(request_id=request_id).first()
    service_req.request_status = 'Completed'
    rating = ProfessionalRating(rcustomer_id=customer_id,rprofessional_id=professional_id,rrequest_id=request_id,stars=stars,comments=comments)
    db.session.add(rating)
    db.session.commit()
    professional = Professional.query.filter_by(professional_id=professional_id).first()
    avg = (sum([int(rating.stars) for rating in professional.ratings]))/(len(professional.ratings))
    professional.rating = avg
    db.session.commit()
    flash("Request completed successfully")
    return redirect(url_for('customer_dashboard',customer_id=customer_id))

@app.route('/customer/search/<customer_id>')
def customer_search(customer_id):
    customer = Customer.query.filter_by(customer_id=customer_id).first()
    if not customer:
        return render_template('dne.html',field = 'Customer')
    if customer.login_status != 1:
        flash("You need to login first.")
        return redirect(url_for('customer_login'))
    if not request.args:
        return render_template('customer_searchpage.html',customer=customer)
    filter = request.args.get('filter')
    search = '%' + request.args.get('search') + '%'
    services = None
    if filter == 'name':
        services = Service.query.filter(Service.name.like(search)).all()
    elif filter == 'city':
        serivces = Service.query.join(Professional).filter(Professional.city.like(search)).all()
    elif filter == 'pincode':
        services = Service.query.join(Professional).filter(Professional.pincode.like(search)).all()
    return render_template('customer_searchpage.html',customer = customer,services=services)
        

@app.route('/customer/profile/<customer_id>')
def customer_profile(customer_id):
    customer = Customer.query.filter_by(customer_id=customer_id).first()
    if not customer:
        return render_template('dne.html',field = 'Customer')
    if customer.login_status != 1:
        flash("You need to login first.")
        return redirect(url_for('customer_login'))
    return render_template('customer_profilepage.html',customer=customer)

@app.route('/customer/updateprofile/<customer_id>',methods=['GET','POST'])
def customer_updateprofile(customer_id):
    customer = Customer.query.filter_by(customer_id=customer_id).first()
    if not customer:
        return render_template('dne.html',field = 'Customer')
    if customer.login_status != 1:
        flash("You need to login first.")
        return redirect(url_for('customer_login'))
    if request.method=='GET':
        return render_template('customer_updateprofile.html',customer=customer)
    else:
        customer.name = request.form.get("name")
        customer.address = request.form.get("address")
        customer.phone_no = request.form.get("phone_no")
        customer.city = request.form.get("city")
        customer.pincode = request.form.get("pincode")
        db.session.commit()
        flash("Profile updated successfully")
        return redirect(url_for('customer_profile',customer_id=customer_id))

@app.route('/customer/summary/<customer_id>')
def customer_summary(customer_id):
    customer = Customer.query.filter_by(customer_id=customer_id).first()
    if not customer:
        return render_template('dne.html',field = 'Customer')
    if customer.login_status != 1:
        flash("You need to login first.")
        return redirect(url_for('customer_login'))
    if customer.ratings:
        rated = {'5 stars':0,'4 stars':0,'3 stars':0,'2 stars':0,'1 stars':0}
        for rating in customer.ratings:
            if rating.stars == 5:
                rated['5 stars'] += 1
            if rating.stars == 4:
                rated['4 stars'] += 1
            if rating.stars == 3:
                rated['3 stars'] += 1
            if rating.stars == 2:
                rated['2 stars'] += 1
            if rating.stars == 1:
                rated['1 stars'] += 1
        ratings_count = list(rated.values())
        colors = ['#00A3AD', '#3DAF94', '#F6A625', '#6D6E71', '#EF5D28']
        fig, ax = plt.subplots()
        ax.pie(ratings_count,colors=colors,startangle=90,autopct=None)
        ax.axis('equal')
        centre_circle = plt.Circle((0, 0), 0.70, fc='white')
        fig.gca().add_artist(centre_circle)
        plt.text(0, 0, f'Overall Rating\n{customer.rating:.1f}/5', ha='center', va='center', fontsize=12)
        legend_labels = ['5 stars - Very Good', '4 stars - Good', '3 stars - Average', '2 stars - Fair', '1 star - Poor']
        handles = [plt.Line2D([0], [0], marker='o', color='w', label=label, markersize=10, markerfacecolor=color) for label, color in zip(legend_labels, colors)]
        plt.legend(handles=handles, loc='upper left', bbox_to_anchor=(0.8,0.3))
        plt.title('Your Rating Distribution')
        chart_path = os.path.join('static','images','customer_rating.png')
        plt.savefig(chart_path, bbox_inches='tight')
        plt.close()
    request_data = {'Requested':0,'Assigned':0,'Completed':0,'Closed':0}
    for req in customer.requests:
        if req.request_status == 'Requested':
            request_data['Requested'] += 1
        if req.request_status == 'Accepted':
            request_data['Assigned'] += 1
        if req.request_status == 'Completed':
            request_data['Completed'] += 1
        if req.request_status == 'Closed':
            request_data['Closed'] += 1
    labels = request_data.keys()
    values = request_data.values()
    fig, ax = plt.subplots()
    bars = ax.bar(labels, values, color=['#F44336', '#FFC107', '#4CAF50', '#2196F3'])
    ax.set_title('Service Request Status Distribution')
    ax.set_xlabel('Request Status')
    ax.set_ylabel('Number of Requests')
    ax.set_ylim(0, max(values) + 1)
    for bar in bars:
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, yval, yval, ha='center', va='bottom')
    chart_path = os.path.join('static', 'images', 'customer_servicerequest.png')
    plt.savefig(chart_path, bbox_inches='tight')
    plt.close()
    return render_template('customer_summarypage.html',customer=customer)

@app.route('/customer/logout/<customer_id>')
def customer_logout(customer_id):
    customer = Customer.query.filter_by(customer_id=customer_id).first()
    if not customer:
        return render_template('dne.html',field = 'Customer')
    if customer.login_status != 1:
        flash("You need to login first.")
        return redirect(url_for('customer_login'))
    customer.login_status = 0
    db.session.commit()
    flash("Successfully logged out.")
    flash("Thank you for browsing.")
    return redirect(url_for('customer_login'))

@app.route('/professional/login',methods=["GET","POST"])
def professional_login():
    if request.method == "GET":
        return render_template('professional_login.html')
    elif request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        professional = Professional.query.filter_by(email_id=email).first()
        if not professional:
            flash("User not found")
            return redirect(url_for('professional_login'))
        if professional.password != password:
            flash("Invalid password")
            return redirect(url_for('professional_login'))
        professional.login_status = 1
        db.session.commit()
        return redirect(url_for('professional_dashboard',professional_id=professional.professional_id))
        
@app.route('/professional/sign_up',methods=["GET","POST"])
def professional_signup():
    if request.method == "GET":
        type = request.args.get('type')
        services = Service.query.filter_by(type=type).all()
        if not type:
            flash("Please select service type for continuing signing up.")
            return render_template('professional_signup.html')
        if  not services:
            flash("Thank you for your interest! Currently, the service you're looking for isn't available, please choose another service")
            return render_template('professional_signup.html')
        return render_template('professional_signup.html',services = services)
    elif request.method == "POST":
        name = request.form.get("name")
        address = request.form.get("address")
        phone_no = request.form.get("phone_no")
        city = request.form.get("city")
        pincode = request.form.get("pincode")
        email = request.form.get("email")
        password = request.form.get('password')
        service_id = request.form.get('service_id')
        experience = request.form.get('experience')
        file = request.files['resume'].read()
        emails = [email[0] for email in db.session.query(Professional.email_id).all()]
        if email in emails:
            flash("Email already exists")
            return redirect(url_for('professional_signup'))
        new_professional = Professional(name=name, address=address, phone_no=phone_no, city=city, pincode=pincode, email_id=email, password=password, service_id=service_id, experience=experience, resume=file,status='under-verification',login_status = 0)
        db.session.add(new_professional)
        db.session.commit()
        flash("Successfully registered !!!!")
        flash("HomeVibes awaits you. Login now !!!")
        return redirect(url_for('professional_login'))
    
@app.route('/professional/<professional_id>')
def professional(professional_id):
    professional = Professional.query.filter_by(professional_id=professional_id).first()
    if not professional:
        return render_template('dne.html',field='Professional')
    return render_template('professional.html',professional=professional)

@app.route('/professional/dashboard/<professional_id>')
def professional_dashboard(professional_id):
    professional = Professional.query.filter_by(professional_id=professional_id).first()
    if not professional:
        return render_template('dne.html',field='Professional')
    if professional.login_status != 1:
        flash("You need to login first.")
        return redirect(url_for('professional_login'))
    pending_requests =  [request for request in professional.requests if request.details.request_status=='Requested']
    requests = [request for request in professional.requests if request.details.request_status=='Accepted']
    completed = [request for request in professional.requests if request.details.request_status in ['Completed','Closed']]
    return render_template('professional_dashboard.html',professional=professional,pending_requests=pending_requests,requests=requests,completed=completed)
        
@app.route('/professional/acceptrequest/<professional_id>')
def accept_request(professional_id):
    professional = Professional.query.filter_by(professional_id=professional_id).first()
    if not professional:
        return render_template('dne.html',field='Professional')
    if professional.login_status != 1:
        flash("You need to login first.")
        return redirect(url_for('professional_login'))
    request_id = request.args.get('request_id')
    service_req = ServiceRequest.query.filter_by(request_id=request_id).first()
    service_req.request_status = 'Accepted'
    requests = ProfessionalRequest.query.filter_by(request_id=request_id).all()
    for req in requests:
        if req.professional_id != int(professional_id):
            db.session.delete(req)
    db.session.commit()
    flash('Request Accepted.')
    return redirect(request.referrer)

@app.route('/professional/rejectrequest/<professional_id>')
def reject_request(professional_id):
    professional = Professional.query.filter_by(professional_id=professional_id).first()
    if not professional:
        return render_template('dne.html',field='Professional')
    if professional.login_status != 1:
        flash("You need to login first.")
        return redirect(url_for('professional_login'))
    request_id = request.args.get('request_id')
    req = ProfessionalRequest.query.filter_by(professional_id=professional_id,request_id=request_id).first()
    db.session.delete(req)
    db.session.commit()
    flash('Request Rejected.')
    return redirect(request.referrer)

@app.route('/professional/closerequest/<professional_id>', methods=['GET','POST'])
def close_request(professional_id):
    professional = Professional.query.filter_by(professional_id=professional_id).first()
    if not professional:
        return render_template('dne.html',field='Professional')
    if professional.login_status != 1:
        flash("You need to login first.")
        return redirect(url_for('professional_login'))
    request_id = request.form.get('request_id')
    customer_id = request.form.get('customer_id')
    stars = request.form.get("rating")
    comments = request.form.get("comments")
    service_req = ServiceRequest.query.filter_by(request_id=request_id).first()
    service_req.request_status = 'Closed'
    rating = CustomerRating(rprofessional_id=professional_id,rcustomer_id=customer_id,rrequest_id=request_id,stars=stars,comments=comments)
    db.session.add(rating)
    db.session.commit()
    customer = Customer.query.filter_by(customer_id=customer_id).first()
    avg = (sum([int(rating.stars) for rating in customer.ratings]))/(len(customer.ratings))
    customer.rating = avg
    db.session.commit()
    flash('Request Closed.')
    return redirect(url_for('professional_dashboard',professional_id=professional_id))

@app.route('/professional/profile/<professional_id>')
def professional_profile(professional_id):
    professional = Professional.query.filter_by(professional_id=professional_id).first()
    if not professional:
        return render_template('dne.html',field='Professional')
    if professional.login_status != 1:
        flash("You need to login first.")
        return redirect(url_for('professional_login'))
    return render_template('professional_profilepage.html',professional=professional)

@app.route('/professional/resume/<professional_id>')
def professional_resume(professional_id):
    professional = Professional.query.filter_by(professional_id=professional_id).first()
    if not professional:
        return render_template('dne.html',field='Professional')
    if professional.login_status != 1:
        flash("You need to login first.")
        return redirect(url_for('professional_login'))
    if not professional.resume:
        flash('No resume found')
        return redirect(url_for('professional_profile',professional_id=professional_id))
    return Response(professional.resume, mimetype='application/pdf')

@app.route('/professional/updateprofile/<professional_id>',methods=['GET','POST'])
def professional_updateprofile(professional_id):
    professional = Professional.query.filter_by(professional_id=professional_id).first()
    if not professional:
        return render_template('dne.html',field='Professional')
    if professional.login_status != 1:
        flash("You need to login first.")
        return redirect(url_for('professional_login'))
    if request.method == 'GET':
        return render_template('professional_updateprofile.html',professional=professional)
    elif request.method == 'POST':
        professional.name = request.form.get("name")
        professional.address = request.form.get("address")
        professional.phone_no = request.form.get("phone_no")
        professional.city = request.form.get("city")
        professional.pincode = request.form.get("pincode")
        professional.experience = request.form.get('experience')
        db.session.commit()
        flash('Profile Updated.')
        return redirect(url_for('professional_profile',professional_id=professional_id))
    
@app.route('/professional/search/<int:professional_id>',methods=['GET','POST'])
def professional_search(professional_id):
    professional = Professional.query.filter_by(professional_id=professional_id).first()
    if not professional:
        return render_template('dne.html',field='Professional')
    if professional.login_status != 1:
        flash("You need to login first.")
        return redirect(url_for('professional_login'))
    if not request.args:
        return render_template('professional_searchpage.html',professional=professional)
    filter = request.args.get('filter')
    search = '%' + request.args.get('search') + '%'
    requests = None
    if filter == 'date':
        requests = ProfessionalRequest.query.join(ServiceRequest).filter(ProfessionalRequest.professional_id==professional_id,ServiceRequest.request_date.like(search)).all()
    elif filter == 'city':
        requests = ProfessionalRequest.query.join(ServiceRequest).join(Customer).filter(ProfessionalRequest.professional_id==professional_id,Customer.city.like(search)).all()
    elif filter == 'pincode':
        requests = ProfessionalRequest.query.join(ServiceRequest).join(Customer).filter(ProfessionalRequest.professional_id==professional_id,Customer.pincode.like(search)).all()
    return render_template('professional_searchpage.html',professional=professional,requests=requests)

@app.route('/professional/summary/<professional_id>')
def professional_summary(professional_id):
    professional = Professional.query.filter_by(professional_id=professional_id).first()
    if not professional:
        return render_template('dne.html',field='Professional')
    if professional.login_status != 1:
        flash("You need to login first.")
        return redirect(url_for('professional_login'))
    rated = {'5 stars':0,'4 stars':0,'3 stars':0,'2 stars':0,'1 stars':0}
    if professional.ratings:
        for rating in professional.ratings:
            if rating.stars == 5:
                rated['5 stars'] += 1
            if rating.stars == 4:
                rated['4 stars'] += 1
            if rating.stars == 3:
                rated['3 stars'] += 1
            if rating.stars == 2:
                rated['2 stars'] += 1
            if rating.stars == 1:
                rated['1 stars'] += 1
        ratings_count = list(rated.values())
        colors = ['#00A3AD', '#3DAF94', '#F6A625', '#6D6E71', '#EF5D28']
        fig, ax = plt.subplots()
        ax.pie(ratings_count,colors=colors,startangle=90,autopct=None)
        ax.axis('equal')
        centre_circle = plt.Circle((0, 0), 0.70, fc='white')
        fig.gca().add_artist(centre_circle)
        plt.text(0, 0, f'Overall Rating\n{professional.rating:.1f}/5', ha='center', va='center', fontsize=12)
        legend_labels = ['5 stars - Very Good', '4 stars - Good', '3 stars - Average', '2 stars - Fair', '1 star - Poor']
        handles = [plt.Line2D([0], [0], marker='o', color='w', label=label, markersize=10, markerfacecolor=color) for label, color in zip(legend_labels, colors)]
        plt.legend(handles=handles, loc='upper left', bbox_to_anchor=(0.8,0.3))
        plt.title('Your Rating Distribution')
        chart_path = os.path.join('static','images','professional_rating.png')
        plt.savefig(chart_path, bbox_inches='tight')
        plt.close()
    request_data = {'Assigned':0,'Completed':0,'Closed':0}
    for req in professional.requests:
        if req.details.request_status == 'Accepted':
            request_data['Assigned'] += 1
        if req.details.request_status == 'Completed':
            request_data['Completed'] += 1
        if req.details.request_status == 'Closed':
            request_data['Closed'] += 1
    labels = request_data.keys()
    values = request_data.values()
    fig, ax = plt.subplots()
    bars = ax.bar(labels, values, color=['#FFC107', '#4CAF50', '#2196F3'])
    ax.set_title('Service Request Status Distribution')
    ax.set_xlabel('Request Status')
    ax.set_ylabel('Number of Requests')
    ax.set_ylim(0, max(values) + 1)
    for bar in bars:
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, yval, yval, ha='center', va='bottom')
    chart_path = os.path.join('static', 'images', 'professional_servicerequest.png')
    plt.savefig(chart_path, bbox_inches='tight')
    plt.close()
    return render_template('professional_summarypage.html',professional=professional)

@app.route('/professional/logout/<professional_id>')
def professional_logout(professional_id):
    professional = Professional.query.filter_by(professional_id=professional_id).first()
    if not professional:
        return render_template('dne.html',field='Professional')
    if professional.login_status != 1:
        flash("You need to login first.")
        return redirect(url_for('professional_login'))
    professional.login_status = 0
    db.session.commit()
    flash('Successfully logged out.')
    return redirect(url_for('professional_login'))

@app.route('/admin/login',methods=["GET","POST"])
def admin_login():
    if request.method == "GET":
        return render_template('admin_login.html')
    elif request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        admin = Admin.query.filter_by(email_id=email).first()
        if not admin:
            flash("Access denied. You are not an admin.")
            return redirect(url_for('admin_login'))
        if admin.password != password:
                flash("Access denied. Invalid password.")
                return redirect(url_for('admin_login'))
        admin.login_status = 1
        db.session.commit()
        return redirect(url_for('admin_dashboard',admin_id=admin.admin_id))
    
@app.route('/service/<service_id>')
def service(service_id):
    service = Service.query.filter_by(service_id=service_id).first()
    if not service:
        return render_template('dne.html',field='Service')
    return render_template('service.html',service=service)

@app.route('/admin/dashboard/<admin_id>')
def admin_dashboard(admin_id):
    admin = Admin.query.filter_by(admin_id=admin_id).first()
    if not admin:
        return render_template('dne.html',field='Admin')
    if admin.login_status != 1:
        flash("You need to login first.")
        return redirect(url_for('admin_login'))
    services = Service.query.all()
    professionals = Professional.query.all()
    customers = Customer.query.all()
    return render_template('admin_dashboard.html',admin=admin,services=services,professionals=professionals,customers=customers)
        
@app.route('/admin/addservice/<admin_id>',methods=["POST"])
def add_service(admin_id):
    admin = Admin.query.filter_by(admin_id=admin_id).first()
    if not admin:
        return render_template('dne.html',field='Admin')
    if admin.login_status != 1:
        flash("You need to login first.")
        return redirect(url_for('admin_login'))
    name = request.form.get('name')
    description = request.form.get('description')
    base_price = request.form.get('base_price')
    time_required = request.form.get('time_required')
    type = request.form.get('type')
    new_service = Service(name=name,description=description,base_price=base_price,time_required=time_required,type=type)
    db.session.add(new_service)
    db.session.commit()
    flash("Service added successfully.")
    return redirect(url_for('admin_dashboard',admin_id=1))

@app.route('/admin/updateservice/<admin_id>',methods=['GET','POST'])
def update_service(admin_id):
    admin = Admin.query.filter_by(admin_id=admin_id).first()
    if not admin:
        return render_template('dne.html',field='Admin')
    if admin.login_status != 1:
        flash("You need to login first.")
        return redirect(url_for('admin_login'))
    service_id = request.args.get('service_id')
    service = Service.query.filter_by(service_id=service_id).first()
    if request.method == 'GET':
        return render_template('update_service.html',service=service,admin=admin)
    elif request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        base_price = request.form.get('base_price')
        time_required = request.form.get('time_required')
        type = request.form.get('type')
        service.name = name
        service.description = description
        service.base_price = base_price
        service.time_required = time_required
        service.type = type
        db.session.commit()
        flash("Service updated successfully.")
        return redirect(url_for('admin_dashboard',admin_id=admin_id))
    
@app.route('/admin/deleteservice/<admin_id>')
def delete_service(admin_id):
    admin = Admin.query.filter_by(admin_id=admin_id).first()
    if not admin:
        return render_template('dne.html',field='Admin')
    if admin.login_status != 1:
        flash("You need to login first.")
        return redirect(url_for('admin_login'))
    service_id = request.args.get('service_id')
    service = Service.query.filter_by(service_id=service_id).first()
    for professional in service.professionals:
        for rating in professional.ratings:
            db.session.delete(rating)
        for rating in professional.customer_ratings:
            db.session.delete(rating)
        for req in professional.requests:
            db.session.delete(req)
        db.session.delete(professional)
    service_reqs = ServiceRequest.query.filter_by(req_service_id=service_id).all()
    for req in service_reqs:
        db.session.delete(req)
    db.session.delete(service)
    db.session.commit()
    flash("Service deleted successfully.")
    return redirect(request.referrer)

@app.route('/admin/deleteprofessional/<admin_id>')
def delete_professional(admin_id):
    admin = Admin.query.filter_by(admin_id=admin_id).first()
    if not admin:
        return render_template('dne.html',field='Admin')
    if admin.login_status != 1:
        flash("You need to login first.")
        return redirect(url_for('admin_login'))
    professional_id = request.args.get('professional_id')
    professional = Professional.query.filter_by(professional_id=professional_id).first()
    for rating in professional.ratings:
        db.session.delete(rating)
    for rating in professional.customer_ratings:
        db.session.delete(rating)
    for req in professional.requests:
        db.session.delete(req)
    db.session.delete(professional)
    db.session.commit()
    flash("Professional deleted successfully.")
    return redirect(request.referrer)

@app.route('/admin/deletecustomer/<admin_id>')
def delete_customer(admin_id):
    admin = Admin.query.filter_by(admin_id=admin_id).first()
    if not admin:
        return render_template('dne.html',field='Admin')
    if admin.login_status != 1:
        flash("You need to login first.")
        return redirect(url_for('admin_login'))
    customer_id = request.args.get('customer_id')
    customer = Customer.query.filter_by(customer_id=customer_id).first()
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
    flash("Customer deleted successfully.")
    return redirect(request.referrer)

@app.route('/admin/professional/resume/<admin_id>')
def verify_resume(admin_id):
    admin = Admin.query.filter_by(admin_id=admin_id).first()
    if not admin:
        return render_template('dne.html',field='Admin')
    if admin.login_status != 1:
        flash("You need to login first.")
        return redirect(url_for('admin_login'))
    professional_id = request.args.get('professional_id')
    professional = Professional.query.filter_by(professional_id=professional_id).first()
    if not professional.resume:
        flash('No resume found')
        return redirect(url_for('admin_dashboard',admin_id=1))
    return Response(professional.resume, mimetype='application/pdf')
        
@app.route('/admin/professional/status/<admin_id>')
def active_professional(admin_id):
    admin = Admin.query.filter_by(admin_id=admin_id).first()
    if not admin:
        return render_template('dne.html',field='Admin')
    if admin.login_status != 1:
        flash("You need to login first.")
        return redirect(url_for('admin_login'))
    professional_id = request.args.get('professional_id')
    print(professional_id)
    status = request.args.get('status')
    professional = Professional.query.filter_by(professional_id=professional_id).first()
    professional.status = status
    db.session.commit()
    return redirect(request.referrer)

@app.route('/admin/customer/status/<admin_id>')
def active_customer(admin_id):
    admin = Admin.query.filter_by(admin_id=admin_id).first()
    if not admin:
        return render_template('dne.html',field='Admin')
    if admin.login_status != 1:
        flash("You need to login first.")
        return redirect(url_for('admin_login'))
    customer_id = request.args.get('customer_id')
    status = request.args.get('status')
    customer = Customer.query.filter_by(customer_id=customer_id).first()
    customer.status = status
    db.session.commit()
    return redirect(request.referrer)

@app.route('/admin/search/<admin_id>')
def admin_search(admin_id):
    admin = Admin.query.filter_by(admin_id=admin_id).first()
    if not admin:
        return render_template('dne.html',field='Admin')
    if admin.login_status != 1:
        flash("You need to login first.")
        return redirect(url_for('admin_login'))
    if not request.args:
        return render_template('admin_searchpage.html',admin=admin)
    term = request.args.get('term')
    filter =  request.args.get('filter')
    search = '%' + request.args.get('search') + '%'
    fields = None
    if not term:
        flash('Please select valid term')
        return redirect(url_for('admin_search',admin_id=1))
    if not filter:
        flash('Please select valid filter')
        return redirect(url_for('admin_search',admin_id=1))
    if term == 'Services':
        if filter == 'name':
            fields = Service.query.filter(Service.name.like(search)).all()
        elif filter == 'city':
            fields = Service.query.join(Professional).filter(Professional.city.like(search)).all()
        elif filter == 'pincode':
            fields = Service.query.join(Professional).filter(Professional.pincode.like(search)).all()
    elif term == 'Professionals':
        if filter == 'name':
            fields = Professional.query.join(Service).filter(Service.name.like(search)).all()
        elif filter == 'city':
            fields = Professional.query.filter(Professional.city.like(search)).all()
        elif filter == 'pincode':
            fields = Professional.query.filter(Professional.pincode.like(search)).all()
    return render_template('admin_searchpage.html',fields=fields,admin=admin,term=term)

@app.route('/admin/summary/<admin_id>')
def admin_summary(admin_id):
    admin = Admin.query.filter_by(admin_id=admin_id).first()
    if not admin:
        return render_template('dne.html',field='Admin')
    if admin.login_status != 1:
        flash("You need to login first.")
        return redirect(url_for('admin_login'))
    customers = Customer.query.all()
    rated = {'5 stars':0,'4 stars':0,'3 stars':0,'2 stars':0,'1 stars':0}
    for customer in customers:
        for rating in customer.ratings:
            if rating.stars == 5:
                rated['5 stars'] += 1
            if rating.stars == 4:
                rated['4 stars'] += 1
            if rating.stars == 3:
                rated['3 stars'] += 1
            if rating.stars == 2:
                rated['2 stars'] += 1
            if rating.stars == 1:
                rated['1 stars'] += 1
    ratings_count = list(rated.values())
    colors = ['#00A3AD', '#3DAF94', '#F6A625', '#6D6E71', '#EF5D28']
    fig, ax = plt.subplots()
    ax.pie(ratings_count,colors=colors,startangle=90,autopct=None)
    ax.axis('equal')
    centre_circle = plt.Circle((0, 0), 0.70, fc='white')
    fig.gca().add_artist(centre_circle)
    plt.text(0, 0, f'Overall Platform Rating\n{customer.rating:.1f}/5', ha='center', va='center', fontsize=12)
    legend_labels = ['5 stars - Very Good', '4 stars - Good', '3 stars - Average', '2 stars - Fair', '1 star - Poor']
    handles = [plt.Line2D([0], [0], marker='o', color='w', label=label, markersize=10, markerfacecolor=color) for label, color in zip(legend_labels, colors)]
    plt.legend(handles=handles, loc='upper left', bbox_to_anchor=(0.8,0.3))
    plt.title('Customer Rating Distribution')
    chart_path = os.path.join('static','images','platform_rating.png')
    plt.savefig(chart_path, bbox_inches='tight')
    plt.close()
    request_data = {'Requested':0,'Assigned':0,'Completed':0,'Closed':0}
    for customer in customers:
        for req in customer.requests:
            if req.request_status == 'Requested':
                request_data['Requested'] += 1
            if req.request_status == 'Accepted':
                request_data['Assigned'] += 1
            if req.request_status == 'Completed':
                request_data['Completed'] += 1
            if req.request_status == 'Closed':
                request_data['Closed'] += 1
    labels = request_data.keys()
    values = request_data.values()
    fig, ax = plt.subplots()
    bars = ax.bar(labels, values, color=['#F44336', '#FFC107', '#4CAF50', '#2196F3'])
    ax.set_title('Overall Service Request Status')
    ax.set_xlabel('Request Status')
    ax.set_ylabel('Number of Requests')
    ax.set_ylim(0, max(values) + 1)
    for bar in bars:
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, yval, yval, ha='center', va='bottom')
    chart_path = os.path.join('static', 'images', 'platform_servicerequest.png')
    plt.savefig(chart_path, bbox_inches='tight')
    plt.close()
    return render_template('admin_summarypage.html',admin=admin)

@app.route('/admin/logout/<admin_id>')
def admin_logout(admin_id):
    admin = Admin.query.filter_by(admin_id=admin_id).first()
    if not admin:
        return render_template('dne.html',field='Admin')
    if admin.login_status != 1:
        flash("You need to login first.")
        return redirect(url_for('admin_login'))
    admin.login_status = 0
    db.session.commit()
    flash('Successfully logged out.')
    flash('Thank you for browsing.')
    return redirect(url_for('admin_login'))

@app.route('/admin/<admin_id>/deleteall',methods=["GET","POST"])
def deleteall(admin_id):
    admin = Admin.query.filter_by(admin_id=admin_id).first()
    if not admin:
        return render_template('dne.html',field='Admin')
    if admin.login_status != 1:
        flash("You need to login first.")
        return redirect(url_for('admin_login'))
    services = Service.query.all()
    for service in services:
        for professional in service.professionals:
            for rating in professional.ratings:
                db.session.delete(rating)
            for rating in professional.customer_ratings:
                db.session.delete(rating)
            for req in professional.requests:
                db.session.delete(req)
            db.session.delete(professional)
        service_reqs = ServiceRequest.query.filter_by(req_service_id=service.service_id).all()
        for req in service_reqs:
            db.session.delete(req)
        db.session.delete(service)
    db.session.commit()
    flash("All Services deleted successfully.")
    return redirect(request.referrer)
    