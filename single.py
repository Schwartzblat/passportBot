import requests
import json
from datetime import datetime, timedelta
from time import sleep
import asyncio
import threading
import jwt
import re


def get_api_key():
    res = requests.get('https://myvisit.com/bundles/plugins?v=3591605')
    pattern = "ApplicationAPIKey: '.+',"
    return re.findall(pattern, res.text)[0].split("'")[1]


token = ''
username = jwt.decode(token, options={"verify_signature": False})['unique_name']
api_key = get_api_key()
headers = {
    'Application-Api-Key': api_key,
    'Authorization': 'JWT ' + token,
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36',
    'Application-Name': 'myVisit.com v3.5'
}
dates = {}
questions = {
    "id": {
        "questionId": "113",
        "questionnaireItemId": "1674"
    },
    "phone": {
        "questionId": "114",
        "questionnaireItemId": "1675"
    }
}
user_data = {}

def answer(text, answer_type):
    baseurl = f'https://central.qnomy.com/CentralAPI/PreparedVisit/{username}/Answer'
    payload = {
        'AnswerIds': 'null',
        'AnswerText': text,
        'PreparedVisitToken': username,
        'QuestionId': questions[answer_type]['questionId'],
        'QuestionnaireItemId': questions[answer_type]['questionnaireItemId']
    }
    res = requests.post(baseurl, headers=headers, data=payload)
    while res.status_code != 200:
        res = requests.post(baseurl, headers=headers, data=payload)


def listen_to_service(service_id: str, location_name: str):
    baseurl = 'https://central.qnomy.com/CentralAPI/SearchAvailableDates'
    queryString = {
        'serviceId': service_id,
        'startDate': '2022-06-16'
    }
    print(service_id)
    while True:
        try:
            res = requests.get(baseurl, params=queryString, headers=headers)
            while res.status_code != 200:
                print(res.status_code)
                sleep(1)
                res = requests.get(baseurl, params=queryString, headers=headers)
            data = json.loads(res.text)
            if not data['Success'] or data['Results'] is None:
                continue
            for item in data['Results']:
                if dates.get(service_id) is None or item in dates.get(service_id):
                    continue
                print("New date:", item, "at", location_name, datetime.now())
                if is_interested():
                    book_appointment(service_id, item['calendarDate'], item['calendarId'])
            dates[service_id] = data['Results']
        except Exception as e:
            # print(e)
            pass
        sleep(5)


def is_interested():
    return input("Interested? (y/n)").lower() == 'y'


def get_time(service_id: str, calendar_id: str) -> list:
    baseurl = "https://central.qnomy.com/CentralAPI/SearchAvailableSlots"
    queryString = {
        'CalendarId': calendar_id,
        'ServiceId': service_id,
        'dayPart': 0
    }
    res = requests.get(baseurl, params=queryString, headers=headers)
    print(res.text)
    data = json.loads(res.text)
    if data['Success']:
        return data['Results']
    return []


def book_appointment(service_id: str, date: str, date_id: str):
    print(f"Booking appointment... at {date}")
    answer(user_data['id'], 'id')
    answer(user_data['phone'], 'phone')
    hour = get_time(service_id, date_id)[0]['Time']
    print("Hour: ", hour)
    baseurl = 'https://central.qnomy.com/CentralAPI/AppointmentSet'
    queryString = {
        'ServiceId': service_id,
        'appointmentDate': date,
        'appointmentTime': hour
    }
    res = requests.get(baseurl, params=queryString, headers=headers)
    print(res.text)
    exit(0)


def get_locations():
    baseurl = 'https://central.qnomy.com/CentralAPI/LocationSearch'
    queryString = {
        'currentPage': '1',
        'isFavorite': 'false',
        'orderBy': 'Distance',
        'organizationId': '56',
        'position': '{"lat": "32.1798", "lng": "34.9408", "accuracy": 1440}',
        'resultsInPage': '100',
        'serviceTypeId': '156',
        'src': 'mvws'
    }
    res = requests.get(baseurl, params=queryString, headers=headers)
    if res.status_code != 200:
        print(res.status_code)
        print(res.text)
        return []
    data = json.loads(res.text)
    return data['Results']


def get_input(locations: list):
    id = input("Enter your id number: ")
    phone_number = input("Enter your phone number: ")
    for i in range(len(locations)):
        print(str(i), locations[i]['LocationName'])

    locations_list = []
    print("Enter the numbers of the wanted locations. if you want to stop type 'quit': ")
    to_continue = input()
    while to_continue != "quit":
        try:
            locations_list.append(locations[int(to_continue)])
        except ValueError:
            print("Invalid input")
        to_continue = input()
    info_dict = {
        "id": id,
        "phone": phone_number,
        "locations": locations_list
    }
    return info_dict


def main():
    user_data = get_input(get_locations())
    locations = user_data['locations']
    for location in locations:
        threading.Thread(target=lambda: listen_to_service(location['ServiceId'], location['LocationName'])).start()
        sleep(2)
    sleep(1000000)


if __name__ == '__main__':
    main()
