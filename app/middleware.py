from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import UserData
from django.conf import settings

class AuthenticateUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        excluded_urls = ['/user/register/', '/user/login/','/user/addUser/','/user/check-login/','/']
        print(request.path_info)
        if request.path_info in excluded_urls:
            return self.get_response(request)
        token = request.COOKIES.get('ExpenseToken')

        if not token:
            return HttpResponseRedirect(reverse('homepage'))

        try:
            user_obj = UserData.objects.get(id=token)
            request.user = user_obj
        except UserData.DoesNotExist:
            return HttpResponseRedirect(reverse('homepage'))

        response = self.get_response(request)
        return response
