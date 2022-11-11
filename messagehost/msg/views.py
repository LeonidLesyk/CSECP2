from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from .models import public_keys
from .models import unread_messages
from datetime import datetime, timedelta

held_puzzles =[]

#todo
@csrf_exempt
def send(request):
    PAYLOAD = request.POST.get("encrypted_message")
    SIGNATURE = request.POST.get("signature")
    RECEIVER = request.POST.get("receiver")


    new_message = unread_messages(payload=PAYLOAD, signature=SIGNATURE,receiver=RECEIVER)

    new_message.save()
    print("message saved")
    return HttpResponse("send mesg")

def read(request):
    return HttpResponse("readmsg")

@csrf_exempt
def certify(request):
    requested_username = request.POST.get("username")
    entry = public_keys.objects.get(username=requested_username)
    print("giving following key for user: " + requested_username)
    print(entry.public_key)
    return HttpResponse(entry.public_key)

@csrf_exempt
def register(request):
    username = request.POST.get("username")
    public_key = request.POST.get("public_key")
    newuser = public_keys(username=username,public_key=public_key)
    newuser.save()
    return HttpResponse("register")

#gives a puzzle to be encrypted and sent back as proof of private key ownership (0 knowledge proof)
def givePuzzle(request):

    #clear puzzles older than 5 seconds
    while held_puzzles[0] + timedelta(5) < datetime.now():
        held_puzzles.pop(0)
    
    puzzle = datetime.now()

    held_puzzles.append(puzzle)
    return HttpResponse(puzzle)
