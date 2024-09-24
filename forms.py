from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, IntegerField
from wtforms.validators import DataRequired, EqualTo

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    role = SelectField('Role', choices=[('customer', 'Customer'), ('professional', 'Service Professional')], validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password_confirm = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    service_type = StringField('Service Type')  # For professionals
    experience = IntegerField('Experience (years)')  # For professionals
    submit = SubmitField('Register')

class ServiceForm(FlaskForm):
    name = StringField('Service Name', validators=[DataRequired()])
    base_price = IntegerField('Base Price', validators=[DataRequired()])
    time_required = IntegerField('Time Required (minutes)', validators=[DataRequired()])
    description = StringField('Description')
    submit = SubmitField('Create Service')

class ServiceRequestForm(FlaskForm):
    service_id = IntegerField('Service ID', validators=[DataRequired()])
    submit = SubmitField('Request Service')

class SearchForm(FlaskForm):
    search_query = StringField('Search', validators=[DataRequired()])
    submit = SubmitField('Search')