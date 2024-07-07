from flask import render_template, flash, redirect, url_for
from .forms import LoginForm
from app import app

@app.route("/")
@app.route("/index")
def index():
    user = {"username": "Miguel"}
    buildings = [
        {
            "address": "123",
            "reporting_year": 2024,
            "country": "Germany",
            "zip": "12023",
            "property_type" : "RSF",
            "size": 100
            
        }
    ]
    return render_template("index.html", user=user, buildings=buildings)

@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash(f"Login requested for user {form.username.data}, remember_me = {form.remember_me.data}")
        return redirect(url_for("index"))
    return render_template("login.html", title="Sign In", form=form)