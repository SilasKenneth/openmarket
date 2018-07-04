from flask import Flask, render_template, request, redirect, flash, jsonify, session, url_for
from collections import OrderedDict
from model import *

app = Flask(__name__)

sign_up_error = []
errors_signup = {
    "name": "Name cannot be empty"
}
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'


def logged_in(user_name):
    if 'user' not in session:
        return False
    if 'user_type' not in session:
        return False
    if session['user_type'] != user_name:
        return False
    return True


def logged():
    if 'user' in session:
        return True
    if session['user'] is not None:
        return True
    return False


def format_datetime(value):
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    return str(value.day) + "," + str(months[value.month - 1]) + " " + str(value.year)


app.jinja_env.filters['datetime'] = format_datetime
app.url_map.strict_slashes = False

def any_empty(fields):
    for field in fields:
        if fields[str(field).strip()].strip() == "":
            sign_up_error.append(field)
    return sign_up_error


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/trader/login", methods=["POST", "GET"])
@app.route("/trader/login/", methods=["POST", "GET"])
def trader_login():
    global error
    if request.method == "POST":
        username = request.form['email_username'].strip()
        password = request.form['pass'].strip()
        if username == "" or password == "":
            error = "Please fill in all the fields"
            return render_template("traders/login.html", error=error)
        user = db_session.query(Trader).filter(Trader.email == username).one_or_none()
        if user is None:
            error = "The email or password is incorrect"
            return render_template("traders/login.html", error=error)
        if not user.verify_password(password):
            error = "The email or password is incorrect"
            return render_template("traders/login.html", error=error)
        usere = OrderedDict()
        usere['id'] = user.id
        usere['user_id'] = user.id_pass
        usere['email'] = user.email
        usere['county'] = user.county
        usere['name'] = user.name
        usere['bio'] = user.bio
        session['user'] = usere
        session['user_type'] = "trader"
        return redirect(url_for("trader_home"))
    return render_template("traders/login.html")


@app.route("/trader/signup", methods=["POST", "GET"])
def trader_signup():
    counties = County.query.all()
    global error
    if request.method == "POST":
        name = request.form['name'].strip()
        email = request.form['email'].strip()
        county = request.form['county'].strip()
        idnum = request.form['idnum'].strip()
        phone = request.form['phone'].strip()
        password = request.form['password'].strip()
        if name == "" or email == "" or county == "" or idnum == "" or phone == "" or password == "":
            error = "Please fill in all the fields"
            return render_template("trader/new.html", error=error, counties=counties)
        try:
            trader = Trader(name, email, county, idnum, phone, password)
            trader.hash_password()
            db_session.add(trader)
            db_session.commit()
            usere = OrderedDict()
            usere['id'] = trader.id
            usere['user_id'] = trader.id_pass
            usere['email'] = trader.email
            usere['county'] = trader.county
            usere['name'] = trader.name
            usere['bio'] = trader.bio
            session['user'] = usere
            session['user_type'] = "trader"
            return redirect(url_for("trader_home"))
        except Exception as ex:
            db_session.rollback()
            error = "Sorry we had a problem saving your record to the database"
            return render_template("traders/new.html", error=error, counties=counties)
    return render_template("traders/new.html", counties=counties)


