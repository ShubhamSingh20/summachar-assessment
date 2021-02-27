from rest_framework.request import Request

class JWTCookieApply:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request : Request):
        # A Simple work around to avoid making anymore changes
        # to the djangorestsimple_jwt. Take the jwt token from the 
        # cookie & append it in the header

        if httpCookie := request.COOKIES.get('jwt', False):
            request.META['HTTP_AUTHORIZATION'] = "Bearer {}".format(httpCookie)

        response = self.get_response(request)
        return response