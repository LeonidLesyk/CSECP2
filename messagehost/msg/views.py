from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse

def send(request):
    return HttpResponse("send mesg")

def read(request):
    return HttpResponse("readmsg")

def certify(request):
    return HttpResponse("certify")

def register(request):
    return HttpResponse("register")