@app.route("/trader/changepass")
def trader_changepass():
    if 'username' not in session:
        return redirect("/trader/login")
    if request.method == "POST":
        currentpass = request.form['current_pass']
        newpass = request.form['new_pass']
    else:
        return render_template("traders/changepass.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


@app.route("/admin")
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


@app.route("/admin/new", methods=['GET', 'POST'])
def admin_new():
    if not logged_in("admin"):
        return redirect(url_for("admin_login"))
    if request.method == "POST":
        username = request.form['username'].strip()
        email = request.form['email'].strip()
        fullnames = request.form['fullnames'].strip()
        password = request.form['password'].strip()
        pass_c = request.form['confirmpass'].strip()
        if username == "" or email == '' or fullnames == '' or password == '' or pass_c == '':
            error_empty = "Please fill up all the fields"
            return render_template("admin/new.html", error=error_empty)
        else:
            user = Admin(email, fullnames, username, password)
            user.hash_password()
            if not user.verify_password(pass_c):
                error_no_match = "The two password do not match"
                return render_template("admin/new.html", error=error_no_match)
            try:
                db_session.add(user)
                db_session.commit()
            except Exception as e:
                db_session.rollback()
                error_something = "Something went wrong while adding the record. most possibly duplicates"
                return render_template("admin/new.html", error=error_something)
            return redirect("/admin")
    return render_template("admin/new.html")


@app.route("/admin/account", methods=['GET', 'POST'])
def admin_prof():
    if 'user' in session:
        if session['user'] is None:
            return redirect(url_for("admin_login"))
        else:
            if session['user_type'] == 'admin':
                return render_template('admin/profile.html')
            else:
                return redirect(url_for('admin_login'))
    else:
        return redirect(url_for('admin_login'))


@app.route("/admin/account/edit", methods=['POST', 'GET'])
def admin_edit():
    old = OrderedDict()
    if not logged_in("admin"):
        return redirect(url_for("admin_login"))
    if request.method == "POST":
        email = request.form['email'].strip()
        username = request.form['username'].strip()
        if username == "" or email == "":
            error_empty = "Please fill in all the fields"
            return render_template("admin/edit.html", error=error_empty)
        else:
            return render_template("admin/edit.html")
    user = session['user']
    return render_template("admin/edit.html", user=user)


@app.route("/admin/vet/add", methods=['POST', 'GET'])
def vet_new():
    old = OrderedDict()
    counties = db_session.query(County).all()
    if not logged_in("admin"):
        return redirect(url_for("admin_login"))
    if request.method == "POST":
        fullnames = request.form['fullnames'].strip()
        email = request.form['email'].strip()
        county = request.form['county'].strip()
        national_id = request.form['national_id'].strip()
        password = request.form['password'].strip()
        confirmpass = request.form['confirmpass'].strip()
        phone = request.form['phone'].strip()
        if fullnames == '' or email == '' or national_id == '' or county == '' or phone == '' or password == '' or confirmpass == '':
            error_empty = "All the details must be filled"
            return render_template("veterinary/new.html", error=error_empty, old=old)
        else:
            username = str(email).split("@")[0]
            user = Veterinary(fullnames, username, password, email, county, national_id, phone)
            user.hash_password()
            if not user.verify_password(confirmpass):
                error_not = "The two passwords do not match"
                return render_template("veterinary/new.html", error=error_not)
            else:
                try:
                    db_session.add(user)
                    db_session.commit()
                except Exception as e:
                    db_session.rollback()
                    error = "You may have tried to enter a value already entered"
                    return render_template("veterinary/new.html", error=error)
                return redirect("/admin/vets")
    return render_template("veterinary/new.html", counties=counties)


@app.route("/admin/vets", methods=['GET', 'POST'])
def all_vets():
    vets = db_session.query(Veterinary).join(County).all()
    return render_template("/veterinary/all.html", vets=vets)


@app.route("/admin/counties", methods=['GET', 'POST'])
def counties():
    if not logged_in("admin"):
        return redirect(url_for("admin_login"))
    counties = db_session.query(County).all()
    return render_template("admin/counties.html", counties=counties)


@app.route("/admin/counties/new", methods=['GET', 'POST'])
def new_county():
    if not logged_in("admin"):
        return redirect(url_for("admin"))
    if request.method == "POST":
        name = request.form['name']
        if name.strip() == '':
            error_empty = "The county name must be specified"
            return render_template("admin/newc.html", error=error_empty)
        else:
            cnt = County(name)
            try:
                db_session.add(cnt)
                db_session.commit()
            except Exception as ex:
                error_p = "We have trouble processing your request"
                db_session.rollback()
                return render_template("admin/newc.html", error=error_p)
            return redirect(url_for('counties'))
    return render_template("admin/newc.html")


@app.route("/admin/changepass", methods=['GET', 'POST'])
def admin_change_pass():
    if not logged_in("admin"):
        return redirect(url_for("admin_login"))
    if request.method == "POST":
        currpass = request.form['curr_pass'].strip()
        newpass = request.form['newpass'].strip()
        passconf = request.form['confirm_pass'].strip()
        if passconf == "" or newpass == "" or currpass == "":
            error_e = "The fields cannot be empty"
            return render_template("admin/changepass.html", error=error_e)
        user = db_session.query(Admin).filter(Admin.id == session['user']['id']).first()
        if passconf != newpass:
            error_nm = "The new password and confirmation do not match"
            return render_template("admin/changepass.html", error=error_nm)
        if not user.verify_password(newpass):
            error_i = "The current password looks incorrect"
            return render_template("admin/changepass.html", error=error_i)

    return render_template("admin/changepass.html")


@app.route("/admin/login/", methods=['POST', 'GET'])
@app.route("/admin/login/", methods=['POST', 'GET'])
def admin_login():
    old = OrderedDict()
    username = ""
    password = ""
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        if password.strip() != "" and username.strip() != "":
            old['password'] = password.strip()
            old['username'] = username.strip()
            creds = db_session.query(Admin).filter(
                (Admin.username == username) | (Admin.email == username)).one_or_none()
            if creds is None:
                error_wrong = "Wrong username or password"
                return render_template("admin/login.html", error=error_wrong, old=old)
            else:
                verified = creds.verify_password(password)
                user = OrderedDict()
                user['display_name'] = creds.username
                user['username'] = username
                user['email'] = creds.email
                user['id'] = creds.id
                user['fullnames'] = creds.fullnames
                # print(user)
                session['user_type'] = 'admin'
                session['user'] = user
                if verified:
                    return redirect(url_for("admin_index"))
                error_wrong = "Wrong username or password"
                return render_template("admin/login.html", old=old, error=error_wrong)
        else:
            error_empty = "Please specify a username and a password!"
            return render_template("admin/login.html", error=error_empty, old=old)
    return render_template("admin/login.html", old=old)


@app.route("/trader")
@app.route("/trader/")
def trader_home():
    return render_template("traders/index.html")


@app.route("/traders/<int:ids>")
@app.route("/traders/<int:ids>/")
def view_trader(ids):
    trader = db_session.query(Trader).filter(Trader.id == ids).one_or_none()
    if trader is None:
        return render_template("traders/404.html")
    county = db_session.query(County).filter(County.id == trader.county).one_or_none()
    return render_template("traders/profile.html", trader=trader, county=county)


# Livestock route
@app.route("/livestocks/<int:ids>")
@app.route("/livestocks/<int:ids>/")
def view_livestock(ids):
    live = db_session.query(Livestock).filter(Livestock.id == ids).one_or_none()
    if live is None:
        return render_template("livestocks/404.html", animal=ids)
    return render_template("livestocks/profile.html", livestock=live)


@app.route("/livestocks/<int:ids>/edit")
@app.route("/livestocks/<int:ids>/edit/")
def edit_livestock(ids):
    live = db_session.query(Livestock).filter(Livestock.id == ids).one_or_none()
    if live is None:
        return render_template("livestocks/404.html")
    trader = live.traders
    return render_template("livestocks/edit.html", live=live, trader=trader)


@app.route("/livestocks/<int:ids>/delete", methods=["POST", "GET"])
@app.route("/livestocks/<int:ids>/delete/", methods=["POST", "GET"])
def delete_livestock(ids):
    return render_template("livestocks/delete.html")


@app.route("/livestocks/<int:ids>/photoupload", methods=["GET", "POST"])
@app.route("/livestocks/<int:ids>/photoupload/", methods=["GET", "POST"])
def livestock_photoupload(ids):
    return render_template("livestocks/photoupload.html")


@app.route("/livestocks")
@app.route("/livestocks/")
def livestock_index():
    livestocks = db_session.query(Livestock).all()
    return render_template("livestocks/index.html", livestocks=livestocks)


# Medications route

@app.route("/livestocks/<int:ids>/medications", methods=["GET", "POST"])
@app.route("/livestocks/<int:ids>/medications/", methods=["GET", "POST"])
def medications(ids):
    animal = db_session.query(Livestock).filter(Livestock.id == ids).one_or_none()
    if animal is None:
        return render_template("livestocks/404.html")
    medication = animal.medications
    diseases = animal.diagnosis
    return render_template("medications/index.html", animal=animal, medications=medication, diseases=diseases)


@app.route("/livestocks/<int:ids>/medications/new")
@app.route("/livestocks/<int:ids>/medications/new/")
def create_medication(ids):
    return render_template("medications/new.html")


@app.route("/livestocks/<int:ids>/medications/<int:ids1>")
@app.route("/livestocks/<int:ids>/medications/<int:ids1>/")
def view_medication(ids, ids1):
    return render_template("medications/view.html")


if __name__ == "__main__":
    app.run(host="localhost", port=3000, debug=True)
