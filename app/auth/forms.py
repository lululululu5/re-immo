from flask_wtf import FlaskForm
from flask_babel import _, lazy_gettext as _l
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Regexp

import sqlalchemy as sa
from app.models import User
from app import db

class LoginForm(FlaskForm):
    email = StringField(_l("Email"), validators=[DataRequired(), Email()])
    password = PasswordField(_l(_l("Password")), validators=[DataRequired()])
    remember_me = BooleanField(_l("Remember Me"))
    submit = SubmitField(_l("Sign in"))
    
class RegistrationForm(FlaskForm):
    username = StringField("Name", validators=[DataRequired()])
    email = StringField(_l("Email"), validators=[DataRequired(), Email()])
    password = PasswordField((_l("Password")),
                             validators=[DataRequired(),
                                         Regexp(
                                             regex=r'^(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$',
                                             message=_l("Password must contain at least one uppercase letter, one number, and one special character, and be at least 8 characters long."))])
    password2 = PasswordField(_l("Repeat Password"), validators=[DataRequired(), EqualTo("password", message="Password needs to be the same.")])
    submit = SubmitField(_l("Register"))
    
    
    def validate_email(self,email):
        user = db.session.scalar(sa.select(User).where(User.email == email.data))
        if user is not None: 
            raise ValidationError("User already exists, please use different email")
        
    # def validate_password_strength(self, password):
    #     pass
    
class ResetPasswordRequestForm(FlaskForm):
    email = StringField(_l("Email"), validators=[DataRequired(), Email()])
    submit = SubmitField(_l("Request Password Reset"))
    
class ResetPasswordForm(FlaskForm):
    password = PasswordField(_l("New Password"), 
                             validators=[DataRequired(),
                                         Regexp(
                                             regex=r'^(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$',
                                             message=_l("Password must contain at least one uppercase letter, one number, and one special character, and be at least 8 characters long."))])
    password2 = PasswordField(_l("Repeat New Password"), validators=[DataRequired(), EqualTo("password", message=_l("Passwords must match."))])
    submit = SubmitField(_l("Update Password"))