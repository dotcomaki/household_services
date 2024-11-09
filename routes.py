# Debug check
print("routes.py is being imported")

from wtforms.validators import DataRequired, Optional
from flask import render_template, redirect, url_for, flash, request, send_from_directory
from app import app, db
from datetime import datetime
from forms import LoginForm, RegistrationForm, ServiceForm, ServiceRequestForm, SearchForm, EditUserForm, RatingForm
from models import User, Service, ServiceRequest
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os

ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
        # Handle professional specific fields
        if form.role.data == 'professional':
            user.service_type = form.service_type.data
            user.experience = int(form.experience.data)
            # Handle resume upload
            if 'resume' not in request.files:
                flash('No resume file part')
                return redirect(request.url)
            file = request.files['resume']
            if file.filename == '':
                flash('No selected resume file')
                return redirect(request.url)
            if form.resume.data:
                filename = secure_filename(form.resume.data.filename)
                unique_filename = f"{user.username}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{filename}"
                form.resume.data.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_filename))
                user.resume_filename = unique_filename
                user.approval_status = 'pending'
            else:
                flash('Invalid file type. Only PDF files are allowed.')
                return redirect(request.url)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful. Your account is pending approval.')
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
                if user.approval_status == 'approved':
                    login_user(user)
                    return redirect(url_for('professional_dashboard'))
                elif user.approval_status == 'blocked':
                    flash('Your account has been blocked by the admin.')
                    return redirect(url_for('index'))
                else:
                    flash('Your account is pending approval.')
                    return redirect(url_for('index'))
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

# Services Route
@app.route('/services')
def services():
    services = Service.query.all()
    return render_template('services.html', services=services)



## ADMIN ROUTES ##



# Admin Dashboard Route
@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        flash('Access denied.')
        return redirect(url_for('index'))
    services = Service.query.all()
    professionals = User.query.filter_by(role='professional').all()
    service_requests = ServiceRequest.query.all()
    pending_professionals = User.query.filter_by(role='professional', approval_status='pending').all()
    rated_service_requests = ServiceRequest.query.filter(ServiceRequest.rating.isnot(None)).all()
    return render_template('admin_dashboard.html', services=services, professionals=professionals, service_requests=service_requests, pending_professionals=pending_professionals, rated_service_requests=rated_service_requests)

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
    user = User.query.get_or_404(user_id)
    form = EditUserForm(obj=user)
    
    if user.role == 'professional':
        # For professionals, these fields are required
        form.service_type.validators = [DataRequired()]
        form.experience.validators = [DataRequired()]
    else:
        # For customers, these fields are optional
        form.service_type.validators = [Optional()]
        form.experience.validators = [Optional()]
    
    if form.validate_on_submit():
        user.username = form.username.data
        if form.password.data:
            hashed_password = generate_password_hash(form.password.data)
            user.password = hashed_password
        # Update professional-specific fields
        if user.role == 'professional':
            user.service_type = form.service_type.data
            user.experience = form.experience.data
            user.is_approved = form.is_approved.data
        db.session.commit()
        flash('User updated successfully.')
        return redirect(url_for('admin_dashboard'))
    
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
@app.route('/delete_service/<int:service_id>', methods=['POST'])
@login_required
def delete_service(service_id):
    if current_user.role != 'admin':
        flash('Access denied.')
        return redirect(url_for('index'))

    service = Service.query.get_or_404(service_id)

    associated_requests = ServiceRequest.query.filter_by(service_id=service.id).first()
    if associated_requests:
        flash('Cannot delete service. There are service requests associated with this service.')
        return redirect(url_for('admin_dashboard'))

    db.session.delete(service)
    db.session.commit()
    flash('Service deleted successfully.')
    return redirect(url_for('admin_dashboard'))

