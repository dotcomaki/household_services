from flask_wtf import FlaskForm
from wtforms import (
    StringField, PasswordField, SubmitField, SelectField, IntegerField,
    TextAreaField
)
from wtforms.validators import DataRequired, Length, EqualTo, Optional

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
    search_term = StringField('Search', validators=[DataRequired()])
    submit = SubmitField('Search')

class EditUserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=100)])
    password = PasswordField('New Password', validators=[Optional()])
    confirm_password = PasswordField('Confirm New Password', validators=[
        Optional(),
        EqualTo('password', message='Passwords must match.')
    ])
    role = SelectField('Role', choices=[('admin', 'Admin'), ('professional', 'Professional'), ('customer', 'Customer')], validators=[DataRequired()])
    submit = SubmitField('Update User')