class SaveUserIdMiddleware:
    def __init__(self, get_response, some_arg=None):
        self.get_response = get_response
        self.some_arg = some_arg

    def __call__(self, request):
        # Lógica que utiliza some_arg
        response = self.get_response(request)
        if request.user.is_authenticated:
            request.session['user_id'] = request.user.id
        else:
            request.session.pop('user_id', None)
        return response


# class SaveUserIdMiddleware:
#     def _init_(self, get_response):
#         self.get_response = get_response

#     def _call_(self, request):
#         response = self.get_response(request)
#         if request.user.is_authenticated:
#             request.session['user_id'] = request.user.id
#         else:
#             request.session.pop('user_id', None)
#         return response