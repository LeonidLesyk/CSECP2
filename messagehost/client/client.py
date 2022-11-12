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
def sendmessage(to,message,by):
    
    #get receivers public key from server
    public_keystr = getspecpublickey(to)
    public_key = load_pem_public_key(public_keystr.encode())
    if isinstance(public_key, rsa.RSAPublicKey):
        print("worked")

    #create signature using your own private key
    signature = myprivatekey.sign(
        str.encode(message),
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
         hashes.SHA256()
    )
    print(signature)

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
    print(r.text)

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
    print(pem_public_key.decode())

    r = requests.post(url=URL, data=DATA)
    print(r.status_code)

#returns public key of the username stored on the server database
def getspecpublickey(username):
    URL = URLPREFIX + "/msg/certify/"
    DATA = {'username':username}
    r = requests.post(url=URL, data=DATA)
    print("got key for user: " + username)
    print(r.text)
    return r.text

#gets puzzle needed for reading messages and proof of private key ownership
def getpuzzle():
    URL = URLPREFIX + "/msg/getpuzzle/"
    r = requests.get(url=URL)
    return r.text

def readmessages(username):

    puzzle = getpuzzle()
    print(type(puzzle))
    print(puzzle)
    signature = myprivatekey.sign(
        str.encode(puzzle),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
        ),
         hashes.SHA256()
    )

    """
    print(signature)
    mypublickey.verify(
        signature,
        str.encode(puzzle),
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    print("verified")
    
    signature = signature.hex()
    print("new sig")
    print(signature)
    print("puzzle")
    print(puzzle)
    print("publickeystring")
    print(pubkeystr)
    """

    #ensures proper sending over post
    signature=signature.hex()

    URL = URLPREFIX + "/msg/readmessage/"
    DATA = {'username':username,'signature':signature,'puzzle':puzzle}
    r = requests.post(url=URL, data=DATA)

    msg_list = json.loads(r.text)
    print(len(msg_list))
    #print(r.text)

    for msg in msg_list:
        print(bytes(msg["fields"]["payload"],'utf-8'))
        
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

        #verify
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


#load in private key from file
myprivatekey = None
privkeystr = None
with open("rsa.pem", "rb") as privatekey_file:
        
        myprivatekey = serialization.load_pem_private_key(
            privatekey_file.read(),
            password=None
        )

mypublickey = None
with open("rsa.pub", "rb") as keyfile:
        mypublickey = serialization.load_pem_public_key(
            keyfile.read(),
        )

with open("rsa.pub", "rb") as keyfile:
    pubkeystr = keyfile.read()


#register("me")
#sendmessage("me", "greetings","me")
readmessages("me")