# Serve Resume Files
@app.route('/view_resume/<filename>')
@login_required
def view_resume(filename):
    if current_user.role != 'admin':
        flash('Access denied.')
        return redirect(url_for('index'))
    
    filename = secure_filename(filename)

    resume_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    if not os.path.exists(resume_path):
        flash('Resume file not found.')
        return redirect(url_for('admin_dashboard'))

    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Approve Professional Route
@app.route('/admin/approve_professional/<int:professional_id>', methods=['POST'])
@login_required
def approve_professional(professional_id):
    if current_user.role != 'admin':
        flash('Access denied.')
        return redirect(url_for('index'))

    professional = User.query.get_or_404(professional_id)
    professional.approval_status = 'approved'
    db.session.commit()
    flash(f'Professional {professional.username} has been approved.')
    return redirect(url_for('admin_dashboard'))

# Reject Professional Route
@app.route('/admin/reject_professional/<int:professional_id>', methods=['POST'])
@login_required
def reject_professional(professional_id):
    if current_user.role != 'admin':
        flash('Access denied.')
        return redirect(url_for('index'))

    professional = User.query.get_or_404(professional_id)
    professional.is_approved = False
    db.session.commit()
    flash('Professional rejected.')
    return redirect(url_for('admin_dashboard'))

# Block Professional Route
@app.route('/admin/block_professional/<int:professional_id>', methods=['POST'])
@login_required
def block_professional(professional_id):
    if current_user.role != 'admin':
        flash('Access denied.')
        return redirect(url_for('index'))

    professional = User.query.get_or_404(professional_id)
    professional.approval_status = 'blocked'
    db.session.commit()
    flash(f'Professional {professional.username} has been blocked.')
    return redirect(url_for('admin_dashboard'))

# Delete Professional Route
@app.route('/admin/delete_professional/<int:professional_id>', methods=['POST'])
@login_required
def delete_professional(professional_id):
    if current_user.role != 'admin':
        flash('Access denied.')
        return redirect(url_for('index'))

    professional = User.query.get_or_404(professional_id)
    db.session.delete(professional)
    db.session.commit()
    flash('Professional deleted successfully.')
    return redirect(url_for('admin_dashboard'))

# Search Route
@app.route('/admin/search', methods=['GET', 'POST'])
@login_required
def admin_search():
    if current_user.role != 'admin':
        flash('Access denied.')
        return redirect(url_for('index'))

    results = None
    if request.method == 'POST':
        search_by = request.form.get('search_by')
        search_query = request.form.get('search_query')
        if search_by == 'service_request':
            results = ServiceRequest.query.filter(ServiceRequest.id == search_query).all()
        elif search_by == 'customer':
            results = User.query.filter(User.role == 'customer', User.username.ilike(f'%{search_query}%')).all()
        elif search_by == 'professional':
            results = User.query.filter(User.role == 'professional', User.username.ilike(f'%{search_query}%')).all()
        elif search_by == 'service':
            results = Service.query.filter(Service.name.ilike(f'%{search_query}%')).all()
        else:
            flash('Invalid search option.')
    return render_template('admin_search.html', results=results)

# Summary Route
@app.route('/admin/summary')
@login_required
def admin_summary():
    if current_user.role != 'admin':
        flash('Access denied.')
        return redirect(url_for('index'))
    return render_template('admin_summary.html')


## PROFESSIONAL ROUTES ##



