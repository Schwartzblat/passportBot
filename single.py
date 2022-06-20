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


def listen_to_service(service_id: str, location_name: str):
    baseurl = 'https://central.qnomy.com/CentralAPI/SearchAvailableDates'
    queryString = {
        'serviceId': service_id,
        'startDate': '2022-06-16'
    }
    # print(service_id)
    while True:
        try:
            res = requests.get(baseurl, params=queryString, headers=headers)
            while res.status_code != 200:
                sleep(1)
                res = requests.get(baseurl, params=queryString, headers=headers)
            data = json.loads(res.text)
            if not data['Success'] or data['Results'] is None:
                continue
            for item in data['Results']:
                if dates.get(service_id) is None or item in dates.get(service_id):
                    continue
                print("New date:", item, "at", location_name)
            dates[service_id] = data['Results']
        except Exception as e:
            # print(e)
            pass
        sleep(5)


def is_interested():
    pass


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


def book_appointment(service_id: str, date: str, hour: str, user_data: dict):
    baseurl = 'https://central.qnomy.com/CentralAPI/AppointmentSet'
    queryString = {
        'ServiceId': service_id,
        'appointmentDate': date,
        'appointmentTime': hour
    }
    res = requests.get(baseurl, params=queryString, headers=headers)
    print(res.text)


def get_locations():
    baseurl = 'https://central.qnomy.com/CentralAPI/LocationSearch'
    queryString = {
        'currentPage': '1',
        'isFavorite': 'false',
        'orderBy': 'Distance',
        'organizationId': '56',
        'position': '{"lat": "", "lng": "", "accuracy": 1440}',
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


def main():
    locations = get_locations()
    for location in locations:
        threading.Thread(target=lambda: listen_to_service(location['ServiceId'], location['LocationName'])).start()
        sleep(0.1)
    sleep(1000000)


if __name__ == '__main__':
    # sleep(10 * 3600 + 16 * 60)
    main()
