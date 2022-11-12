import requests
import sys
import json
import codecs
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.serialization import load_pem_public_key

#URLPREFIX = "https://ll213.host.cs.st-andrews.ac.uk"
URLPREFIX = "http://localhost:22849"

#send encrypted and signed message to server
def sendmessage(message,to,by):
    
    #get receivers public key from server
    public_keystr = getspecpublickey(to)
    public_key = load_pem_public_key(public_keystr.encode())

    #create signature using your own private key
    signature = myprivatekey.sign(
        str.encode(message),
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
         hashes.SHA256()
    )

    #encrypt message using receivers public key
    encrypted_message = public_key.encrypt(
        str.encode(message),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    #encrypt sender name
    encrypted_sender = public_key.encrypt(
        str.encode(by),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    URL = URLPREFIX + "/msg/sendmessage/"
    DATA = {'receiver':to,'encrypted_message':encrypted_message.hex(), 'signature':signature.hex(), 'sender':encrypted_sender.hex()}

    r = requests.post(url=URL, data=DATA)
    if(r.status_code != 200):
        print("failure to send message")
        quit()

#register public key and username to server
def register(username):
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )

    encrypted_pem_private_key = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )

    pem_public_key = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    #store both public and private keys in pem format
    private_key_file = open("rsa.pem", "w+")
    private_key_file.write(encrypted_pem_private_key.decode())
    private_key_file.close()

    public_key_file = open("rsa.pub", "w+")
    public_key_file.write(pem_public_key.decode())
    public_key_file.close()

    #send username and public key to server
    URL = URLPREFIX + "/msg/registeruser/"
    DATA = {'username':username,'public_key':pem_public_key}

    r = requests.post(url=URL, data=DATA)
    if(r.status_code!=200):
        print("registration failure, duplicate username?")
        print("please reregister your now saved keys are not on the server")
        quit()

#returns public key of the username stored on the server database
def getspecpublickey(username):
    URL = URLPREFIX + "/msg/certify/"
    DATA = {'username':username}
    r = requests.post(url=URL, data=DATA)
    if(r.status_code!=200):
        print(f"public key retrieval failure for {username}, not a registered user?")
        quit()
    
    return r.text

#gets puzzle needed for reading messages and proof of private key ownership
def getpuzzle():
    URL = URLPREFIX + "/msg/getpuzzle/"
    r = requests.get(url=URL)
    return r.text

def readmessages(username):

    #get puzzle, sign it
    puzzle = getpuzzle()
    signature = myprivatekey.sign(
        str.encode(puzzle),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
        ),
         hashes.SHA256()
    )

    #ensures proper sending over post
    signature=signature.hex()

    URL = URLPREFIX + "/msg/readmessage/"
    DATA = {'username':username,'signature':signature,'puzzle':puzzle}
    r = requests.post(url=URL, data=DATA)
    if(r.status_code!=200):
        print("failure reading messages: puzzle failed?")
        quit()

    msg_list = json.loads(r.text)
    no_newmessages = len(msg_list)
    if(no_newmessages > 0):
        print(f"you have {no_newmessages} new message(s)")
    else:
        print("no new messages")

    for msg in msg_list:
        try:
            #decrypt message and sender
            decrypted_message = myprivatekey.decrypt(
                codecs.decode(msg["fields"]["payload"],'hex_codec'),
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            decrypted_sender = myprivatekey.decrypt(
                codecs.decode(msg["fields"]["sender"],'hex_codec'),
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )

            #get claimed senders public key for verification of signature
            sender_public_keystr = getspecpublickey(decrypted_sender.decode("utf-8"))
            sender_publickey = load_pem_public_key(sender_public_keystr.encode())

            #verify given signature with decoded message
            sender_publickey.verify(
                codecs.decode(msg["fields"]["signature"],'hex_codec'),
                decrypted_message,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )

            print("verified message from " + decrypted_sender.decode('utf-8') + ":")
            print(decrypted_message)
        except:
            print("message could not be verified and decrypted")

def printusage():
    print("Usage:")
    print("python client.py <HOST_URL> register <NEW_USERNAME>")
    print("     creates a keypair storing them in rsa.pem and rsa.pub and stores the public key on the server")
    print("     be sure to remember your username!!!")
    print("     this will overwrite any previously stored keyfile with the same name")
    print("python client.py <HOST_URL> read <YOUR_USERNAME>")
    print("     gets your unread messages from the server, they will be deleted from the server by the time you get them, you will not be able to read them again")
    print("python client.py <HOST_URL> send <MESSAGE> <ADDRESSEE_USERNAME> <YOUR_USERNAME>")
    print("     sends the message the user specified, be sure to write your username correctly")

def loadPrivateKey():
    #load in private key from file
    global myprivatekey
    with open("rsa.pem", "rb") as privatekey_file:
        myprivatekey = serialization.load_pem_private_key(
            privatekey_file.read(),
            password=None
        )

if(len(sys.argv) > 1):
    URLPREFIX = sys.argv[1]

if(len(sys.argv) == 4):
    if(sys.argv[2] == "register"):
        print("registering user...")
        register(sys.argv[3])
        print("registered")
    elif(sys.argv[2] == "read"):
        loadPrivateKey()
        print("getting messages for user:" + sys.argv[3])
        readmessages(sys.argv[3])
    else:
        printusage()

elif(len(sys.argv) == 6 and sys.argv[2] == "send"):
    loadPrivateKey()
    print("sending message...")
    sendmessage(sys.argv[3],sys.argv[4],sys.argv[5])
    print("message sent")
else:
    printusage()







