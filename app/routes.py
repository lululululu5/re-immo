from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
import sqlalchemy as sa
from urllib.parse import urlsplit

from .forms import LoginForm, RegistrationForm, BuildingAssessmentForm
from .models import User, Building
from app import app, db

@app.route("/")
@app.route("/index")
@login_required
def index():
    building = db.session.scalar(sa.select(Building).where(Building.user_id == current_user.id))
    return render_template("index.html", building=building)

@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(sa.select(User).where(User.email == form.email.data))
        if user is None or not user.check_password(form.password.data):
            flash("Invalid username or password")
            return redirect(url_for("login"))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get("next")
        if not next_page or urlsplit(next_page).netloc != "":
            next_page = url_for("index")
        return redirect(next_page)
    return render_template("login.html", title="Sign In", form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))

@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(name=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("Congratulation, you are now a registered user!")
        return redirect(url_for("login"))
    return render_template("register.html", title="Register", form=form)

@app.route("/building", methods=["GET", "POST"])
@login_required
def building():
    form = BuildingAssessmentForm()
    if form.validate_on_submit():
        building = Building(
            address=form.address.data,
            zip = form.zip.data,
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
        flash("Building successfully created.")
        return redirect(url_for("index"))
    return render_template("building.html", title="Building", form=form)

@app.route("/building/<id>", methods=["DELETE"])
@login_required
def delete_building():
    pass
    