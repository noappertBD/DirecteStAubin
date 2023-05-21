
# ██████╗ ██╗██████╗ ███████╗ ██████╗████████╗███████╗███████╗ █████╗ ██╗███╗   ██╗████████╗ █████╗ ██╗   ██╗██████╗ ██╗███╗   ██╗     █████╗ ██████╗ ██╗
# ██╔══██╗██║██╔══██╗██╔════╝██╔════╝╚══██╔══╝██╔════╝██╔════╝██╔══██╗██║████╗  ██║╚══██╔══╝██╔══██╗██║   ██║██╔══██╗██║████╗  ██║    ██╔══██╗██╔══██╗██║
# ██║  ██║██║██████╔╝█████╗  ██║        ██║   █████╗  ███████╗███████║██║██╔██╗ ██║   ██║   ███████║██║   ██║██████╔╝██║██╔██╗ ██║    ███████║██████╔╝██║
# ██║  ██║██║██╔══██╗██╔══╝  ██║        ██║   ██╔══╝  ╚════██║██╔══██║██║██║╚██╗██║   ██║   ██╔══██║██║   ██║██╔══██╗██║██║╚██╗██║    ██╔══██║██╔═══╝ ██║
# ██████╔╝██║██║  ██║███████╗╚██████╗   ██║   ███████╗███████║██║  ██║██║██║ ╚████║   ██║   ██║  ██║╚██████╔╝██████╔╝██║██║ ╚████║    ██║  ██║██║     ██║
# ╚═════╝ ╚═╝╚═╝  ╚═╝╚══════╝ ╚═════╝   ╚═╝   ╚══════╝╚══════╝╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝   ╚═╝   ╚═╝  ╚═╝ ╚═════╝ ╚═════╝ ╚═╝╚═╝  ╚═══╝    ╚═╝  ╚═╝╚═╝     ╚═╝


from app.db import Users
from flask import Flask, render_template, jsonify, request, session, redirect, url_for
from app.edrequests import getLoginInfo, getHomework, getSchedule, getGrades, getViescolaire

app = Flask("DirecteSaintAubin")
app.config["SECRET_KEY"] = "devsecret"

app.config.update(
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_SAMESITE='None'
)


### LOGIN ###
@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method != 'POST':
        return render_template('login.html')
    username = str(request.form['username'])
    password = str(request.form['password'])
    loginResponse = getLoginInfo(username, password)
    if loginResponse.json().get("code") != 200:
        return jsonify({"code": "401", "message": "Invalid credentials"}), 401
    account = loginResponse.json().get("data").get("accounts")[0]
    id_key = account.get("id")
    loginId = account.get("idLogin")
    firstName = account.get("prenom")
    lastName = account.get("nom")
    if ("classe" in account.get("profile")):
        classLevel = account.get("profile").get("classe").get("code")
        session["accountType"] = "Student"
    else:
        classLevel = "Teacher"
        session["accountType"] = "Teacher"

    discriminentId = str(id_key)+str(loginId)
    verify = Users.selectBy(discriminentId=discriminentId)
    if verify.count() == 0:
        Users(discriminentId=discriminentId, firstName=firstName,
              lastName=lastName, classLevel=classLevel)
    session["userId"] = id_key
    session["token"] = loginResponse.json().get("token")
    return jsonify(loginResponse.json())


### PROFILE ###
@app.route('/profile/')
def profiles():
    users = Users.select()
    return jsonify({"code": "200", "data": [user.toDict() for user in users]})


@app.route('/profile/<discriminentId>/', methods=['GET'])
def profile(discriminentId):
    verify = Users.select(Users.q.discriminentId == discriminentId)
    user = []
    if verify.count() == 0:
        return jsonify({"code": "401", "message": "Invalid credentials"}), 401
    user = {"code": "200", "data": [verify[0].toDict()]}
    return jsonify(user)


### DEVOIRS ###
@app.route('/homeworks/')
def homework():
    if "userId" not in session:
        return jsonify({"status": 401, "data": "Not logged in"}), 401
    homeworkResponse = getHomework(session["token"], session["userId"], None)
    session["token"] = homeworkResponse.json().get("token")
    return jsonify({"status": 200, "data": homeworkResponse.json()})


### EMPLOI DU TEMPS ###
@app.route('/schedule/')
def schedule():
    if "userId" not in session:
        return jsonify({"status": 401, "data": "Not logged in"}), 401
    scheduleResponse = getSchedule(session["token"], session["userId"], (
        "E" if session["accountType"] == "Student" else "P"), None)
    session["token"] = scheduleResponse["token"]
    return jsonify({"status": 200, "data": {k: [value.toJSON() for value in v] for k, v in scheduleResponse["data"].items()}})


@app.route('/schedule/<date>/')
def schedule_withdate(date):
    if "userId" not in session:
        return jsonify({"status": 401, "data": "Not logged in"}), 401
    scheduleResponse = getSchedule(session["token"], session["userId"], (
        "E" if session["accountType"] == "Student" else "P"), date)
    session["token"] = scheduleResponse["token"]
    return jsonify({"status": 200, "data": {k: [value.toJSON() for value in v] for k, v in scheduleResponse["data"].items()}})


### NOTES ###
@app.route("/grades/")
def grades():
    if ("userId" not in session):
        return jsonify({"status": 401, "data": "Not logged in"}), 401
    response = getGrades(session["token"], session["userId"],
                         ("eleves" if session["accountType"] == "Student" else "profs"))
    return jsonify(response)


### VIE SCOLAIRE ###
@app.route("/viescolaire/")
def viescolaire():
    if ("userId" not in session):
        return jsonify({"status": 401, "data": "Not logged in"}), 401
    response = getViescolaire(session["token"], session["userId"], (
        "eleves" if session["accountType"] == "Student" else "profs"))
    return jsonify(response)


### MAILS ###
@app.route("/mail/")
def mail():
    pass


@app.route("/mail/read/")
def mail_read():
    pass


@app.route("/mail/send/")
def mail_send():
    pass


### CLOUD ###
@app.route("/cloud/")
def cloud():
    pass


### ESPACES DE TRAVAIL ###
@app.route("/workspaces/")
def workspaces():
    pass

### RESTE ###
@app.after_request
def add_header(response):
    response.headers["Access-Control-Allow-Origin"] = request.headers.get(
        "Origin")
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, TOKEN, token"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    return response


app.run(port=8000, host="0.0.0.0", threaded=True)
