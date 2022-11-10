import requests
import sys

def sendmessage(to,message):
    URL = "https://ll213.host.cs.st-andrews.ac.uk/msg/sendmessage/"
    DATA = {'receiver':to,'message':message}

    r = requests.post(url=URL, data=DATA)

    print(r.text)

sendmessage("a","hello")