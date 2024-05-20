from app.db import Users
from flask import Flask, render_template, jsonify, request, session, redirect, url_for
from app.edrequests import (
    getLoginInfo,
    getHomework,
    getSchedule,
    getGrades,
    getViescolaire,
    getMails,
    getMail,
    sendMail,
    getWorkspaces,
)
import base64
import json

app = Flask("DSA")
app.config["SECRET_KEY"] = "devsecret"

app.config.update(SESSION_COOKIE_SECURE=True, SESSION_COOKIE_SAMESITE="None")


@app.route("/", methods=["GET", "POST"])
def index():
    return redirect("login")


@app.route("/github/", methods=["GET", "POST"])
def github():
    return redirect("https://github.com/aleod72/DirecteStAubin")


### LOGIN ###
@app.route("/login/", methods=["GET", "POST"])
def login():
    if request.method != "POST":
        return render_template("login.html")
    username = str(request.form["username"])
    password = str(request.form["password"])
    loginResponse = getLoginInfo(username, password)
    if loginResponse.get("code") != 200:
        # return jsonify({"code": "401", "message": "Invalid credentials"}), 401
        return jsonify(loginResponse)
    account = loginResponse.get("data").get("accounts")[0]
    id_key = account.get("id")
    loginId = account.get("idLogin")
    firstName = account.get("prenom")
    lastName = account.get("nom")
    if account["typeCompte"] == "E":
        if "class" in account.get("profile"):
            classLevel = account.get("profile").get("classe").get("code")
        else:
            classLevel = "unknown"
        session["accountType"] = "Student"
    else:
        classLevel = "Teacher"
        session["accountType"] = "Teacher"

    discriminentId = str(id_key) + str(loginId)
    verify = Users.selectBy(discriminentId=discriminentId)
    if verify.count() == 0:
        Users(
            discriminentId=discriminentId,
            firstName=firstName,
            lastName=lastName,
            classLevel=classLevel,
        )
    session["userId"] = id_key
    session["token"] = loginResponse.get("token")
    return jsonify(loginResponse)


### PROFILE ###
@app.route("/profile/")
def profiles():
    users = Users.select()
    return jsonify({"code": "200", "data": [user.toDict() for user in users]})


@app.route("/profile/<discriminentId>/", methods=["GET"])
def profile(discriminentId):
    verify = Users.select(Users.q.discriminentId == discriminentId)
    user = []
    if verify.count() == 0:
        return jsonify({"code": "401", "message": "Invalid credentials"}), 401
    user = {"code": "200", "data": [verify[0].toDict()]}
    return jsonify(user)


### DEVOIRS ###
@app.route("/homeworks/", methods=["GET", "POST"])
def homework():
    if "token" not in session and "token" not in request.form:
        return jsonify({"status": 401, "data": "Not logged in"}), 401

    token = session["token"] if "token" in session else str(request.form["token"])
    if "userId" in session:
        user_id = session["userId"]
    elif "userId" in request.form:
        user_id = str(request.form["userId"])
    else:
        return jsonify({"status": 401, "data": "Invalid userId"}), 401

    homeworkResponse = getHomework(token, user_id, None)
    session["token"] = homeworkResponse.get("token")
    return jsonify({"status": 200, "data": homeworkResponse})


### EMPLOI DU TEMPS ###
@app.route("/schedule/", methods=["GET", "POST"])
def schedule():
    if "token" not in session and "token" not in request.form:
        return jsonify({"status": 401, "data": "Not logged in"}), 401

    token = session["token"] if "token" in session else str(request.form["token"])
    if "userId" in session:
        user_id = session["userId"]
    elif "userId" in request.form:
        user_id = str(request.form["userId"])
    else:
        return jsonify({"status": 401, "data": "Invalid userId"}), 401

    if "accountType" in session:
        account_type = str(session["accountType"])
    elif "accountType" in request.form:
        account_type = str(request.form["accountType"])
    else:
        return jsonify({"status": 401, "data": "Invalid accountType"}), 401

    scheduleResponse = getSchedule(
        token, user_id, ("E" if account_type == "Student" else "P"), None
    )
    session["token"] = scheduleResponse["token"]
    return jsonify(
        {
            "status": 200,
            "data": {
                k: [value.toJSON() for value in v]
                for k, v in scheduleResponse["data"].items()
            },
        }
    )


