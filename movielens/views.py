from django.http import HttpRequest, HttpResponse

def index(request : HttpRequest):
    return HttpResponse("Sample response")