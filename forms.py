from flask_wtf import FlaskForm
from wtforms import (
    StringField, PasswordField, SubmitField, SelectField, IntegerField,
    TextAreaField
)
from wtforms.validators import DataRequired, Length, EqualTo, Optional, ValidationError

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(message='Username is required.'), Length(min=2, max=100)
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required.')
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(message='Please confirm your password.'),
        EqualTo('password', message='Passwords must match.')
    ])
    role = SelectField('Role', choices=[
        ('customer', 'Customer'),
        ('professional', 'Professional')
    ], validators=[DataRequired(message='Please select a role.')])
    service_type = StringField('Service Type', validators=[Optional()])
    experience = StringField('Experience (years)', validators=[Optional()])
    submit = SubmitField('Register')

    def validate(self, extra_validators=None):
        rv = FlaskForm.validate(self)
        if not rv:
            return False

        if self.role.data == 'professional':
            if not self.service_type.data:
                self.service_type.errors.append('Service Type is required for professionals.')
                return False
            if not self.experience.data:
                self.experience.errors.append('Experience is required for professionals.')
                return False
            else:
                # Validate that experience is a positive integer
                try:
                    experience_value = int(self.experience.data)
                    if experience_value < 0:
                        self.experience.errors.append('Experience must be a positive number.')
                        return False
                except ValueError:
                    self.experience.errors.append('Experience must be a valid integer.')
                    return False
        return True

    # Existing validate_username method
    def validate_username(self, username):
        from models import User
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Username already exists. Please choose a different username.')

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