@app.route("/schedule/<date>/", methods=["GET", "POST"])
def schedule_withdate(date):
    if "token" not in session and "token" not in request.form:
        return jsonify({"status": 401, "data": "Not logged in"}), 401

    token = session["token"] if "token" in session else str(request.form["token"])
    if "userId" in session:
        user_id = session["userId"]
    elif "userId" in request.form:
        user_id = str(request.form["userId"])
    else:
        return jsonify({"status": 401, "data": "Invalid userId"}), 401

    if "accountType" in session:
        account_type = session["accountType"]
    elif "accountType" in request.form:
        account_type = str(request.form["accountType"])
    else:
        return jsonify({"status": 401, "data": "Invalid accountType"}), 401

    scheduleResponse = getSchedule(
        token, user_id, ("E" if account_type == "Student" else "P"), date
    )
    session["token"] = scheduleResponse["token"]
    return jsonify(
        {
            "status": 200,
            "data": {
                k: [value.toJSON() for value in v]
                for k, v in scheduleResponse["data"].items()
            },
        }
    )


### NOTES ###
@app.route("/grades/", methods=["GET", "POST"])
def grades():
    if "token" not in session and "token" not in request.form:
        return jsonify({"status": 401, "data": "Not logged in"}), 401

    token = session["token"] if "token" in session else str(request.form["token"])
    if "userId" in session:
        user_id = session["userId"]
    elif "userId" in request.form:
        user_id = str(request.form["userId"])
    else:
        return jsonify({"status": 401, "data": "Invalid userId"}), 401

    if "accountType" in session:
        account_type = session["accountType"]
    elif "accountType" in request.form:
        account_type = str(request.form["accountType"])
    else:
        return jsonify({"status": 401, "data": "Invalid accountType"}), 401

    response = getGrades(
        token, user_id, ("eleves" if account_type == "Student" else "profs")
    )
    session["token"] = response["token"]
    return jsonify(response)


### VIE SCOLAIRE ###
@app.route("/viescolaire/", methods=["GET", "POST"])
def viescolaire():
    if "token" not in session and "token" not in request.form:
        return jsonify({"status": 401, "data": "Not logged in"}), 401

    token = session["token"] if "token" in session else str(request.form["token"])
    if "userId" in session:
        user_id = session["userId"]
    elif "userId" in request.form:
        user_id = str(request.form["userId"])
    else:
        return jsonify({"status": 401, "data": "Invalid userId"}), 401

    if "accountType" in session:
        account_type = session["accountType"]
    elif "accountType" in request.form:
        account_type = str(request.form["accountType"])
    else:
        return jsonify({"status": 401, "data": "Invalid accountType"}), 401

    response = getViescolaire(
        token, user_id, ("eleves" if account_type == "Student" else "profs")
    )
    session["token"] = response["token"]
    return jsonify(response)


### MAILS ###
@app.route("/mail/", methods=["GET", "POST"])
def mail():
    if "token" not in session and "token" not in request.form:
        return jsonify({"status": 401, "data": "Not logged in"}), 401

    token = session["token"] if "token" in session else str(request.form["token"])
    if "userId" in session:
        user_id = session["userId"]
    elif "userId" in request.form:
        user_id = str(request.form["userId"])
    else:
        return jsonify({"status": 401, "data": "Invalid userId"}), 401

    if "accountType" in session:
        account_type = session["accountType"]
    elif "accountType" in request.form:
        account_type = str(request.form["accountType"])
    else:
        return jsonify({"status": 401, "data": "Invalid accountType"}), 401

    response = getMails(
        token, user_id, ("eleves" if account_type == "Student" else "profs"), "", ""
    )
    session["token"] = response["token"]
    return jsonify(response)


