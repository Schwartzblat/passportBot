import requests
import json
from datetime import datetime, timedelta
from time import sleep
import timeit
import asyncio


start = timeit.default_timer()

headers = {
        'Application-Api-Key': '',
        'Authorization': '',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36',
        'Application-Name': 'myVisit.com v3.5'
}

async def get_dates(service_id: str) -> list[datetime]:
    baseurl = 'https://central.qnomy.com/CentralAPI/SearchAvailableDates'
    queryString = {
        'serviceId': service_id,
        'startDate': '2022-06-16'
    }
    print(service_id)
    res = requests.get(baseurl, params=queryString, headers=headers)
    while res.status_code != 200:
        sleep(1)
        print("Retrying...")
        res = requests.get(baseurl, params=queryString, headers=headers)
    if res.status_code != 200:
        print(res.status_code)
        print(res.text)
        return []
    data = json.loads(res.text)
    dates = []
    if not data['Success'] or data['Results'] is None:
        return []
    slot_promises = []
    for result in data['Results']:
        slot_promises.append(getSlots(service_id, result['calendarId'], result['calendarDate']))
    days = []
    for i in range(len(slot_promises)):
        slot_output = await slot_promises[i]
        days.append(slot_output)

    for day in days:
        for time in day['times']:
            dates.append(str(
                datetime.strptime(day['calendar'], "%Y-%m-%dT00:00:00") + timedelta(minutes=time['Time'])))
    return dates


async def getSlots(service_id: str, calendar_id: str, calendar_date: str):
    queryString = {
        'CalendarId': calendar_id,
        'ServiceId': service_id,
        'dayPart': 0
    }
    baseurl = 'https://central.qnomy.com/CentralAPI/searchAvailableSlots'
    loop = asyncio.get_event_loop()
    # res = await
    res = await loop.run_in_executor(None, lambda: requests.get(baseurl, params=queryString, headers=headers))
    while res.status_code != 200:
        sleep(1)
        print("Retrying...")
        res = await loop.run_in_executor(None, lambda: requests.get(baseurl, params=queryString, headers=headers))
    if res.status_code != 200:
        print(res.status_code)
        return {
            'times': [],
            'calendar': calendar_date
        }
    times = json.loads(res.text)
    try:
        if times['Results'] is None:
            return {
                'times': [],
                'calendar': calendar_date
            }
    except KeyError:
        return {
            'times': [],
            'calendar': calendar_date
        }
    return {
        'times': times['Results'],
        'calendar': calendar_date
    }


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

async def main():
    locations = get_locations()
    promises = []
    for location in locations:
        t = asyncio.create_task(get_dates(str(location['ServiceId'])))
        promises.append(t)

    for i in range(len(promises)):
        while not promises[i].done():
            await asyncio.sleep(0.1)
        output = promises[i].result()
        print(locations[i]['LocationName'], output)
    print(f"finished in {timeit.default_timer() - start} seconds.")


if __name__ == '__main__':
    asyncio.run(main())