# Professional Dashboard
@app.route('/professional_dashboard')
@login_required
def professional_dashboard():
    if current_user.role != 'professional' or current_user.approval_status != 'approved':
        flash('Access denied or account not approved.')
        return redirect(url_for('index'))

    # Define the statuses for assigned (open) tasks
    assigned_statuses = ['accepted', 'in_progress']

    # Fetch assigned (open) tasks
    assigned_requests = ServiceRequest.query.filter(
        ServiceRequest.professional_id == current_user.id,
        ServiceRequest.service_status.in_(assigned_statuses)
    ).all()

    # Define the statuses for closed tasks
    closed_statuses = ['completed', 'cancelled']

    # Fetch closed tasks
    closed_requests = ServiceRequest.query.filter(
        ServiceRequest.professional_id == current_user.id,
        ServiceRequest.service_status.in_(closed_statuses)
    ).all()

    # Fetch ratings received
    rated_requests = ServiceRequest.query.filter(
        ServiceRequest.professional_id == current_user.id,
        ServiceRequest.rating.isnot(None)
    ).all()

    # Calculate average rating
    average_rating = db.session.query(db.func.avg(ServiceRequest.rating)).filter(
        ServiceRequest.professional_id == current_user.id,
        ServiceRequest.rating.isnot(None)
    ).scalar()
    if average_rating:
        average_rating = round(average_rating, 2)

    # Debug Check
    print(f"Assigned Requests Count: {len(assigned_requests)}")
    for req in assigned_requests:
        print(f"Assigned - ID: {req.id}, Status: {req.service_status}")

    print(f"Closed Requests Count: {len(closed_requests)}")
    for req in closed_requests:
        print(f"Closed - ID: {req.id}, Status: {req.service_status}")

    return render_template(
        'professional_dashboard.html',
        assigned_requests=assigned_requests,
        closed_requests=closed_requests,
        rated_requests=rated_requests,
        average_rating=average_rating
    )

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
@app.route('/accept_request/<int:request_id>', methods=['POST', 'GET'])
@login_required
def accept_request(request_id):
    if current_user.role != 'professional':
        flash('Access denied.')
        return redirect(url_for('index'))

    service_request = ServiceRequest.query.get_or_404(request_id)

    if service_request.professional_id:
        flash('This request has already been assigned.')
        return redirect(url_for('view_requests'))

    service_request.professional_id = current_user.id
    service_request.service_status = 'accepted'
    db.session.commit()

    flash('Service request accepted and assigned to you.')
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

# Complete Request Route
@app.route('/complete_request/<int:request_id>', methods=['POST'])
@login_required
def complete_request(request_id):
    if current_user.role != 'professional':
        flash('Access denied.')
        return redirect(url_for('index'))

    service_request = ServiceRequest.query.get_or_404(request_id)

    if service_request.professional_id != current_user.id:
        flash('You are not authorized to complete this service request.')
        return redirect(url_for('professional_dashboard'))

    service_request.service_status = 'completed'
    service_request.date_of_completion = datetime.utcnow()
    db.session.commit()

    flash('Service request marked as completed.')
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

# Cancel Request Route
@app.route('/cancel_request/<int:request_id>', methods=['POST'])
@login_required
def cancel_request(request_id):
    service_request = ServiceRequest.query.get_or_404(request_id)
    
    if service_request.customer_id != current_user.id:
        flash('You are not authorized to cancel this request.')
        return redirect(url_for('customer_dashboard'))

    service_request.service_status = 'cancelled'
    db.session.commit()
    flash('Your service request has been cancelled successfully.')
    return redirect(url_for('customer_dashboard'))

# Rate Professional Route
@app.route('/submit_rating/<int:service_request_id>', methods=['GET', 'POST'])
@login_required
def submit_rating(service_request_id):
    if current_user.role != 'customer':
        flash('Access denied.')
        return redirect(url_for('index'))

    service_request = ServiceRequest.query.get_or_404(service_request_id)

    if service_request.customer_id != current_user.id:
        flash('You are not authorized to rate this service.')
        return redirect(url_for('customer_dashboard'))

    if service_request.service_status != 'completed':
        flash('You can only rate completed services.')
        return redirect(url_for('customer_dashboard'))

    if service_request.rating is not None:
        flash('You have already rated this service.')
        return redirect(url_for('customer_dashboard'))

    form = RatingForm()
    if form.validate_on_submit():
        service_request.rating = form.rating.data
        service_request.remarks = form.remark.data
        db.session.commit()
        flash('Thank you for your feedback!')
        return redirect(url_for('customer_dashboard'))

    return render_template('submit_rating.html', form=form, service_request=service_request)