@app.route("/mail/q=<query>/", methods=["GET", "POST"])
def mail_query(query):
    if "token" not in session and "token" not in request.form:
        return jsonify({"status": 401, "data": "Not logged in"}), 401

    token = session["token"] if "token" in session else str(request.form["token"])
    if "userId" in session:
        user_id = session["userId"]
    elif "userId" in request.form:
        user_id = str(request.form["userId"])
    else:
        return jsonify({"status": 401, "data": "Invalid userId"}), 401

    if "accountType" in session:
        account_type = session["accountType"]
    elif "accountType" in request.form:
        account_type = str(request.form["accountType"])
    else:
        return jsonify({"status": 401, "data": "Invalid accountType"}), 401

    response = getMails(
        token, user_id, ("eleves" if account_type == "Student" else "profs"), query, ""
    )
    session["token"] = response["token"]
    return jsonify(response)


@app.route("/mail/<classeur>/", methods=["GET", "POST"])
def mail_classeur(classeur):
    if "token" not in session and "token" not in request.form:
        return jsonify({"status": 401, "data": "Not logged in"}), 401

    token = session["token"] if "token" in session else str(request.form["token"])
    if "userId" in session:
        user_id = session["userId"]
    elif "userId" in request.form:
        user_id = str(request.form["userId"])
    else:
        return jsonify({"status": 401, "data": "Invalid userId"}), 401

    if "accountType" in session:
        account_type = session["accountType"]
    elif "accountType" in request.form:
        account_type = str(request.form["accountType"])
    else:
        return jsonify({"status": 401, "data": "Invalid accountType"}), 401

    response = getMails(
        token,
        user_id,
        ("eleves" if account_type == "Student" else "profs"),
        "",
        classeur,
    )
    session["token"] = response["token"]
    return jsonify(response)


@app.route("/mail/<classeur>/q=<query>/", methods=["GET", "POST"])
def mail_query_in_classeur(classeur, query):
    if "token" not in session and "token" not in request.form:
        return jsonify({"status": 401, "data": "Not logged in"}), 401

    token = session["token"] if "token" in session else str(request.form["token"])
    if "userId" in session:
        user_id = session["userId"]
    elif "userId" in request.form:
        user_id = str(request.form["userId"])
    else:
        return jsonify({"status": 401, "data": "Invalid userId"}), 401

    if "accountType" in session:
        account_type = session["accountType"]
    elif "accountType" in request.form:
        account_type = str(request.form["accountType"])
    else:
        return jsonify({"status": 401, "data": "Invalid accountType"}), 401

    response = getMails(
        token,
        user_id,
        ("eleves" if account_type == "Student" else "profs"),
        query,
        classeur,
    )
    session["token"] = response["token"]
    return jsonify(response)


@app.route("/mail/read/<id>/", methods=["GET", "POST"])
def mail_read(id):
    if "token" not in session and "token" not in request.form:
        return jsonify({"status": 401, "data": "Not logged in"}), 401

    token = session["token"] if "token" in session else str(request.form["token"])
    if "userId" in session:
        user_id = session["userId"]
    elif "userId" in request.form:
        user_id = str(request.form["userId"])
    else:
        return jsonify({"status": 401, "data": "Invalid userId"}), 401

    if "accountType" in session:
        account_type = session["accountType"]
    elif "accountType" in request.form:
        account_type = str(request.form["accountType"])
    else:
        return jsonify({"status": 401, "data": "Invalid accountType"}), 401

    response = getMail(
        token, user_id, ("eleves" if account_type == "Student" else "profs"), id
    )
    session["token"] = response["token"]
    return jsonify(response)


