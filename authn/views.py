import json
import traceback

from django.contrib.auth.hashers import check_password
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from authn.models import User as user_model

# Create your views here.


@method_decorator(csrf_exempt, name="dispatch")
class Register(View):
    def post(self, request, *args, **kargs):
        # 先從request中提取post來的資料
        try:
            data = json.loads(request.body)
            username = data.get("username")
            password = data.get("password")
            e_mail = data.get("e_mail")
            if any([username is None, password is None, e_mail is None]) is True:
                return JsonResponse(
                    {"message": "Username, password and e_mail are required"},
                    status=400,
                )
            # 判斷是否有資料存在
            if user_model.objects.filter(e_mail=e_mail).exists():
                return JsonResponse(
                    {"message": "E_mail has been registered"},
                    status=400,
                )
            # 建立新user
            user = user_model.objects.create(
                username=username, password=password, e_mail=e_mail
            )
            result = {
                "_id": str(user._id),
                "username": user.username,
                "created_at": user.created_at,
                "updated_at": user.updated_at,
            }
            # 返回成功建立response
            return JsonResponse(
                {"user": result},
                status=201,
            )
        except json.JSONDecodeError:
            return JsonResponse({"message": "Invalid JSON format"}, status=400)
        except Exception as e:
            traceback.print_exc()
            return JsonResponse({"message": "failed", "error": str(e)}, status=500)


@method_decorator(csrf_exempt, name="dispatch")
class Login(View):
    def post(self, request, *args, **kwargs):
        try:
            # retrieve data from request
            data = json.loads(request.body)
            e_mail = data.get("e_mail")
            password = data.get("password")
            # check e_mail is valid, and exist
            if not e_mail or not password:
                return JsonResponse(
                    {"message": "E-mail and password required"}, status=400
                )
            if user_model.objects.filter(e_mail=e_mail).exists() is False:
                return JsonResponse({"message": "E-mail does not exist"}, status=400)
            # retrieve user from DB
            user = user_model.objects.filter(e_mail=e_mail).first()
            # match psw
            if check_password(password, user.password) is False:  # type: ignore
                return JsonResponse({"message": "Wrong password"}, status=400)
            return JsonResponse({"message": "Login success"}, status=200)
            # response success or not
        except json.JSONDecodeError:
            return JsonResponse({"message": "Invalid JSON format"}, status=400)
        except Exception as e:
            traceback.print_exc()
            return JsonResponse({"message": "failed", "error": str(e)}, status=500)
