import requests, json
import urllib.parse
import datetime, time


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


def makePost(url, data, params={'v': '4.27.4'}, headers=headers):
    params = params
    data = 'data=' + json.dumps(data)
    return requests.post(url, params=params, headers=headers, data=data)


def getLoginInfo(username, password):
    data = {"uuid": "", "identifiant": urllib.parse.quote(username), "motdepasse": urllib.parse.quote(password), "isReLogin": False}
    return makePost('https://api.ecoledirecte.com/v3/login.awp', data)

def getHomework(token, userId, date):
    params = {'verbe': "get", 'v': '4.27.4'}
    newHeaders = headers.copy()
    newHeaders['x-token'] = token
    if(date == None):
        return makePost('https://api.ecoledirecte.com/v3/Eleves/{}/cahierdetexte.awp'.format(userId), {}, params, newHeaders)
    else:
        return makePost('https://api.ecoledirecte.com/v3/Eleves/{}/{}-{}-{}/cahierdetexte.awp'.format(userId, date(datetime.date.year)), {}, params, newHeaders)

def getSchedule(token, userId, date):
    params = {'verbe': "get", 'v': '4.27.4'}
    start_date = date
    end_date = date
    if(date == None):
        start_date = datetime.date.today() - datetime.timedelta(days=datetime.date.today().weekday())
        end_date = start_date + datetime.timedelta(days=6)

    data = {
        "dateDebut": start_date.strftime("%Y-%m-%d"),
        "dateFin": end_date.strftime("%Y-%m-%d"),
        "avecTrous": False
    }

    newHeaders = headers.copy()
    newHeaders['x-token'] = token
    result = makePost('https://api.ecoledirecte.com/v3/E/{}/emploidutemps.awp'.format(userId), data, params, newHeaders).json()
    token = result["token"]
    result = result["data"]
    courses = {}
    for data in result:
        name = data["matiere"]
        teacher = data["prof"]
        room = data["salle"]
        start = datetime.datetime.strptime(data["start_date"], "%Y-%m-%d %H:%M")
        end = datetime.datetime.strptime(data["end_date"], "%Y-%m-%d %H:%M")
        color = data["color"]
    
        start_minutes = (start.hour*60 + start.minute) - 495
        end_minutes = (end.hour*60 + end.minute) - 495
        day = start.strftime("%Y-%m-%d")
        if(not day in courses):
            courses[day] = []
        courses[day].append(Course(name, teacher, room, start_minutes, end_minutes, color))
    return {"token": token, "data":courses}