@app.route("/mail/read/<id>/page/", methods=["GET", "POST"])
def mail_readinpage(id):
    if "token" not in session and "token" not in request.form:
        return jsonify({"status": 401, "data": "Not logged in"}), 401

    token = session["token"] if "token" in session else str(request.form["token"])
    if "userId" in session:
        user_id = session["userId"]
    elif "userId" in request.form:
        user_id = str(request.form["userId"])
    else:
        return jsonify({"status": 401, "data": "Invalid userId"}), 401

    if "accountType" in session:
        account_type = session["accountType"]
    elif "accountType" in request.form:
        account_type = str(request.form["accountType"])
    else:
        return jsonify({"status": 401, "data": "Invalid accountType"}), 401

    response = getMail(
        token, user_id, ("eleves" if account_type == "Student" else "profs"), id
    )
    session["token"] = response["token"]
    return (
        (base64.b64decode(response["data"]["content"].encode("utf-8")).decode("utf-8"))
        .encode("ascii", "xmlcharrefreplace")
        .decode("ascii")
    )+"<style>@import url('https://fonts.googleapis.com/css2?family=Reddit+Sans:ital,wght@0,200..900;1,200..900&display=swap');*{font-family: 'Reddit Sans', sans-serif;}</style>"


@app.route("/mail/send/", methods=["GET", "POST"])
def mail_send():
    if request.method != "POST":
        return render_template("mailsend.html")
    if "token" not in session and "token" not in request.form:
        return jsonify({"status": 401, "data": "Not logged in"}), 401

    token = (
        session["token"]
        if "token" in session
        else request.form["token"]
    )
    if "userId" in session:
        user_id = session["userId"]
    elif "userId" in request.form:
        user_id = request.form["userId"]
    else:
        return jsonify({"status": 401, "data": "Invalid userId"}), 401

    if "accountType" in session:
        account_type = session["accountType"]
    elif "accountType" in request.form:
        account_type = request.form["accountType"]
    else:
        return jsonify({"status": 401, "data": "Invalid accountType"}), 401

    subject = request.form["subject"] if "subject" in request.form else None
    content = request.form["content"] if "content" in request.form else None
    to = '{"type": "E", "id": %s, "isPP": false, "isSelected": true, "to_cc_cci": "to"}' % request.form["to"] if "to" in request.form else None
    to = [to]
    print(to)
    response = sendMail(
        token,
        user_id,
        ("eleves" if account_type == "Student" else "profs"),
        subject,
        content,
        to,
    )

    session["token"] = response["token"]
    return jsonify(response)


@app.route("/mail/dest/", methods=["GET", "POST"])
def mail_dest():
    pass


### CLOUD ###
@app.route("/cloud/", methods=["GET", "POST"])
def cloud():
    pass


### ESPACES DE TRAVAIL ###
@app.route("/workspaces/")
def workspaces():
    if "token" not in session and "token" not in request.form:
        return jsonify({"status": 401, "data": "Not logged in"}), 401

    token = session["token"] if "token" in session else str(request.form["token"])
    if "userId" in session:
        user_id = session["userId"]
    elif "userId" in request.form:
        user_id = str(request.form["userId"])
    else:
        return jsonify({"status": 401, "data": "Invalid userId"}), 401

    if "accountType" in session:
        account_type = session["accountType"]
    elif "accountType" in request.form:
        account_type = str(request.form["accountType"])
    else:
        return jsonify({"status": 401, "data": "Invalid accountType"}), 401

    response = getWorkspaces(
        token, user_id, ("E" if account_type == "Student" else "P")
    )
    session["token"] = response["token"]
    return jsonify(response)


### RESTE ###


@app.after_request
def add_header(response):
    response.headers["Access-Control-Allow-Origin"] = request.headers.get("Origin")
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers[
        "Access-Control-Allow-Headers"
    ] = "Content-Type, Authorization, TOKEN, token"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    return response


app.run(port=8000, host="0.0.0.0", threaded=True, debug=False)
