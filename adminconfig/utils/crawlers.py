import LocalDriver

LocalDriver.LocalDriver()

import json
import time as pytime
import uuid
from datetime import datetime

import pytz
import requests
from django.conf import settings
from django.db import transaction

from taiwan_area_info.models import AreaInfo, DistrictInfo  # noqa: E402
from youbike.models import YoubikeStationsInfo, YoubikeStationsStatus

API_URL = "https://apis.youbike.com.tw/json/"
SOURCE = ["area-all.json", "station-yb1.json", "station-yb2.json"]

with open("adminconfig/utils/Stations.json", mode="r", encoding="utf8") as file:
    STATIONS = json.loads(file.read())


@transaction.atomic
def create_area_info(url: str):
    session = requests.Session()
    go = session.get(url)
    if go.status_code == 200:
        data = json.loads(go.text)
    try:
        for county in data:
            query = {
                "area_name_cn": county["area_name_tw"],
            }
            # area_mapping = {
            #     "area_code": county["area_code"],
            #     "area_code_2": county["area_code_2"],
            # }

            area = AreaInfo.objects.get(**query)
            area.area_code = county["area_code"]
            area.area_code_2 = county["area_code_2"]
            area.save()
            print("area ok")
            # area_uuid = area._id

            # service_mapping = {
            #     "area_uuid": area_uuid,
            #     "station_no_start": county["station_start"],
            #     "station_no_end": county["station_end"],
            #     "bike_types": tuple(f"Type{val}" for val in county["bike_type"]),
            #     "member_count": county["member_card_count"],
            #     "ride_count1": county["ride_count"],
            #     "ride_count2": county["ride_count2"],
            #     "visit_count": county["visit_count"],
            # }
            # service = ServiceInfo(**service_mapping)
            # service.save()
            # print("service ok")
    except Exception:
        transaction.set_rollback(True)
        raise Exception("Write in db error")


@transaction.atomic
def station_info_crawler(url: str):
    session = requests.Session()
    go = session.get(url)
    if go.status_code == 200:
        data = json.loads(go.text)
    try:
        area_cache = {}
        district_cache = {}
        for idx, station in enumerate(data):
            # 從area model 拿到 area uuid
            if area_cache.get(station["area_code"]) is None:
                area = AreaInfo.objects.get(area_code=station["area_code"])
                area_uuid = area._id
                area_cache[station["area_code"]] = area_uuid
            else:
                area_uuid = area_cache[station["area_code"]]
            # 判斷district有沒有建立在district model
            if station["district_tw"] in district_cache.keys():
                # 有則將district_uuid拿到
                district_uuid = district_cache[station["district_tw"]]
            # 無則建立district，並將uuid存下
            else:
                district = create_district_info(station, area_uuid)
                district_uuid = district._id
                district_cache[station["district_tw"]] = district_uuid

            # 將station info存到 station info model
            station_info = create_station_info(station, area_uuid, district_uuid)

            # 將station status存到 station status (獨立function)
            create_station_status_info(station, station_info._id)
            if idx % 100 == 0:
                print(f"{idx} stations completed")
    except Exception:
        transaction.set_rollback(True)
        raise Exception("Write in db error")


@transaction.atomic
def create_district_info(station: dict, area_uuid: uuid.UUID):
    try:
        new_district = DistrictInfo.objects.create(
            area_uuid=area_uuid,
            district_tw=station["district_tw"],
            district_en=station["district_en"],
        )
        return new_district

    except Exception:
        transaction.set_rollback(True)
        raise Exception("Write in db error")


@transaction.atomic
def create_station_info(station: dict, area_uuid: uuid.UUID, district_uuid: uuid.UUID):
    try:
        station_info = YoubikeStationsInfo.objects.create(
            area_uuid=area_uuid,
            district_uuid=district_uuid,
            name_tw=station["name_tw"],
            name_en=station["name_en"],
            address_tw=station["address_tw"],
            address_en=station["address_en"],
            lat=station["lat"],
            lng=station["lng"],
            station_no=station["station_no"],
        )
        return station_info

    except Exception:
        transaction.set_rollback(True)
        raise Exception("station_info Write in db error")


@transaction.atomic
def create_station_status_info(
    station: dict, station_uuid: uuid.UUID, bulk_create=False
):
    try:
        if bulk_create:
            station_status_info = YoubikeStationsStatus(
                station_uuid=station_uuid,
                parking_spaces=station["parking_spaces"],
                available_spaces=station["available_spaces"],
                record_time=station["time"],
                station_status=station["status"],
            )
        else:
            station_status_info = YoubikeStationsStatus.objects.create(
                station_uuid=station_uuid,
                parking_spaces=station["parking_spaces"],
                available_spaces=station["available_spaces"],
                record_time=station["time"],
                station_status=station["status"],
            )
        return station_status_info

    except Exception:
        transaction.set_rollback(True)
        raise Exception(f"station_status Write in db error {station}")


def get_list():
    data = {}
    stations = YoubikeStationsInfo.objects.all()
    for sta in stations:
        data[sta.station_no] = str(sta._id)
    data = json.dumps(data)
    with open("Stations.json", mode="w", encoding="utf8") as file:
        file.write(data)


def station_status_crawler(url: str):
    session = requests.Session()
    go = None
    for i in range(10):
        if i != 0:
            pytime.sleep(1)
        print(f"第{i+1}次連線{url}")
        go = session.get(url)
        if go.status_code == 200:
            break
    else:
        raise Exception("connecting fail")
    try:
        print(f"connecting {url} start")
        data = json.loads(go.text)
        station_uuid = None
        for station in data:
            time = datetime.strptime(station["time"], "%Y-%m-%d %H:%M:%S")
            time = pytz.timezone(settings.TIME_ZONE).localize(time)
            station["time"] = time
            if station["station_no"] not in STATIONS.keys():
                area = AreaInfo.objects.get(area_code=station["area_code"])
                district = DistrictInfo.objects.get(district_tw=station["district_tw"])
                station_uuid = create_station_info(station, area._id, district._id)._id
                get_list()

        if station_uuid is None:
            station_uuid = STATIONS[station["station_no"]]
        await_created = [
            create_station_status_info(station, station_uuid, bulk_create=True)
            for station in data
        ]
        with transaction.atomic():
            YoubikeStationsStatus.objects.bulk_create(await_created, batch_size=1000)
        print("completed")
    except Exception:
        raise Exception(f"data fail {station}")


if __name__ == "__main__":
    for idx in range(1, 3):
        # go
        station_status_crawler(API_URL + SOURCE[idx])
