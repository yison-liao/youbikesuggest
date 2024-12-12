from celery import shared_task

from taiwan_area_info.models import AreaInfo, DistrictInfo


@shared_task
def fetch_area_info(district_name: str):
    try:
        query = {}
        query["district_tw"] = district_name
        district = DistrictInfo.objects.filter(**query).first()
        data = {}
        if district:
            data = {
                "district_uuid": district._id,
                "district_tw": district.district_tw,
                "district_en": district.district_en,
            }
            area = AreaInfo.objects.filter(_id=district.area_uuid).first()
            if area:
                data["Area_info"] = {
                    "area_name_cn": area.area_name_cn,
                    "area_name_en": area.area_name_en,
                    "area_uuid": area._id,
                    "geo": {
                        "lat_range": [area.lat_from, area.lat_to],
                        "lng_range": [area.lng_from, area.lng_to],
                    },
                }
        return data
    except Exception as e:
        raise e
