from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

# Create your views here.
from django.http import HttpResponse

#todo
@csrf_exempt
def send(request):
    return HttpResponse("send mesg")

def read(request):
    return HttpResponse("readmsg")

def certify(request):
    return HttpResponse("certify")

def register(request):
    return HttpResponse("register")


