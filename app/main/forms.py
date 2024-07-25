from datetime import datetime
import json

from flask_wtf import FlaskForm
from flask_babel import _, lazy_gettext as _l
from wtforms import StringField, SubmitField, SelectField, IntegerField, DecimalField
from wtforms.validators import DataRequired, ValidationError, NumberRange, Optional

from app.main import bp
from app.models import FGasTypes, EnergyTypes
from app.utils import DifferentTo

from app.data.geo_data import country_nuts0
from app.data.emissions import other_energy_types, f_gas

country_choices = [(code, country) for country, code in country_nuts0.items()]
current_year = datetime.today().year

        
postal_codes = {}
postal_codes_loaded = False

@bp.before_request
def load_postal_codes():
    global postal_codes, postal_codes_loaded
    if not postal_codes_loaded:
        with open("app/data/zip_to_nuts3.json", 'r') as file:
            postal_codes = json.load(file)
        postal_codes_loaded = True



        
class BuildingAssessmentForm(FlaskForm):
    address = StringField(_l("Address*"), validators=[DataRequired()])
    zip = StringField(_l("Zip*"), validators=[DataRequired()])
    country = SelectField(_l("Country*"), choices=country_choices, validators=[DataRequired()])
    construction_year = IntegerField(_l("Construction Year*"), validators=[DataRequired(), NumberRange(min=1400, max=current_year)])
    property_type = SelectField(_l("Property Type*"), choices=[("RMF", "Residential Multi Family"), ("RSF", "Residential Single Family")], validators=[DataRequired()])
    size = IntegerField(_l("Size in SQM*"), validators=[DataRequired(), NumberRange(min=0)])
    reporting_year = IntegerField(_l("Reporting Year*"), validators=[DataRequired(), NumberRange(min=2000, max=current_year)])
    
    
    # Energy consumption
    grid_elec = DecimalField(_l("Grid Electricity in kWh"), validators=[Optional(), NumberRange(min=0)])
    natural_gas = DecimalField(_l("Natural Gas in kWh"), validators=[Optional(), NumberRange(min=0)])
    fuel_oil = DecimalField(_l("Fuel Oil in kWh"), validators=[Optional(), NumberRange(min=0)])
    dist_heating = DecimalField(_l("Dist in Heating in kWh"), validators=[Optional(), NumberRange(min=0)])
    dist_cooling = DecimalField(_l("District Cooling in kWh"), validators=[Optional(), NumberRange(min=0)])
    o1_energy_type = SelectField(
        _l("Other Type 1"),
        choices=[('', _l('Select any'))] + [(choice.name, choice.value) for choice in EnergyTypes],
        coerce=lambda x: None if x == '' else EnergyTypes[x]
    )
    o1_consumption = DecimalField(_l("Other 1 in kWh"), validators=[Optional(), NumberRange(min=0)])
    o2_energy_type = SelectField(
        _l("Other Type 2"),
        choices=[('', _l('Select any'))] + [(choice.name, choice.value) for choice in EnergyTypes],
        coerce=lambda x: None if x == '' else EnergyTypes[x],  validators=[DifferentTo("o1_energy_type", message=_l("Energy Type fields need to be different"))]
    )
    o2_consumption = DecimalField(_l("Other 2 in kWh"), validators=[Optional(), NumberRange(min=0)])
    
    #Fugitive Emissions
    f_gas_1_type = SelectField(
        _l("F-Gas 1 Type"),
        choices=[('', _l('Select any'))] + [(choice.name, choice.value) for choice in FGasTypes],
        coerce=lambda x: None if x == '' else FGasTypes[x]
    )
    f_gas_1_amount = DecimalField(_l("Leakage F Gas 1"), validators=[Optional(), NumberRange(min=0)])
    f_gas_2_type = SelectField(
        _l("F-Gas 2 Type"),
        choices=[('', _l('Select any'))] + [(choice.name, choice.value) for choice in FGasTypes],
        coerce=lambda x: None if x == '' else FGasTypes[x],  validators=[DifferentTo("f_gas_1_type", message=_l("F-Gas fields need to be different"))]
    )
    f_gas_2_amount = DecimalField(_l("Leakage F Gas 2"), validators=[Optional(), NumberRange(min=0)])
    
    #Renewables
    pv_wind_consumed= DecimalField(_l("PV and Wind consumed kWh"), validators=[Optional(), NumberRange(min=0)])
    pv_wind_exported= DecimalField(_l("PV and Wind exported kWh"), validators=[Optional(), NumberRange(min=0)])
    hp_solar_consumed= DecimalField(_l("Heatpump and Solar consumed kWh"), validators=[Optional(), NumberRange(min=0)])
    hp_solar_exported= DecimalField(_l("PV and Wind consumed kWh"), validators=[Optional(), NumberRange(min=0)])
    off_site_renewables= DecimalField(_l("Off-site renewable consumed kWh"), validators=[Optional(), NumberRange(min=0)])
    
    # Retrofit
    retrofit_year = IntegerField(_l("Planned Retrofit Year"), validators=[Optional(), NumberRange(min=current_year, max=2050)])
    retrofit_investment = DecimalField(_l("Planned Retrofit Investement in Euro"), validators=[Optional(), NumberRange(min=0)])
    
    # Submit
    submit = SubmitField(_l("Add Building"))
    
    def validate_zip(self, zip):
        """
        Check whether the zip value is valid. Cross check with country. 
        """
        country_zip = self.country.data + zip.data
        
        if country_zip not in postal_codes:
            raise ValidationError(_l("Postal Code and Country do not match."))
        

    