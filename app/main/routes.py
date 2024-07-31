from flask import render_template, flash, redirect, url_for, request, jsonify
from flask_login import current_user, login_required
from flask_babel import _
import sqlalchemy as sa

from app.main.forms import BuildingAssessmentForm
from app.models import Building, Settings
from app.services.building_services import BuildingCalculations
from app import db
from app.main import bp

@bp.route("/")
def home():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    else:
        return redirect(url_for("main.landing_page"))

@bp.route("/index")
@login_required
def index():
    building = db.session.scalar(sa.select(Building).where(Building.user_id == current_user.id))
    crrem_data = {}
    stranding_year = {"year": None}
    retrofit_year = {"year": None}
    
    if building:
        settings = db.session.scalar(sa.select(Settings).where(Settings.building_id == building.id))
        baseline_emissions =  BuildingCalculations.baseline_emissions(building)["baseline_emissions"]
        ghg_emissions_2035 = BuildingCalculations.ghg_for_year(building, settings, 2035)
        if baseline_emissions > 0:
            building.baseline_emissions = round(baseline_emissions, 2)
            building.ghg_emissions_2035 = round(ghg_emissions_2035, 2)
        
        decarbonisation_targets = BuildingCalculations.decarbonisation_targets(building, settings)
        emissions_per_year = BuildingCalculations.emissions_per_year(building, settings)
        excess_emissions = BuildingCalculations.excess_emissions(building, settings)
        for k,v in excess_emissions.items():
            if v is None:
                continue
            if v > 0:
                stranding_year["year"] = k
                building.stranding_year = k
                break
        retrofit_year["year"] = building.retrofit_year
        
        crrem_data = {
            "decarbonisation_targets": decarbonisation_targets,
            "emissions_per_year": emissions_per_year,
            "excess_emissions": excess_emissions, 
            "stranding_year": stranding_year,
            "retrofit_year": retrofit_year}
        
    return render_template("index.html", building=building, crrem_data=crrem_data)

@bp.route("/landing")
def landing_page():
    return render_template("landing_page.html")


@bp.route("/add_building", methods=["GET", "POST"])
@login_required
# Add check for only having one building per person
def add_building():
    has_building = db.session.scalar(sa.select(Building).where(Building.user_id == current_user.id))
    if has_building:
        flash(_("You cannot have more than one building. But you can edit or delete your existing building."))
        return redirect(url_for("main.edit_building"))
    form = BuildingAssessmentForm()
    if form.validate_on_submit():
        building = Building(
            address=form.address.data,
            zip = form.zip.data,
            construction_year = form.construction_year.data,
            reporting_year=form.reporting_year.data,
            country = form.country.data,
            property_type = form.property_type.data,
            size = form.size.data,
            grid_elec = form.grid_elec.data,
            natural_gas = form.natural_gas.data,
            fuel_oil = form.fuel_oil.data,
            dist_heating = form.dist_heating.data,
            dist_cooling = form.dist_cooling.data,
            o1_energy_type = form.o1_energy_type.data,
            o1_consumption = form.o1_consumption.data,
            o2_energy_type = form.o2_energy_type.data,
            o2_consumption = form.o2_consumption.data,
            f_gas_1_type = form.f_gas_1_type.data,
            f_gas_1_amount = form.f_gas_1_amount.data,
            f_gas_2_type = form.f_gas_2_type.data,
            f_gas_2_amount = form.f_gas_2_amount.data,
            pv_wind_consumed= form.pv_wind_consumed.data,
            pv_wind_exported= form.pv_wind_exported.data,
            hp_solar_consumed= form.hp_solar_consumed.data,
            hp_solar_exported= form.hp_solar_exported.data,
            off_site_renewables= form.off_site_renewables.data,
            retrofit_year = form.retrofit_year.data,
            retrofit_investment = form.retrofit_investment.data,
            user_id = current_user.id
        )
        db.session.add(building)
        db.session.commit()
        s = Settings(building_id = building.id)
        db.session.add(s)
        db.session.commit()
        flash(_("Building successfully created."))
        return redirect(url_for("main.index"))
    return render_template("add_building.html", title=_("Add Building"), form=form)

