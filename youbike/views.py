import json
import traceback

from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from youbike.models import YoubikeStationsStatus as status_models


# Create your views here.
# youbikestatus input->station uuid , datetime.
# output -> {"station-uuid":[datas]}
# pagination
@method_decorator(csrf_exempt, name="dispatch")
class YoubikeStationsStatus(View):
    def get(self, request, *args, **kargs):
        try:
            data = json.loads(request.body)
            station_uuid = data.get("station_uuid")
            from_datatime = data.get("from_datatime", None)
            to_datetime = data.get("to_datetime", None)
            query = {
                "station_uuid": station_uuid,
                "from_datatime__gte": from_datatime,
                "to_datetime__lte": to_datetime,
            }
            station_status_query_sets = status_models.objects.filter(**query)
            result = {
                f"{station_uuid}": [
                    {
                        "parking_spaces": q_set.parking_spaces,
                        "available_spaces": q_set.available_spaces,
                        "station_status": q_set.station_status,
                        "record_time": q_set.record_time,
                        "update_at": q_set.update_at,
                    }
                    for q_set in station_status_query_sets
                ]
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
