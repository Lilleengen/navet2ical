import datetime
import requests
import os
from bs4 import BeautifulSoup
from icalendar import Calendar, Event
from flask import Flask, request
import requests_toolbelt.adapters.appengine

requests_toolbelt.adapters.appengine.monkeypatch()

app = Flask(__name__)

@app.route("/")
def cal():
    if request.args.get("token") != os.environ["TOKEN"]:
        return "No"
    auth_obj = {"username": os.environ["USERNAME"], "password": os.environ["PASSWORD"]}
    auth = requests.post("https://ifinavet.no/login", auth_obj, allow_redirects=False)

    cookies = {
        'PLAY_SESSION': auth.headers["set-cookie"].split("=",1)[1]
    }

    presentations = requests.get("https://ifinavet.no/event", cookies=cookies)

    parse = BeautifulSoup(presentations.text, "html5lib")

    d = datetime.date.today()

    semesters = parse.find('div', {'class': 'semesterplan-content'})
    sem_all = semesters.find_all('div', {'class': 'semester'})

    sem = sem_all[0]

    if d.month > 6:
        sem = sem_all[1]

    urls = []
    for event in sem.find_all('div', {'class': 'event'}):
        urls.append(event.find('a').get('href'))

    events = []
    for url in urls:
        event = requests.get("https://ifinavet.no" + url, cookies=cookies)
        text = event.text.encode('ascii', 'ignore').decode('ascii')
        if "meldt, meld deg av" in text:
            parse = BeautifulSoup(event.text, "html.parser")
            title = parse.find('h1', {'class': 'event-title'}).text
            url = "https://ifinavet.no" + url
            infobox = parse.find_all('div', {'class': 'event-infobox-element'})
            time = infobox[0].find('p').text
            loc = infobox[1].find('p').text

            events.append({
                'title': title,
                'time': time,
                'loc': loc,
                'url': url
            })

    cal = Calendar()
    cal.add('prodid', '-//Navet to cal//ifinavet.no//')
    cal.add('version', '2.0')

    for event in events:
        cal_event = Event()
        cal_event.add('summary', event["title"])
        cal_event.add('url', event["url"])
        cal_event['location'] = event["loc"]
        date = datetime.datetime.strptime(event["time"], '%d.%m.%Y %H:%M')
        cal_event.add('dtstart', date - datetime.timedelta(hours=2))
        cal_event.add('dtend', date)
        cal_event.add('dtstamp', date - datetime.timedelta(hours=2))

        cal.add_component(cal_event)

    return cal.to_ical()