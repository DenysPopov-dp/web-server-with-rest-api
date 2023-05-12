# test.py
# PURPOSE: test for the webserver. Tests that a user can't delete a tweet that they didn't make. Then test
# that a user can delete a tweet that they made. Then test that the tweet was deleted successfully.

import socket
import json



# Constants
HOST = '127.0.0.1'                 # Symbolic name meaning all available interfaces
PORT = 8080

USERNAME1 = "DenysP"
COOKIE1 = "testCookieForDenys"

USERNAME_FROM_C_TEST = "cTest"
COOKIE_FROM_C_TEST = "testCookieForcTest"


#######################################################################################
########## Test deleting tweet that the user did not make #############################
#######################################################################################

#create the socket for and connect
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((HOST, PORT))

#get tweets to choose the one to delete
request = "GET /api/tweet HTTP/1.1\r\nHost: 127.0.0.1\r\nCookie:verySecureCookie={}\r\n\r\n".format(COOKIE1)
sock.sendall(request.encode())

#check that the we got the response
response = sock.recv(1024).decode()
print(response.strip())
assert response.startswith("HTTP/1.1 200 OK")

#get body of the response
body = response.split("\n\n")[-1]

uuidToDelete= ""
body = body.split("\n")
for tweet in body[:len(body)-1]: #get the uuid of the tweet made by another user
    tweet = json.loads(tweet)
    if tweet["username"] != USERNAME1:
        uuidToDelete = tweet["uuid"]

print("ID of the tweet to delete: " + uuidToDelete)


#######################################################################################
########## Test deleting tweet that the user made #############################
#######################################################################################

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((HOST, PORT))

#try to delete the post
request = "DELETE /api/tweet/{} HTTP/1.1\r\nHost: 127.0.0.1\r\nCookie:verySecureCookie={}\r\n\r\n".format(uuidToDelete,COOKIE1)
sock.sendall(request.encode())

response = sock.recv(1024).decode()
print(response.strip())
assert response.startswith("HTTP/1.1 401 Unauthorized")
print("Tweet with uuid: " + uuidToDelete + " was not deleted by user: " + USERNAME1)


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((HOST, PORT))

#try to delete the post, but now using the the user who made the post
request = "DELETE /api/tweet/{} HTTP/1.1\r\nHost: 127.0.0.1\r\nCookie:verySecureCookie={}\r\n\r\n".format(uuidToDelete,COOKIE_FROM_C_TEST)
sock.sendall(request.encode())

response = sock.recv(1024).decode()
print(response.strip())
assert response.startswith("HTTP/1.1 200 OK")
print("Tweet with uuid: " + uuidToDelete + " was deleted by user: " + USERNAME_FROM_C_TEST)

#######################################################################################
########## Test that the tweet was indeed deleted #####################################
#######################################################################################

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((HOST, PORT))

#get tweets to choose the one to delete
request = "GET /api/tweet HTTP/1.1\r\nHost: 127.0.0.1\r\nCookie:verySecureCookie={}\r\n\r\n".format(COOKIE1)
sock.sendall(request.encode())

#check that the we got the response
response = sock.recv(1024).decode()
print(response.strip())
assert response.startswith("HTTP/1.1 200 OK")

#get body of the response
body = response.split("\n\n")[-1]

#check every tweet for the uuid we just deleted
body = body.split("\n")
for tweet in body[:len(body)-1]: #get the uuid of the tweet made by another user
    tweet = json.loads(tweet)
    assert(tweet["uuid"] != uuidToDelete)

print("Tweet with uuid: " + uuidToDelete + " was deleted successfully")
