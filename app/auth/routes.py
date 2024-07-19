from flask_login import current_user, login_user, logout_user
from flask import redirect, url_for, flash, request, render_template, jsonify
from flask_babel import lazy_gettext as _l, _
import sqlalchemy as sa
from urllib.parse import urlsplit


from app import db
from app.auth import bp
from app.auth.forms import LoginForm, RegistrationForm
from app.models import User

@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(sa.select(User).where(User.email == form.email.data))
        if user is None or not user.check_password(form.password.data):
            flash(_("Invalid username or password"))
            return redirect(url_for("auth.login"))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get("next")
        if not next_page or urlsplit(next_page).netloc != "":
            next_page = url_for("main.index")
        return redirect(next_page)
    return render_template("auth/login.html", title=_("Sign In"), form=form)

@bp.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("main.index"))

@bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(name=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(_("Congratulation, you are now a registered user!"))
        return redirect(url_for("auth.login"))
    return render_template("auth/register.html", title=_("Register"), form=form)

@bp.route("/delete_user/<user_id>", methods=["DELETE"])
def delete_user(user_id):
    if not current_user or not current_user.user_type == "admin":
        return jsonify({"error": "Unauthorized"}), 403
    
    user_to_delete = User.query.get(user_id)
    
    if user_to_delete is None:
        return jsonify({"error": "User not found"}), 404
    
    db.session.delete(user_to_delete)
    db.session.commit()
    
    return jsonify({"message": "User deleted successfully"}, 200)