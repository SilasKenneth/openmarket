from flask import Flask, render_template, request, redirect, flash, jsonify, session, url_for
from collections import OrderedDict

# from language_support_pkgs import packagekit_what_provides_locale
from passlib.apps import custom_app_context as pwd_context
from model import *
import random
app = Flask(__name__)

sign_up_error = []
errors_signup = {
    "name": "Name cannot be empty"
}
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
def any_empty(fields):
    sign_up_error = []
    for field in fields:
        if fields[str(field).strip()].strip() == "":
            sign_up_error.append(field)
    return sign_up_error
@app.route("/")
def index():
    # alp = [chr(c) for c in range(65, 91)]
    # for i in range(10000):
    #     name = "".join([random.choice(alp) for x in range(40)])
    #     email = "".join([random.choice(alp) for x in range(10)])
    #     email += "@"
    #     email += "".join([random.choice(alp) for x in range(10)])
    #     email += "."
    #     email += "".join([random.choice(alp) for x in range(3)])
    #     user = User(name=name.lower(), email=email.lower())
    #     db_session.add(user)
    # db_session.commit()
    users = None
    return render_template("index.html", users=users)
@app.route("/trader/login", methods=["POST","GET"])
def trader_login():
    old = OrderedDict()
    old['username'] = ""
    old['password'] = ""
    print(pwd_context.encrypt("silas"))
    if request.method == "POST":
        old['username'] = request.form['email_username']
        old['password'] = request.form['pass']
        password = request.form['pass']
        user = Trader.query.filter(Trader.email == request.form['email_username'])
        print(user)
        return render_template("traders/login.html", old=old)
    else:
        return render_template("traders/login.html", old=old)
@app.route("/trader/signup", methods=["POST","GET"])
def trader_signup():
    counties = County.query.all()
    old = OrderedDict()
    sample = [('idnum', '32281737'), ('county', "Migori"),('phone', '0791350402'), ('name', 'Silas Kenneth'), ('email', 'silaskenneth1@gmail.com')]
    for k in range(len(sample)):
        sample[k] = list(sample[k])
        old[sample[k][0]] = ""
    if request.method == "POST":
        for kk in range(len(sample)):
            old[sample[kk][0]] = request.form[sample[kk][0]]
        try:
            trader = Trader(request.form['name'],request.form['email'],request.form['county'],request.form['idnum'],request.form['phone']
                            ,request.form['password'])

            db_session.add(trader)
            db_session.commit()
            session['user'] = trader.id
            return redirect(url_for("trader_login"))
        except Exception as ex:
            print(ex)
            db_session.rollback()
        return render_template("traders/new.html", errors = [] if len(any_empty(request.form)) == 0 else any_empty(request.form), old = old, counties=counties)
    else:
        return render_template("traders/new.html", old = old, counties=counties)
@app.route("/trader/changepass")
def trader_changepass():
    if 'username' not in session:
        return redirect("/trader/login")
    if request.method == "POST":
        pass
    else:
        return render_template("traders/changepass.html")




@app.route("/admin")
@app.route("/admin/")
def admin_index():
    if 'user' in session:
        if 'user_type' in session:
            if session['user_type'] != 'admin':
                return redirect(url_for("admin_login"))
            else:
                return render_template("admin/home.html", user=session['user'])
        else:
            return redirect(url_for("admin_login"))
    else:
        return redirect(url_for('admin_login'))
@app.route("/admin/login/", methods=['POST', 'GET'])
@app.route("/admin/login/", methods=['POST', 'GET'])
def admin_login():
    old = OrderedDict()
    old['username'] = ""
    old['password'] = ""
    username = ""
    password = ""
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        if password.strip() != "" and username.strip() != "":
            old['password'] = password
            old['username'] = username
            creds = db_session.query(Admin).filter(Admin.username == username).one_or_none()
            print(creds)
            if creds == None:
                error_wrong = "Wrong username or password"
                return render_template("admin/login.html", error=error_wrong)
            else:
                return render_template("admin/login.html")
        else:
            error_empty = "Please specify a username and a password!"
            return render_template("admin/login.html", error=error_empty)
    return render_template("admin/login.html", old=old)


@app.route("/trader")
def trader_home():
    return render_template("traders/index.html")
@app.route("/traders/<int:ids>")
def view_trader(ids):
    trader = db_session.query(Trader).filter(Trader.id == ids).one_or_none()
    if trader == None:
        return render_template("traders/404.html")
    county = db_session.query(County).filter(County.id == trader.county).one_or_none()
    return render_template("traders/profile.html", trader = trader, county=county)
#Livestock route
@app.route("/livestocks/<int:ids>")
def view_livestock(ids):
    live = db_session.query(Livestock).filter(Livestock.id == ids).one_or_none()
    if live == None:
        return render_template("livestocks/404.html", animal = ids)
    return render_template("livestocks/profile.html", livestock = live)
@app.route("/livestocks/<int:ids>/edit")
def edit_livestock(ids):
    live = db_session.query(Livestock).filter(Livestock.id == ids).one_or_none()
    if live == None:
        return render_template("livestocks/404.html")
    trader = live.traders
    return render_template("livestocks/edit.html", live = live, trader = trader)
@app.route("/livestocks/<int:ids>/delete", methods = ["POST", "GET"])
def delete_livestock(ids):
    return render_template("livestocks/delete.html")
@app.route("/livestocks/<int:ids>/photoupload", methods=["GET", "POST"])
def livestock_photoupload(ids):
    return render_template("livestocks/photoupload.html")
@app.route("/livestocks")
def livestock_index():
    livestocks = db_session.query(Livestock).all()
    return render_template("livestocks/index.html", livestocks=livestocks)

# Medications route

@app.route("/livestocks/<int:ids>/medications", methods = ["GET", "POST"])
def medications(ids):
    animal = db_session.query(Livestock).filter(Livestock.id == ids).one_or_none()
    if animal == None:
        return render_template("livestocks/404.html")
    medications = animal.medications
    diseases = animal.diagnosis
    return render_template("medications/index.html", animal = animal, medications=medications, diseases = diseases)
@app.route("/livestocks/<int:ids>/medications/new")
def create_medication(ids):
    return render_template("medications/new.html")
@app.route("/livestocks/<int:ids>/medications/<int:ids1>")
def view_medication(ids, ids1):
    return render_template("medications/view.html")


if __name__ == "__main__":
    app.run(host="localhost",port=3000,debug=True)
