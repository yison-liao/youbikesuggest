import LocalDriver

LocalDriver.LocalDriver()

import json
import time as pytime
import uuid
from datetime import datetime
from uuid import UUID

import pytz
import requests
from django.conf import settings
from django.db import transaction

from taiwan_area_info.models import AreaInfo, DistrictInfo  # noqa: E402
from weather.models import ObservationStationInfo, PrecipitationObservationStatics
from youbike.models import YoubikeStationsInfo, YoubikeStationsStatus

API_URL = "https://apis.youbike.com.tw/json/"
SOURCE = ["area-all.json", "station-yb1.json", "station-yb2.json"]
CENTRAL_WEATHER_ADMIN_API_URL = f"https://opendata.cwa.gov.tw/api/v1/rest/datastore/O-A0002-001?Authorization={settings.CENTRAL_WEATHER_ADMIN_API_TOKEN}&format=JSON"

with open("adminconfig/utils/Stations.json", mode="r", encoding="utf8") as file:
    STATIONS = json.loads(file.read())

with open("adminconfig/utils/ObsStations.json", mode="r", encoding="utf8") as file:
    OBS_STATIONS = json.loads(file.read())


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
    with open("adminconfig/utils/Stations.json", mode="w", encoding="utf8") as file:
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


@transaction.atomic
def create_ObsStation_info(station_info: dict):
    try:
        obs_station = ObservationStationInfo.objects.create(**station_info)
        return obs_station
    except Exception:
        transaction.set_rollback(True)
        raise Exception("obs_station Write in db error")


@transaction.atomic
def create_ObsStation_statics(station: dict, obs_station_id: UUID, bulk_create=False):
    try:
        time = datetime.fromisoformat(station["ObsTime"]["DateTime"])
        if bulk_create:
            obs_station_statics = PrecipitationObservationStatics(
                station_uuid=obs_station_id,
                observe_time=time,
                precipi_obstime=float(
                    station["RainfallElement"]["Now"]["Precipitation"]
                ),
                precipi_past_10_min=float(
                    station["RainfallElement"]["Past10Min"]["Precipitation"]
                ),
                precipi_past_1_hr=float(
                    station["RainfallElement"]["Past1hr"]["Precipitation"]
                ),
                precipi_past_3_hr=float(
                    station["RainfallElement"]["Past3hr"]["Precipitation"]
                ),
            )
        else:
            obs_station_statics = PrecipitationObservationStatics.objects.create(
                station_uuid=obs_station_id,
                observe_time=time,
                precipi_obstime=float(
                    station["RainfallElement"]["Now"]["Precipitation"]
                ),
                precipi_past_10_min=float(
                    station["RainfallElement"]["Past10Min"]["Precipitation"]
                ),
                precipi_past_1_hr=float(
                    station["RainfallElement"]["Past1hr"]["Precipitation"]
                ),
                precipi_past_3_hr=float(
                    station["RainfallElement"]["Past3hr"]["Precipitation"]
                ),
            )

        return obs_station_statics
    except Exception:
        transaction.set_rollback(True)
        raise Exception("ObsStation_statics Write in db error")


@transaction.atomic
def precipitation_crawler(url: str):
    session = requests.Session()
    go = None
    for i in range(10):
        if i != 0:
            pytime.sleep(1)
        print(f"第{i+1}次連線 precipitation")
        go = session.get(url)
        if go.status_code == 200:
            break
    else:
        raise Exception("connecting fail")
    area_set = AreaInfo.objects.all()
    area_dict = {area.area_name_cn: area._id for area in area_set}
    district_set = DistrictInfo.objects.all()
    district_dict = {district.district_tw: district._id for district in district_set}
    print(f"connecting {url} start")
    data = json.loads(go.text)
    data = data["records"]["Station"]
    try:
        for station in data:
            # step1 建立觀測站基本資料，與area、district連結 *排除南投縣、花蓮縣、宜蘭縣、台東縣、離島
            if (
                station["GeoInfo"]["CountyName"] not in area_dict.keys()
                or station["GeoInfo"]["TownName"] not in district_dict.keys()
            ):
                continue
            # step2 建立觀測資料
            # 觀測站資料
            station_info = {
                "station_name": station["StationName"],
                "station_id": station["StationId"],
                "altitude": station["GeoInfo"]["StationAltitude"],
                "area_uuid": area_dict[station["GeoInfo"]["CountyName"]],
                "district_uuid": district_dict[station["GeoInfo"]["TownName"]],
                "lat": float(station["GeoInfo"]["Coordinates"][1]["StationLatitude"]),
                "lng": float(station["GeoInfo"]["Coordinates"][1]["StationLongitude"]),
            }
            obs_station = create_ObsStation_info(station_info)
            # 雨量資料
            create_ObsStation_statics(station, obs_station._id)
    except Exception:
        transaction.set_rollback(True)
        raise Exception("ObsStation_statics Write in db error")


@transaction.atomic
def precipitation_statics_crawler(url: str):  # TODO
    session = requests.Session()
    go = None
    for i in range(10):
        if i != 0:
            pytime.sleep(1)
        print(f"第{i+1}次連線 {url}")
        go = session.get(url)
        if go.status_code == 200:
            break
    else:
        raise Exception("connecting fail")

    print("connecting precipitation start")
    data = json.loads(go.text)
    data = data["records"]["Station"]
    try:
        await_data = []
        for station in data:
            # step1 get station uuid
            if station["StationId"] not in OBS_STATIONS.keys():
                continue
            obs_station_uuid = OBS_STATIONS[station["StationId"]]
            # step2 建立觀測資料
            # 雨量資料
            await_data.append(
                create_ObsStation_statics(station, obs_station_uuid, bulk_create=True)
            )
        with transaction.atomic():
            PrecipitationObservationStatics.objects.bulk_create(
                await_data, batch_size=1000
            )
        print("completed")
    except Exception:
        transaction.set_rollback(True)
        raise Exception("ObsStation_statics Write in db error")


def get_obsStation_list():
    # 進資料庫把所有的obs站點UUID抓出來
    # key-value -> stationID : UUID
    obs_station_set = ObservationStationInfo.objects.all()
    data_set = {station.station_id: str(station._id) for station in obs_station_set}
    with open("adminconfig/utils/ObsStations.json", mode="w", encoding="utf8") as file:
        content = json.dumps(data_set)
        file.write(content)


if __name__ == "__main__":
    for idx in range(1, 3):
        station_status_crawler(API_URL + SOURCE[idx])
    precipitation_statics_crawler(CENTRAL_WEATHER_ADMIN_API_URL)
