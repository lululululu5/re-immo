from datetime import datetime
import json

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, IntegerField, DateField
from wtforms.validators import DataRequired, Email, ValidationError, EqualTo, NumberRange, Optional
import sqlalchemy as sa

from app import app, db
from .models import User, FGasTypes, EnergyTypes
from .utils import DifferentTo

from .data.geo_data import country_nuts0
from .data.emissions import other_energy_types, f_gas

country_choices = [(code, country) for country, code in country_nuts0.items()]
current_year = datetime.today().year

# postal_codes = {}

# @app.before_first_request
# def load_postal_code():
#     global postal_codes
#     with open("app/data/zip_to_nuts3.json", r) as file:
#         postal_codes = json.load(file)
        
postal_codes = {}
postal_codes_loaded = False

@app.before_request
def load_postal_codes():
    global postal_codes, postal_codes_loaded
    if not postal_codes_loaded:
        with open("app/data/zip_to_nuts3.json", 'r') as file:
            postal_codes = json.load(file)
        postal_codes_loaded = True



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
        
    # def validate_password_strength(self, password):
    #     pass
        
class BuildingAssessmentForm(FlaskForm):
    address = StringField("Address*", validators=[DataRequired()])
    zip = StringField("Zip*", validators=[DataRequired()])
    country = SelectField("Country*", choices=country_choices, validators=[DataRequired()])
    property_type = SelectField("Property Type*", choices=[("RMF", "Residential Multi Family"), ("RSF", "Residential Single Family")], validators=[DataRequired()])
    size = IntegerField("Size in SQM*", validators=[DataRequired(), NumberRange(min=0)])
    reporting_year = IntegerField("Reporting Year*", validators=[DataRequired(), NumberRange(min=1400, max=current_year)])
    submit = SubmitField("Add Building")
    
    # Energy consumption
    grid_elec = IntegerField("Grid Electricity in kWh", validators=[Optional(), NumberRange(min=0)])
    natural_gas = IntegerField("Natural Gas in kWh", validators=[Optional(), NumberRange(min=0)])
    fuel_oil = IntegerField("Fuel Oil in kWh", validators=[Optional(), NumberRange(min=0)])
    dist_heating = IntegerField("Dist in Heating in kWh", validators=[Optional(), NumberRange(min=0)])
    dist_cooling = IntegerField("District Cooling in kWh", validators=[Optional(), NumberRange(min=0)])
    o1_energy_type = SelectField(
        "Other Type 1",
        choices=[('', 'Select any')] + [(choice.name, choice.value) for choice in EnergyTypes],
        coerce=lambda x: None if x == '' else EnergyTypes[x]
    )
    o1_consumption = IntegerField("Other 1 in kWh", validators=[Optional(), NumberRange(min=0)])
    o2_energy_type = SelectField(
        "Other Type 2",
        choices=[('', 'Select any')] + [(choice.name, choice.value) for choice in EnergyTypes],
        coerce=lambda x: None if x == '' else EnergyTypes[x],  validators=[DifferentTo("o1_energy_type", message="Energy Type fields need to be different")]
    )
    o2_consumption = IntegerField("Other 2 in kWh", validators=[Optional(), NumberRange(min=0)])
    
    #Fugitive Emissions
    f_gas_1_type = SelectField(
        "F-Gas 1 Type",
        choices=[('', 'Select any')] + [(choice.name, choice.value) for choice in FGasTypes],
        coerce=lambda x: None if x == '' else FGasTypes[x]
    )
    f_gas_1_amount = IntegerField("Leakage F Gas 1", validators=[Optional(), NumberRange(min=0)])
    # f_gas_2_type = SelectField("Select F Gas 2",  choices=f_gas_types)
    f_gas_2_type = SelectField(
        "F-Gas 2 Type",
        choices=[('', 'Select any')] + [(choice.name, choice.value) for choice in FGasTypes],
        coerce=lambda x: None if x == '' else FGasTypes[x],  validators=[DifferentTo("f_gas_1_type", message="F-Gas fields need to be different")]
    )
    f_gas_2_amount = IntegerField("Leakage F Gas 2", validators=[Optional(), NumberRange(min=0)])
    
    #Renewables
    pv_wind_consumed= IntegerField("PV and Wind consumed kWh", validators=[Optional(), NumberRange(min=0)])
    pv_wind_exported= IntegerField("PV and Wind exported kWh", validators=[Optional(), NumberRange(min=0)])
    hp_solar_consumed= IntegerField("Heatpump and Solar consumed kWh", validators=[Optional(), NumberRange(min=0)])
    hp_solar_exported= IntegerField("PV and Wind consumed kWh", validators=[Optional(), NumberRange(min=0)])
    off_site_renewables= IntegerField("Off-site renewable consumed kWh", validators=[Optional(), NumberRange(min=0)])
    
    # Retrofit
    retrofit_year = IntegerField("Planned Retrofit Year", validators=[Optional(), NumberRange(min=current_year, max=2050)])
    retrofit_investment = IntegerField("Planned Retrofit Investement in Euro", validators=[Optional(), NumberRange(min=0)])
    
    def validate_zip(self, zip):
        """
        Check whether the zip value is valid. Cross check with country. 
        """
        country_zip = self.country.data + zip.data
        
        if country_zip not in postal_codes:
            raise ValidationError("Postal Code and Country do not match.")
        

    