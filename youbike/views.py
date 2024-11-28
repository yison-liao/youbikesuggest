import json
import traceback

from django.core.paginator import Paginator
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from youbike.models import YoubikeStationsInfo as info_models
from youbike.models import YoubikeStationsStatus as status_models
from youbike.utils import get_lat_lng_bounds

SEARCH_DISTANCE = 5  # km


@method_decorator(csrf_exempt, name="dispatch")
class YoubikeStationsStatus(View):
    def get(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            station_uuid = data.get("station_uuid", None)
            if not station_uuid:
                raise Exception("station_uuid is required")

            from_datetime = data.get("from_datetime", None)
            to_datetime = data.get("to_datetime", None)

            page_num = data.get("page_num", 1)
            query = {
                "station_uuid": station_uuid,
            }
            if not query["from_datetime__gte"] and not query["to_datetime__lte"]:
                query["from_datetime__gte"] = from_datetime
                query["to_datetime__lte"] = to_datetime
            station_status_query_sets = status_models.objects.filter(**query)

            paginator = Paginator(station_status_query_sets, 100)
            page_requested = paginator.page(page_num)
            result = {
                "page": page_num,
                "total_pages": paginator.num_pages,
                "total_data": paginator.count,
                f"{station_uuid}": [
                    {
                        "parking_spaces": q_set.parking_spaces,
                        "available_spaces": q_set.available_spaces,
                        "station_status": q_set.station_status,
                        "record_time": q_set.record_time,
                        "update_at": q_set.update_at,
                    }
                    for q_set in page_requested
                ],
            }

            return JsonResponse(
                {"station_status": result},
                status=201,
            )
        except json.JSONDecodeError:
            return JsonResponse({"message": "Invalid JSON format"}, status=400)
        except Exception as e:
            traceback.print_exc()
            return JsonResponse({"message": "failed", "error": str(e)}, status=500)


@method_decorator(csrf_exempt, name="dispatch")
class YoubikeStationsInfo(View):
    def get(self, request, *args, **kwargs):
        """
        json format
        {
        "mode":["get_one", "get_many", "by_distance"], # pick one
        "page_num": 1,  # if mode is get_many, it is necessary
        "lat": float,
        "lng":float, # in mode by_distance, function will set this as center, and search within Certain radius
        }
        """
        try:
            MODE_OPTIONS = ["get_one", "get_many", "by_distance"]
            data = json.loads(request.body)
            mode = data.get("mode")
            if not mode:
                raise Exception("No mode description")
            elif mode not in MODE_OPTIONS:
                raise Exception("Unknown mode")
            query = {}
            # get one
            if mode == MODE_OPTIONS[0]:
                query["name_tw"] = data.get("name_tw", None)
                query["name_en"] = data.get("name_en", None)
                query["station_no"] = data.get("station_no", None)
            elif mode == MODE_OPTIONS[1]:
                # get many
                query["area_uuid"] = data.get("area_uuid", None)
                query["district_uuid"] = data.get("district_uuid", None)
                page_num = data.get("page_num", 1)
            elif mode == MODE_OPTIONS[2]:
                # get by distance
                lat = data.get("lat")
                lng = data.get("lng")
                range = [
                    get_lat_lng_bounds(lat=lat, lng=lng, distance_km=SEARCH_DISTANCE)
                ]
                query["lat__gte"], query["lat__lte"] = range[0], range[1]
                query["lng__gte"], query["lng__lte"] = range[2], range[3]

            for key, val in query.items():
                if val is None:
                    del query[f"{key}"]

            station_info_query_sets = info_models.objects.filter(**query)
            if page_num:
                paginator = Paginator(station_info_query_sets, 100)
                page_requested = paginator.page(page_num)
                result = {
                    "page": page_num,
                    "total_pages": paginator.num_pages,
                    "total_data": paginator.count,
                    "data": [
                        {
                            "_id": q_set._id,
                            "area_uuid": q_set.area_uuid,
                            "district_uuid": q_set.district_uuid,
                            "station_no": q_set.station_no,
                            "name_tw": q_set.name_tw,
                            "name_en": q_set.name_en,
                            "address_tw": q_set.address_tw,
                            "address_en": q_set.address_en,
                            "lat": q_set.lat,
                            "lng": q_set.lng,
                        }
                        for q_set in page_requested
                    ],
                }
            else:
                result = {
                    "data": [
                        {
                            "_id": q_set._id,
                            "area_uuid": q_set.area_uuid,
                            "district_uuid": q_set.district_uuid,
                            "station_no": q_set.station_no,
                            "name_tw": q_set.name_tw,
                            "name_en": q_set.name_en,
                            "address_tw": q_set.address_tw,
                            "address_en": q_set.address_en,
                            "lat": q_set.lat,
                            "lng": q_set.lng,
                        }
                        for q_set in station_info_query_sets
                    ],
                }

            return JsonResponse(
                {"station_status": result},
                status=201,
            )
        except json.JSONDecodeError:
            return JsonResponse({"message": "Invalid JSON format"}, status=400)
        except Exception as e:
            traceback.print_exc()
            return JsonResponse({"message": "failed", "error": str(e)}, status=500)
