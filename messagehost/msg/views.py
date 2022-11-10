from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from .models import public_keys
#todo
@csrf_exempt
def send(request):
    print(request.POST.get("message"))
    return HttpResponse("send mesg")

def read(request):
    return HttpResponse("readmsg")

def certify(request):
    return HttpResponse("certify")

@csrf_exempt
def register(request):
    username = request.POST.get("username")
    public_key = request.POST.get("public_key")
    #print(public_key)
    #todo
    public_key = public_key[public_key.find('\n') + 1: public_key.rfind('\n',0,len(public_key)-1)].replace("\n", "")
    print(public_key[public_key.find('\n') + 1: public_key.rfind('\n',0,len(public_key)-1)].replace("\n", ""))
    newuser = public_keys(username=username,public_key=public_key)
    newuser.save()
    return HttpResponse("register")


