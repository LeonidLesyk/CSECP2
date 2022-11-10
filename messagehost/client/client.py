import requests
import sys
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes

URLPREFIX = "https://ll213.host.cs.st-andrews.ac.uk"
#send encrypted and signed message to server
def sendmessage(to,message):
    
    
    #get receivers public key from server

    
    #encrypt message

    ciphertext = message
    #ciphertext = public_key.encrypt(
    #    message,
    #    padding.OAEP(
    #        mgf=padding.MGF1(algorithm=hashes.SHA256()),
    #        algorithm=hashes.SHA256(),
    #        label=None
    #    )
    #)

    #sign message

    URL = URLPREFIX + "/msg/sendmessage/"
    DATA = {'receiver':to,'message':ciphertext}

    r = requests.post(url=URL, data=DATA)
    print(r.text)



#register public key and username to server
def register(username,password):
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )

    private_key_password = str.encode(password)
    encrypted_pem_private_key = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.BestAvailableEncryption(private_key_password)
    )

    pem_public_key = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

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
    

sendmessage("a","hello")
register("abc","password123")

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