
# ██████╗ ██╗██████╗ ███████╗ ██████╗████████╗███████╗███████╗ █████╗ ██╗███╗   ██╗████████╗ █████╗ ██╗   ██╗██████╗ ██╗███╗   ██╗     █████╗ ██████╗ ██╗
# ██╔══██╗██║██╔══██╗██╔════╝██╔════╝╚══██╔══╝██╔════╝██╔════╝██╔══██╗██║████╗  ██║╚══██╔══╝██╔══██╗██║   ██║██╔══██╗██║████╗  ██║    ██╔══██╗██╔══██╗██║
# ██║  ██║██║██████╔╝█████╗  ██║        ██║   █████╗  ███████╗███████║██║██╔██╗ ██║   ██║   ███████║██║   ██║██████╔╝██║██╔██╗ ██║    ███████║██████╔╝██║
# ██║  ██║██║██╔══██╗██╔══╝  ██║        ██║   ██╔══╝  ╚════██║██╔══██║██║██║╚██╗██║   ██║   ██╔══██║██║   ██║██╔══██╗██║██║╚██╗██║    ██╔══██║██╔═══╝ ██║
# ██████╔╝██║██║  ██║███████╗╚██████╗   ██║   ███████╗███████║██║  ██║██║██║ ╚████║   ██║   ██║  ██║╚██████╔╝██████╔╝██║██║ ╚████║    ██║  ██║██║     ██║
# ╚═════╝ ╚═╝╚═╝  ╚═╝╚══════╝ ╚═════╝   ╚═╝   ╚══════╝╚══════╝╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝   ╚═╝   ╚═╝  ╚═╝ ╚═════╝ ╚═════╝ ╚═╝╚═╝  ╚═══╝    ╚═╝  ╚═╝╚═╝     ╚═╝


from app.db import Users
from flask import Flask, render_template, jsonify, request, session, redirect, url_for
from app.edrequests import getLoginInfo, getHomework, getSchedule, getGrades, getViescolaire, getMails
import requests

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
    print(f'{username}:{password}')
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
        if "cookies" in request.form != "False":
            session["accountType"] = "Student"
    else:
        classLevel = "Teacher"
        if "cookies" in request.form != "False":
            session["accountType"] = "Teacher"

    discriminentId = str(id_key)+str(loginId)
    verify = Users.selectBy(discriminentId=discriminentId)
    if verify.count() == 0:
        Users(discriminentId=discriminentId, firstName=firstName,
              lastName=lastName, classLevel=classLevel)
    if "cookies" in request.form != "False":
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
@app.route('/homeworks/', methods=['GET', 'POST'])
def homework():
    if "token" not in session and "token" not in request.form:
        return jsonify({"status": 401, "data": "Not logged in"}), 401

    if "token" in request.form:
        token = str(request.form['token'])
    else:
        token = session['token']
    if "userId" in request.form:
        user_id = str(request.form['userId'])
    elif "userId" in session:
        user_id = session['userId']
    else:
        return jsonify({"status": 401, "data": "Invalid userId"}), 401

    homeworkResponse = getHomework(token, user_id, None)
    if "cookies" in request.form != "False":
        session["token"] = homeworkResponse.json().get("token")
    return jsonify({"status": 200, "data": homeworkResponse.json()})


### EMPLOI DU TEMPS ###
@app.route('/schedule/', methods=['GET', 'POST'])
def schedule():
    if "token" not in session and "token" not in request.form:
        return jsonify({"status": 401, "data": "Not logged in"}), 401

    if "token" in request.form:
        token = str(request.form['token'])
    else:
        token = session['token']
    if "userId" in request.form:
        user_id = str(request.form['userId'])
    elif "userId" in session:
        user_id = session['userId']
    else:
        return jsonify({"status": 401, "data": "Invalid userId"}), 401
    if "accountType" in request.form:
        account_type = request.form["accountType"]
    elif "accountType" in session:
        account_type = session['accountType']
    else:
        return jsonify({"status": 401, "data": "Invalid accountType"}), 401
    
    scheduleResponse = getSchedule(token, user_id, (
        "E" if account_type == "Student" else "P"), None)
    if "cookies" in request.form != "False":
        session["token"] = scheduleResponse["token"]
    return jsonify({"status": 200, "data": {k: [value.toJSON() for value in v] for k, v in scheduleResponse["data"].items()}})

@app.route('/schedule/<date>/', methods=['GET', 'POST'])
def schedule_withdate(date):
    if "token" not in session and "token" not in request.form:
        return jsonify({"status": 401, "data": "Not logged in"}), 401

    if "token" in request.form:
        token = str(request.form['token'])
    else:
        token = session['token']
    if "userId" in request.form:
        user_id = str(request.form['userId'])
    elif "userId" in session:
        user_id = session['userId']
    else:
        return jsonify({"status": 401, "data": "Invalid userId"}), 401
    if "accountType" in request.form:
        account_type = request.form["accountType"]
    elif "accountType" in session:
        account_type = session['accountType']
    else:
        return jsonify({"status": 401, "data": "Invalid accountType"}), 401
    
    scheduleResponse = getSchedule(token, user_id, (
        "E" if account_type == "Student" else "P"), date)
    if "cookies" in request.form != "False":
        session["token"] = scheduleResponse["token"]
    return jsonify({"status": 200, "data": {k: [value.toJSON() for value in v] for k, v in scheduleResponse["data"].items()}})


