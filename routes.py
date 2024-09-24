from flask import render_template, redirect, url_for, flash, request
from app import app, db
from forms import LoginForm, RegistrationForm, ServiceForm, ServiceRequestForm, SearchForm
from models import User, Service, ServiceRequest
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

@app.route('/')
def index():
    return render_template('index.html')

# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # Handling Admin Login
        if form.username.data == 'admin' and form.password.data == 'admin':
            user = User.query.filter_by(username='admin').first()
            if not user:
                admin_user = User(username='admin', password=generate_password_hash('admin'), role='admin')
                db.session.add(user)
                db.session.commit()
            login_user(user)
            return redirect(url_for('admin_dashboard'))
        
        # Handle other users
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            if user.role == 'professional':
                return redirect(url_for('professional_dashboard'))
            elif user.role == 'customer':
                return redirect(url_for('customer_dashboard'))
        else:
            flash('Invalid username or password')
    return render_template('login.html', form=form)

# Registration Route
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        if form.role.data == 'professional':
            user = User(
                username=form.username.data,
                password=hashed_password,
                role='professional',
                service_type=form.service_type.data,
                experience=form.experience.data
            )
        else:
            user = User(
                username=form.username.data,
                password=hashed_password,
                role='customer'
            )
        db.session.add(user)
        db.session.commit()
        flash('Registration successful')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

# Logout Route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# Admin Dashboard
@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        flash('Access denied.')
        return redirect(url_for('index'))
    services = Service.query.all()
    return render_template('admin_dashboard.html', services=services)

# Create Service Route
@app.route('/admin/create_service', methods=['GET', 'POST'])
@login_required
def create_service():
    if current_user.role != 'admin':
        flash('Access denied.')
        return redirect(url_for('index'))
    form = ServiceForm()
    if form.validate_on_submit():
        service = Service(
            name=form.name.data,
            base_price=form.base_price.data,
            time_required=form.time_required.data,
            description=form.description.data
        )
        db.session.add(service)
        db.session.commit()
        flash('Service created successfully.')
        return redirect(url_for('admin_dashboard'))
    return render_template('create_service.html', form=form)

# Professional Dashboard
@app.route('/professional/dashboard')
@login_required
def professional_dashboard():
    if current_user.role != 'professional':
        flash ('Access denied')
        return redirect(url_for('index'))
    return render_template('professional_dashboard.html')

from models import ServiceRequest

# Service Request Route
@app.route('/professional/requests')
@login_required
def view_requests():
    if current_user.role != 'professional':
        flash('Access denied')
        return redirect(url_for('index'))
    requests = ServiceRequest.query.filter_by(service_status='requested').all()
    return render_template('professional_requests.html', requests=requests)

# Accept Request Route
@app.route('/professional/accept_request/<int:request_id>')
@login_required
def accept_request(request_id):
    if current_user.role != 'professional':
        flash('Access denied.')
        return redirect(url_for('index'))
    service_request = ServiceRequest.query.get(request_id)
    service_request.professional_id = current_user.id
    service_request.service_status = 'assigned'
    db.session.commit()
    flash('Service request accepted.')
    return redirect(url_for('professional_dashboard'))

# Customer Dashboard
@app.route('/customer/dashboard')
@login_required
def customer_dashboard():
    if current_user.role != 'customer':
        flash('Access denied.')
        return redirect(url_for('index'))
    return render_template('customer_dashboard.html')

# Search Service Route
@app.route('/customer/search_service', methods=['GET', 'POST'])
@login_required
def search_services():
    if current_user.role != 'customer':
        flash('Access denied.')
        return redirect(url_for('index'))
    services = Service.query.all()
    return render_template('search_services.html', services=services)

# Create Service Request
@app.route('/customer/request_service/<int:service_id>', methods=['GET', 'POST'])
@login_required
def request_service(service_id):
    if current_user.role != 'customer':
        flash('Access denied.')
        return redirect(url_for('index'))
    service = Service.query.get(service_id)
    service_request = ServiceRequest(
        service_id=service.id,
        customer_id=current_user.id,
        service_status='requested'
    )
    db.session.add(service_request)
    db.session.commit()
    flash('Service request created.')
    return redirect(url_for('customer_dashboard'))