@bp.route("/edit_building", methods=["GET", "POST"])
@login_required
def edit_building():
    building = db.session.scalar(sa.select(Building).where(Building.user_id == current_user.id))
    if not building:
        flash(_("You first need to add a building."))
        return redirect(url_for("main.add_building"))    
    form = BuildingAssessmentForm()
    if form.validate_on_submit():
        building.address=form.address.data
        building.zip = form.zip.data
        building.construction_year = form.construction_year.data
        building.reporting_year=form.reporting_year.data
        building.country = form.country.data
        building.property_type = form.property_type.data
        building.size = form.size.data
        building.grid_elec = form.grid_elec.data
        building.natural_gas = form.natural_gas.data
        building.fuel_oil = form.fuel_oil.data
        building.dist_heating = form.dist_heating.data
        building.dist_cooling = form.dist_cooling.data
        building.o1_energy_type = form.o1_energy_type.data
        building.o1_consumption = form.o1_consumption.data
        building.o2_energy_type = form.o2_energy_type.data
        building.o2_consumption = form.o2_consumption.data
        building.f_gas_1_type = form.f_gas_1_type.data
        building.f_gas_1_amount = form.f_gas_1_amount.data
        building.f_gas_2_type = form.f_gas_2_type.data
        building.f_gas_2_amount = form.f_gas_2_amount.data
        building.pv_wind_consumed= form.pv_wind_consumed.data
        building.pv_wind_exported= form.pv_wind_exported.data
        building.hp_solar_consumed= form.hp_solar_consumed.data
        building.hp_solar_exported= form.hp_solar_exported.data
        building.off_site_renewables= form.off_site_renewables.data
        building.retrofit_year = form.retrofit_year.data
        building.retrofit_investment = form.retrofit_investment.data
        building.user_id = current_user.id
        
        db.session.commit()
        flash(_("Building successfully updated."))
        return redirect(url_for("main.index"))
    
    elif request.method == "GET":
        building = db.session.scalar(sa.select(Building).where(Building.user_id == current_user.id))
        form.address.data = building.address
        form.zip.data = building.zip
        form.construction_year.data = building.construction_year
        form.reporting_year.data = building.reporting_year
        form.country.data = building.country
        form.property_type.data = building.property_type
        form.size.data = building.size
        form.grid_elec.data = building.grid_elec
        form.natural_gas.data = building.natural_gas
        form.fuel_oil.data = building.fuel_oil
        form.dist_heating.data = building.dist_heating
        form.dist_cooling.data = building.dist_cooling
        form.o1_energy_type.data = building.o1_energy_type
        form.o1_consumption.data = building.o1_consumption
        form.o2_energy_type.data = building.o2_energy_type
        form.o2_consumption.data = building.o2_consumption
        form.f_gas_1_type.data = building.f_gas_1_type
        form.f_gas_1_amount.data = building.f_gas_1_amount
        form.f_gas_2_type.data = building.f_gas_2_type
        form.f_gas_2_amount.data = building.f_gas_2_amount
        form.pv_wind_consumed.data = building.pv_wind_consumed
        form.pv_wind_exported.data = building.pv_wind_exported
        form.hp_solar_consumed.data = building.hp_solar_consumed
        form.hp_solar_exported.data = building.hp_solar_exported
        form.off_site_renewables.data = building.off_site_renewables
        form.retrofit_year.data = building.retrofit_year
        form.retrofit_investment.data = building.retrofit_investment
        
    form.submit.label.text = _("Save Building")
    return render_template("edit_building.html", title=_("Edit Building"), form=form)

@bp.route("/delete_building", methods=["DELETE"])
@login_required
def delete_building():
    db.session.query(Building).where(Building.user_id == current_user.id).delete()
    db.session.commit()
    flash(_("Building successfully deleted."))
    return redirect(url_for("main.index"))
    
#Admin feature

    