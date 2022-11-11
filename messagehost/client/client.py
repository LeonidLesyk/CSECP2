import requests
import sys
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.serialization import load_pem_public_key

#URLPREFIX = "https://ll213.host.cs.st-andrews.ac.uk"
URLPREFIX = "http://localhost:22849"
#send encrypted and signed message to server
def sendmessage(to,message):
    
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

    URL = URLPREFIX + "/msg/sendmessage/"
    DATA = {'receiver':to,'encrypted_message':encrypted_message, 'signature':signature}

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

#sendmessage("a","hello")
#register("me")

myprivatekey = None

with open("rsa.pem", "rb") as privatekey_file:

        myprivatekey = serialization.load_pem_private_key(
            privatekey_file.read(),
            password=None
        )

sendmessage("me", "hi")
#getspecpublickey("robert")

#with open("rsa.pem", "rb") as privatekey_file:
#
#        private_key = serialization.load_pem_private_key(
#            privatekey_file.read(),
#            password=b"123",
#        )

#plaintext = private_key.decrypt(
#    ciphertext,
#    padding.OAEP(
#        mgf=padding.MGF1(algorithm=hashes.SHA256()),
#        algorithm=hashes.SHA256(),
#        label=None
#    )
#)

#print(plaintext)