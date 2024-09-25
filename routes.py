print("routes.py is being imported")

from flask import render_template, redirect, url_for, flash, request
from app import app, db
from forms import LoginForm, RegistrationForm, ServiceForm, ServiceRequestForm, SearchForm, EditUserForm
from models import User, Service, ServiceRequest
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

@app.route('/')
def index():
    return render_template('index.html')

# Registration Route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        user = User(
            username=form.username.data,
            password=hashed_password,
            role=form.role.data
        )
        # Handle professional-specific fields
        if form.role.data == 'professional':
            user.service_type = form.service_type.data
            user.experience = int(form.experience.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    else:
        print('Form did not validate.')
        print('Form errors:', form.errors)
    return render_template('register.html', form=form)

# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # Admin Login
        if form.username.data == 'admin' and form.password.data == 'admin':
            user = User.query.filter_by(username='admin').first()
            if not user:
                user = User(username='admin', password=generate_password_hash('admin'), role='admin')
                db.session.add(user)
                db.session.commit()
            login_user(user)
            return redirect(url_for('admin_dashboard'))
        
        # Customer or Professional Login
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

# Logout Route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))



## ADMIN ROUTES ##



# Admin Dashboard Route
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

# Manage Users Route
@app.route('/admin/manage_users')
@login_required
def manage_users():
    if current_user.role != 'admin':
        flash('Access denied.')
        return redirect(url_for('index'))

    users = User.query.all()
    return render_template('manage_users.html', users=users)

# Edit User Route
@app.route('/admin/edit_user/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    if current_user.role != 'admin':
        flash('Access denied.')
        return redirect(url_for('index'))

    user = User.query.get_or_404(user_id)
    form = EditUserForm(obj=user)

    if form.validate_on_submit():
        user.username = form.username.data
        user.role = form.role.data
        # Update password if provided
        if form.password.data:
            user.password = generate_password_hash(form.password.data)
        db.session.commit()
        flash('User updated successfully.')
        return redirect(url_for('manage_users'))

    return render_template('edit_user.html', form=form, user=user)

# Delete User Route
@app.route('/admin/delete_user/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    if current_user.role != 'admin':
        flash('Access denied.')
        return redirect(url_for('index'))

    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully.')
    return redirect(url_for('manage_users'))

# Edit Service Route
@app.route('/admin/edit_service/<int:service_id>', methods=['GET', 'POST'])
@login_required
def edit_service(service_id):
    if current_user.role != 'admin':
        flash('Access denied.')
        return redirect(url_for('index'))

    service = Service.query.get_or_404(service_id)
    form = ServiceForm(obj=service)

    if form.validate_on_submit():
        service.name = form.name.data
        service.base_price = form.base_price.data
        service.time_required = form.time_required.data
        service.description = form.description.data
        db.session.commit()
        flash('Service updated successfully.')
        return redirect(url_for('admin_dashboard'))

    return render_template('edit_service.html', form=form, service=service)

# Delete Service Route
@app.route('/admin/delete_service/<int:service_id>', methods=['POST'])
@login_required
def delete_service(service_id):
    if current_user.role != 'admin':
        flash('Access denied.')
        return redirect(url_for('index'))

    service = Service.query.get_or_404(service_id)
    db.session.delete(service)
    db.session.commit()
    flash('Service deleted successfully.')
    return redirect(url_for('admin_dashboard'))



## PROFESSIONAL ROUTES ##



# Professional Dashboard
@app.route('/professional/dashboard')
@login_required
def professional_dashboard():
    if current_user.role != 'professional':
        flash('Access denied.')
        return redirect(url_for('index'))

    assigned_requests = ServiceRequest.query.filter_by(professional_id=current_user.id).all()
    return render_template('professional_dashboard.html', assigned_requests=assigned_requests)

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
@app.route('/professional/accept_request/<int:request_id>', methods=['GET'])
@login_required
def accept_request(request_id):
    if current_user.role != 'professional':
        flash('Access denied.')
        return redirect(url_for('index'))

    service_request = ServiceRequest.query.get_or_404(request_id)
    if service_request.service_status != 'requested':
        flash('This request is not available.')
        return redirect(url_for('view_requests'))

    service_request.professional_id = current_user.id
    service_request.service_status = 'assigned'
    db.session.commit()
    flash('Service request accepted.')
    return redirect(url_for('professional_dashboard'))

# Reject Request Route
@app.route('/professional/reject_request/<int:request_id>', methods=['POST'])
@login_required
def reject_request(request_id):
    if current_user.role != 'professional':
        flash('Access denied.')
        return redirect(url_for('index'))

    service_request = ServiceRequest.query.get_or_404(request_id)
    if service_request.professional_id != current_user.id and service_request.professional_id is not None:
        flash('You cannot reject a request that is not assigned to you.')
        return redirect(url_for('view_requests'))

    service_request.professional_id = None
    service_request.service_status = 'requested'
    db.session.commit()
    flash('Service request rejected.')
    return redirect(url_for('professional_dashboard'))



## CUSTOMER ROUTES ##



# Customer Dashboard
@app.route('/customer/dashboard')
@login_required
def customer_dashboard():
    if current_user.role != 'customer':
        flash('Access denied.')
        return redirect(url_for('index'))

    service_requests = ServiceRequest.query.filter_by(customer_id=current_user.id).order_by(ServiceRequest.id.desc()).all()
    return render_template('customer_dashboard.html', service_requests=service_requests)

# Search Service Route
@app.route('/customer/search_service', methods=['GET', 'POST'])
@login_required
def search_services():
    if current_user.role != 'customer':
        flash('Access denied.')
        return redirect(url_for('index'))

    form = SearchForm()
    services = Service.query.all()

    if form.validate_on_submit():
        search_term = form.search_term.data
        # Modify the query to filter based on the search term
        services = Service.query.filter(Service.name.ilike(f'%{search_term}%')).all()

    return render_template('search_services.html', services=services, form=form)

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
