import requests
import json
import urllib.parse
import datetime
import time


class Course:
    name: str = ""
    teacher: str = ""
    room: str = ""
    start: datetime.time = None
    end: datetime.time = None
    color: str = ""

    def __init__(self, name, teacher, room, start, end, color):
        self.name = name
        self.teacher = teacher
        self.room = room
        self.start = start
        self.end = end
        self.color = color

    def toJSON(self):
        return {
            "name": self.name,
            "teacher": self.teacher,
            "room": self.room,
            "start": self.start,
            "end": self.end,
            "color": self.color
        }


headers = {
    'authority': 'api.ecoledirecte.com',
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
    'content-type': 'application/x-www-form-urlencoded',
    'origin': 'https://www.ecoledirecte.com',
    'referer': 'https://www.ecoledirecte.com/',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.5249.119 Safari/537.36',
    'x-token': '',
}


def makePost(url, data, params=None, headers=headers):
    if params is None:
        params = {'v': "4.32.0"}
    params = params
    data = f'data={json.dumps(data)}'
    return requests.post(url, params=params, headers=headers, data=data)


def getLoginInfo(username, password):
    data = {"uuid": "", "identifiant": urllib.parse.quote(
        username), "motdepasse": urllib.parse.quote(password), "isReLogin": False}
    return makePost('https://api.ecoledirecte.com/v3/login.awp', data)


def getHomework(token, userId, date):
    params = {'verbe': "get", 'v': "4.32.0"}
    newHeaders = headers.copy()
    newHeaders['x-token'] = token
    if date is None:
        return makePost(
            f'https://api.ecoledirecte.com/v3/Eleves/{userId}/cahierdetexte.awp',
            {},
            params,
            newHeaders,
        )
    else:
        return makePost('https://api.ecoledirecte.com/v3/Eleves/{}/{}-{}-{}/cahierdetexte.awp'.format(userId, date(datetime.date.year)), {}, params, newHeaders)


def getSchedule(token, userId, accountType, date=None):
    params = {'verbe': "get", 'v': "4.32.0"}
    if date is None:
        start_date = datetime.date.today()
    else:
        start_date = datetime.datetime.strptime(date, "%Y-%m-%d")

    start_date = start_date - datetime.timedelta(days=start_date.weekday())
    end_date = start_date + datetime.timedelta(days=6)

    data = {
        "dateDebut": start_date.strftime("%Y-%m-%d"),
        "dateFin": end_date.strftime("%Y-%m-%d"),
        "avecTrous": False
    }

    newHeaders = headers.copy()
    newHeaders['x-token'] = token
    print(
        f'https://api.ecoledirecte.com/v3/{accountType}/{userId}/emploidutemps.awp')
    result = makePost(
        f'https://api.ecoledirecte.com/v3/{accountType}/{userId}/emploidutemps.awp', data, params, newHeaders).json()
    token = result["token"]
    result = result["data"]
    courses = {}
    for data in result:
        name = data["matiere"]
        teacher = data["prof"]
        room = data["salle"]
        start = datetime.datetime.strptime(
            data["start_date"], "%Y-%m-%d %H:%M")
        end = datetime.datetime.strptime(data["end_date"], "%Y-%m-%d %H:%M")
        color = data["color"]
        canceled = data["isAnnule"]
        edited = data["isModifie"]

        start_minutes = (start.hour*60 + start.minute) - 495
        end_minutes = (end.hour*60 + end.minute) - 495
        day = start.strftime("%Y-%m-%d")
        if day not in courses:
            courses[day] = []
        courses[day].append(
            Course(name, teacher, room, start_minutes, end_minutes, color, canceled, edited))
    return {"token": token, "data": courses}


def getGrades(token, userId, accountType):
    newHeaders = headers.copy()
    newHeaders['x-token'] = token
    response = makePost(f'https://api.ecoledirecte.com/v3/{accountType}/{userId}/notes.awp', {
                        "anneeScolaire": ""}, params={"verbe": "get", "v": "4.32.0"}, headers=newHeaders)
    data = response.json()
    token = data["token"]
    data = data["data"]
    raw_grades = data["notes"]
    raw_periods = data["periodes"]

    grades = [
        {
            "name": grade["codeMatiere"],
            "fullname": grade["libelleMatiere"],
            "grade": grade["devoir"],
            "value": grade["valeur"],
            "comment": grade["commentaire"],
            "period": grade["codePeriode"],
            "date": grade["date"],
            "added": grade["dateSaisie"],
            "weight": grade["coef"],
            "on": grade["noteSur"],
            "id": grade["id"],
            "class": {
                "average": grade["moyenneClasse"],
                "max": grade["maxClasse"],
                "min": grade["minClasse"],
            },
        }
        for grade in raw_grades
    ]
    periods = [
        {
            "id": period["codePeriode"],
            "name": period["periode"],
            "start": period["dateDebut"],
            "end": period["dateFin"],
        }
        for period in raw_periods
    ]
    return {"status": 200, "data": {"grades": grades, "periods": periods}, "token": token}


def getViescolaire(token, userId, accountType):
    newHeaders = headers.copy()
    newHeaders['x-token'] = token
    response = makePost(f'https://api.ecoledirecte.com/v3/{accountType}/{userId}/viescolaire.awp', {
                        "anneeScolaire": ""}, params={"verbe": "get", "v": "4.32.0"}, headers=newHeaders)
    data = response.json()
    token = data["token"]
    data = data["data"]
    return {"status": 200, "data": data, "token": token}

def getMails(token, userId, accountType, query, classeur):
    newHeaders = headers.copy()
    newHeaders['x-token'] = token
    params = {
        'force': 'false',
        'typeRecuperation': ("classeur" if classeur is not None else ""),
        'idClasseur': classeur,
        'orderBy': 'date',
        'order': 'desc',
        'query': query,
        'onlyRead': '',
        'page': '',
        'itemsPerPage': '',
        'getAll': '1',
        'verbe': 'get',
        'v': '4.32.0',
    }
    response = makePost(f'https://api.ecoledirecte.com/v3/{accountType}/{userId}/messages.awp', {
                        "anneeScolaire": ""}, params, headers=newHeaders)
    data = response.json()
    token = data["token"]
    data = data["data"]
    return {"status": 200, "data": data, "token": token}
    