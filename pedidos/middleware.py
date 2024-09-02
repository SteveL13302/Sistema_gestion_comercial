from django.utils.deprecation import MiddlewareMixin
from .models import Cliente

class SaveUserIdMiddleware(MiddlewareMixin):
    def __init__(self, get_response, some_arg=None):
        self.get_response = get_response
        self.some_arg = some_arg

    def __call__(self, request):
        response = self.get_response(request)
        if request.user.is_authenticated:
            request.session['user_id'] = request.user.id
        else:
            request.session.pop('user_id', None)
        return response

<<<<<<< HEAD
# class ClienteMiddleware(MiddlewareMixin):
#     def process_request(self, request):
#         if request.user.is_authenticated:
#             if 'user_id' in request.session:
#                 try:
#                     request.cliente = Cliente.objects.get(user_id=request.session['user_id'])
#                 except Cliente.DoesNotExist:
#                     request.cliente = None
#             else:
#                 request.cliente = request.user.cliente if hasattr(request.user, 'cliente') else None
#         else:
#             request.cliente = None

class ClienteMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.user.is_authenticated:
            try:
                request.cliente = Cliente.objects.get(user_id=request.user.id)
            except Cliente.DoesNotExist:
                request.cliente = None
=======
class ClienteMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.user.is_authenticated:
            if 'user_id' in request.session:
                try:
                    request.cliente = Cliente.objects.get(user_id=request.session['user_id'])
                except Cliente.DoesNotExist:
                    request.cliente = None
            else:
                request.cliente = request.user.cliente if hasattr(request.user, 'cliente') else None
>>>>>>> 8c9ea26bb767f236a6778a3174630cfa22d79cc4
        else:
            request.cliente = None
