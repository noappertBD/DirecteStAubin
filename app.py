from db import Users
from flask import Flask, render_template, jsonify, request, session, redirect, url_for
from edrequests import getLoginInfo, getHomework

app = Flask("AfterBank")
app.config["SECRET_KEY"] = "devsecret"


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = str(request.form['username'])
        password = str(request.form['password'])
        loginResponse = getLoginInfo(username, password)
        if loginResponse.json().get("code") == 200:
            account = loginResponse.json().get("data").get("accounts")[0]
            id = account.get("id")
            loginId = account.get("idLogin")
            firstName = account.get("prenom")
            lastName = account.get("nom")
            classLevel = account.get("profile").get("classe").get("code")
            discriminentId = str(id)+str(loginId)
            verify = Users.selectBy(discriminentId=discriminentId)
            if verify.count() == 0:
                Users(discriminentId=discriminentId, firstName=firstName,
                      lastName=lastName, classLevel=classLevel)
            session["userId"] = id
            session["token"] = loginResponse.json().get("token")
            return jsonify(loginResponse.json())
        else:
            return jsonify({"code": "401", "message": "Invalid credentials"}), 401
    else:
        return render_template('login.html')


@app.route('/profile/')
def profiles():
    users = Users.select()
    return jsonify({"code": "200", "data": [user.toDict() for user in users]})

@app.route('/profile/<discriminentId>', methods=['GET'])
def profile(discriminentId):
    verify = Users.select(Users.q.discriminentId == discriminentId)
    user = []
    if verify.count() == 0:
        return jsonify({"code": "401", "message": "Invalid credentials"}), 401
    else:
        user = {"code": "200", "data": verify[0].toDict()}
        return jsonify(user)

@app.route('/homeworks')
def homework():
    if("userId" not in session):
        return redirect(url_for("login"))
    
    else:
        homeworkResponse = getHomework(session["token"], session["userId"], None)
        session["token"] = homeworkResponse.json().get("token")
        return jsonify({"status": 200, "data": homeworkResponse.json()})
        
    



app.run(debug=True, port=5000, host='0.0.0.0', threaded=True)
