from flask import render_template, current_app
from flask_babel import _

from app.email import send_email


def send_password_reset_email(user):
    token = user.get_reset_password_token()
    send_email(_("re:immo Reset your Password"),
               sender=current_app.config["ADMIN"],
               recipients=[user.email],
               text_body=render_template("email/reset_password.txt", 
                                         user=user, token=token),
               html_body=render_template("email/reset_password.html", 
                                         user=user, token=token))
    
def send_email_confirmation(user):
    token = user.get_confirm_email_token()
    send_email(_("re:immo PLease confirm your Email"),
               sender=current_app.config["ADMIN"],
               recipients=[user.email],
               text_body=render_template("email/confirm_email.txt",
                                         user=user, token=token),
               html_body= render_template("email/confirm_email.html",
                                         user=user, token=token)
               )