### NOTES ###
@app.route("/grades/", methods=['GET', 'POST'])
def grades():
    if "token" not in session and "token" not in request.form:
        return jsonify({"status": 401, "data": "Not logged in"}), 401

    if "token" in request.form:
        token = str(request.form['token'])
    else:
        token = session['token']
    if "userId" in request.form:
        user_id = str(request.form['userId'])
    elif "userId" in session:
        user_id = session['userId']
    else:
        return jsonify({"status": 401, "data": "Invalid userId"}), 401
    if "accountType" in request.form:
        account_type = request.form["accountType"]
    elif "accountType" in session:
        account_type = session['accountType']
    else:
        return jsonify({"status": 401, "data": "Invalid accountType"}), 401
    
    response = getGrades(token, user_id,
                         ("eleves" if account_type == "Student" else "profs"))
    if "cookies" in request.form != "False":
        session["token"] = response['token']
    return jsonify(response)


### VIE SCOLAIRE ###
@app.route("/viescolaire/", methods=['GET', 'POST'])
def viescolaire():
    if "token" not in session and "token" not in request.form:
        return jsonify({"status": 401, "data": "Not logged in"}), 401

    if "token" in request.form:
        token = str(request.form['token'])
    else:
        token = session['token']
    if "userId" in request.form:
        user_id = str(request.form['userId'])
    elif "userId" in session:
        user_id = session['userId']
    else:
        return jsonify({"status": 401, "data": "Invalid userId"}), 401
    if "accountType" in request.form:
        account_type = request.form["accountType"]
    elif "accountType" in session:
        account_type = session['accountType']
    else:
        return jsonify({"status": 401, "data": "Invalid accountType"}), 401
    
    response = getViescolaire(token, user_id, (
        "eleves" if account_type == "Student" else "profs"))
    if "cookies" in request.form != "False":
        session["token"] = response['token']
    return jsonify(response)


### MAILS ###
@app.route("/mail/", methods=['GET', 'POST'])
def mail():
    if "token" not in session and "token" not in request.form:
        return jsonify({"status": 401, "data": "Not logged in"}), 401

    if "token" in request.form:
        token = str(request.form['token'])
    else:
        token = session['token']
    if "userId" in request.form:
        user_id = str(request.form['userId'])
    elif "userId" in session:
        user_id = session['userId']
    else:
        return jsonify({"status": 401, "data": "Invalid userId"}), 401
    if "accountType" in request.form:
        account_type = request.form["accountType"]
    elif "accountType" in session:
        account_type = session['accountType']
    else:
        return jsonify({"status": 401, "data": "Invalid accountType"}), 401
    
    response = getMails(token, user_id, (
        "eleves" if account_type == "Student" else "profs"), "", "")
    if "cookies" in request.form != "False":
        session["token"] = response['token']
    return(jsonify(response))

@app.route("/mail/q=<query>/", methods=['GET', 'POST'])
def mail_query(query):
    if "token" not in session and "token" not in request.form:
        return jsonify({"status": 401, "data": "Not logged in"}), 401

    if "token" in request.form:
        token = str(request.form['token'])
    else:
        token = session['token']
    if "userId" in request.form:
        user_id = str(request.form['userId'])
    elif "userId" in session:
        user_id = session['userId']
    else:
        return jsonify({"status": 401, "data": "Invalid userId"}), 401
    if "accountType" in request.form:
        account_type = request.form["accountType"]
    elif "accountType" in session:
        account_type = session['accountType']
    else:
        return jsonify({"status": 401, "data": "Invalid accountType"}), 401
    
    response = getMails(token, user_id, (
        "eleves" if account_type == "Student" else "profs"), query, "")
    if "cookies" in request.form != "False":
        session["token"] = response['token']
    return(jsonify(response))

@app.route("/mail/<classeur>/", methods=['GET', 'POST'])
def mail_classeur(classeur):
    if "token" not in session and "token" not in request.form:
        return jsonify({"status": 401, "data": "Not logged in"}), 401

    if "token" in request.form:
        token = str(request.form['token'])
    else:
        token = session['token']
    if "userId" in request.form:
        user_id = str(request.form['userId'])
    elif "userId" in session:
        user_id = session['userId']
    else:
        return jsonify({"status": 401, "data": "Invalid userId"}), 401
    if "accountType" in request.form:
        account_type = request.form["accountType"]
    elif "accountType" in session:
        account_type = session['accountType']
    else:
        return jsonify({"status": 401, "data": "Invalid accountType"}), 401
    
    response = getMails(token, user_id, (
        "eleves" if account_type == "Student" else "profs"), "", classeur)
    if "cookies" in request.form != "False":
        session["token"] = response['token']
    return(jsonify(response))

@app.route("/mail/<classeur>/q=<query>/", methods=['GET', 'POST'])
def mail_query_in_classeur(classeur, query):
    if "token" not in session and "token" not in request.form:
        return jsonify({"status": 401, "data": "Not logged in"}), 401

    if "token" in request.form:
        token = str(request.form['token'])
    else:
        token = session['token']
    if "userId" in request.form:
        user_id = str(request.form['userId'])
    elif "userId" in session:
        user_id = session['userId']
    else:
        return jsonify({"status": 401, "data": "Invalid userId"}), 401
    if "accountType" in request.form:
        account_type = request.form["accountType"]
    elif "accountType" in session:
        account_type = session['accountType']
    else:
        return jsonify({"status": 401, "data": "Invalid accountType"}), 401
    
    response = getMails(token, user_id, (
        "eleves" if account_type == "Student" else "profs"), query, classeur)
    if "cookies" in request.form != "False":
        session["token"] = response['token']
    return(jsonify(response))


@app.route("/mail/read/", methods=['GET', 'POST'])
def mail_read():
    pass


@app.route("/mail/send/", methods=['GET', 'POST'])
def mail_send():
    pass


### CLOUD ###
@app.route("/cloud/", methods=['GET', 'POST'])
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


app.run(port=8000, host="0.0.0.0", threaded=True, debug=True)
