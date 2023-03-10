import requests, json
import urllib.parse
import datetime

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
    data = {
        "dateDebut": "2023-03-06",
        "dateFin": "2023-03-12",
        "avecTrous": False
    }
    newHeaders = headers.copy()
    newHeaders['x-token'] = token
    return makePost('https://api.ecoledirecte.com/v3/Eleves/{}/emploidutemps.awp'.format(userId), data, params, newHeaders)