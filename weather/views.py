import json
import traceback

from django.core.paginator import Paginator
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from taiwan_area_info.task import fetch_area_info
from weather.models import ObservationStationInfo, PrecipitationObservationStatics


# Create your views here.
@method_decorator(csrf_exempt, name="dispatch")
class Precipitation(View):
    def get(self, request, *args, **kwarg):
        try:
            # get district name
            data = json.loads(request.body)
            district_name = data.get("district_name")
            page_num = data.get("page_num", 1)
            if not district_name:
                return JsonResponse(
                    {"message": "district_name is required"}, status=400
                )
            # fetch uuid from district model by message Q
            district_uuid = fetch_area_info(district_name).get("district_uuid")
            if not district_uuid:
                return JsonResponse({"message": "not found district"}, status=400)
            # fetch observation station uuid thur district uuid
            observation_station = ObservationStationInfo.objects.filter(
                district_uuid=district_uuid
            ).first()
            if not observation_station:
                return JsonResponse(
                    {"message": "not found observation_station"}, status=400
                )
            # fetch Precipitation thur obs_station uuid
            precipitation_static = PrecipitationObservationStatics.objects.filter(
                station_uuid=observation_station._id
            )
            if not precipitation_static:
                return JsonResponse(
                    {"message": "not found precipitation_static"}, status=400
                )
            # paginator Precipitation
            paginator = Paginator(precipitation_static, 100)
            page_requested = paginator.page(page_num)

            result = {
                "page": page_num,
                "total_pages": paginator.num_pages,
                "total_data": paginator.count,
                "observation_station": observation_station.station_name,
                "data": [
                    {
                        "observe_time": q_set.observe_time,
                        "updated_at": q_set.updated_at,
                        "precipi_in_observe_time": q_set.precipi_obstime,
                        "precipi_past_10_min": q_set.precipi_past_10_min,
                        "precipi_past_1_hr": q_set.precipi_past_1_hr,
                        "precipi_past_3_hr": q_set.precipi_past_3_hr,
                    }
                    for q_set in page_requested
                ],
            }

            return JsonResponse({f"{district_name}_precipi": result}, status=200)
        except json.JSONDecodeError:
            return JsonResponse({"message": "Invalid JSON format"}, status=400)
        except Exception as e:
            traceback.print_exc()
            return JsonResponse({"message": "failed", "error": str(e)}, status=500)
