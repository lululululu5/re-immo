from datetime import datetime

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, IntegerField, DateField
from wtforms.validators import DataRequired, Email, ValidationError, EqualTo, NumberRange
import sqlalchemy as sa

from app import db
from .models import User

from .data.geo_data import country_nuts0
from .data.emissions import other_energy_types

country_choices = [(code,country) for country, code in country_nuts0.items()]
current_year = datetime.today().year

other_energy_types = [(key, value) for key,value in other_energy_types.items()]


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Remember Me")
    submit = SubmitField("Sign in")
    
class RegistrationForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    password2 = PasswordField("Repeat Password", validators=[DataRequired(), EqualTo("password", message="Password needs to be the same.")])
    submit = SubmitField("Register")
    
    
    def validate_email(self,email):
        user = db.session.scalar(sa.select(User).where(User.email == email.data))
        if user is not None: 
            raise ValidationError("User already exists, please use different email")
        
    def validate_password_strength(self, password):
        pass
        
class BuildingAssessmentForm(FlaskForm):
    address = StringField("Address", validators=[DataRequired()])
    zip = StringField("Zip", validators=[DataRequired()])
    country = SelectField("Country", choices=country_choices, validators=[DataRequired()])
    property_type = SelectField("Property Type", choices=[("RMF", "Residential Multi Family"), ("RSF", "Residential Single Family")], validators=[DataRequired()])
    size = IntegerField("Size in SQM", validators=[DataRequired(), NumberRange(min=0)])
    reporting_year = IntegerField("Reporting Year", validators=[DataRequired(), NumberRange(min=1400, max=current_year)])
    submit = SubmitField("Add Building")
    
    # Energy consumption
    grid_elec = IntegerField("Grid Electricity in kWh", validators=[NumberRange(min=0)])
    natural_gas = IntegerField("Natural Gas in kWh", validators=[NumberRange(min=0)])
    fuel_oil = IntegerField("Fuel Oil in kWh", validators=[NumberRange(min=0)])
    dist_heating = IntegerField("Dist in Heating in kWh", validators=[NumberRange(min=0)])
    dist_cooling = IntegerField("District Cooling in kWh", validators=[NumberRange(min=0)])
    o1_energy_type = SelectField("Other Type 1", choices=other_energy_types)
    o1_consumption = IntegerField("Other 1 in kWh", validators=[NumberRange(min=0)])
    o2_energy_type = SelectField("Other Type 2", choices=other_energy_types)
    o2_consumption = IntegerField("Other 2 in kWh", validators=[NumberRange(min=0)])
    
    #Fugitive Emissions
    
    
    
    def validate_address(self, address):
        pass
    
    def validate_zip(self, zip):
        pass
    
    def validate_zip_country(self, zip, country):
        pass
    
    