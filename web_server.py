#web_server.py
# 
# PURPOSE: a multi-threaded web server. Web is able to find files on a file system, and serve those files to an HTTP client.
# Paths that are prefixes with /api/ are API calls that run code. All other paths are searched on a local filesystem for files. 
# If the files or API paths do not exist, or have problems, appropriate error messages are returned.
# 

import socket
import threading
import sys
import os
import json
import sqlite3
import uuid

# Constants
HOST = '127.0.0.1'                 # Symbolic name meaning all available interfaces
PORT = 8080

COOKIE_NAME = "verySecureCookie"
METHOD_NOT_ALLOWED_RESPONSE = """HTTP/1.1 405 Method Not Allowed\n\n"""
NOT_FOUND_RESPONSE = """HTTP/1.1 404 NOT FOUND\n\n"""
UNAUTHORIZED_RESPONSE = """HTTP/1.1 401 Unauthorized\n\n"""
OK_RESPONSE = """HTTP/1.1 200 OK\n\n"""
OK_RESPONSE_IMAGE = """HTTP/1.1 200 OK\nContent-Type: image/jpeg\n\n"""
####################### SERVER FUNCTIONS / API FUNCTIONS #############################
def processGet(headers,  id):
    url = headers[0].split(" ")[1]
    byte_content = None

    if id != None and url == "/api/tweet":
        tweets = buildJSONtweets(id)
        response = OK_RESPONSE + tweets
        
    elif url == "/api/tweet": #trying to access api/tweet without being logged in/having a valid cookie
        response = UNAUTHORIZED_RESPONSE
        
    else: #not api paths - search for files on the system and serve them
        if url == '/':
            url = '/index.html'
            
        try:
            if url.endswith(".jpeg"): #if an image, open the image and send a response with image content type
                file = open(os.getcwd() + '/files-distribution' + url, 'rb')
                byte_content = file.read()
                file.close()
                response = OK_RESPONSE_IMAGE 
            else: #all other files, including html
                file = open(os.getcwd() + '/files-distribution' + url, encoding='utf-8')
                content = file.read()
                file.close()
                
                response = OK_RESPONSE + content
            
        except FileNotFoundError:
            response = NOT_FOUND_RESPONSE
    return (response, byte_content,) #return a tuple to unpack -> response always has an http response and byte_content can be None

def processPost(headers,  id):
    apiRequest = headers[0].split(" ")[1]
    body = json.loads(headers[-1])
    response = UNAUTHORIZED_RESPONSE #default to unauthorized response
    
    if id != None and apiRequest == '/api/tweet' : #cannot post a tweet if not logged in
        tweet = body['tweet']
        if tweet != '': #if tweet is empty, do not post it
            addTweet(id, tweet)
        response = 'HTTP/1.1 200 OK\n\n'
    
    elif apiRequest == '/api/login':
        cookie = logIn(body['username'], body['password']) #try to log in -> returns cookie if successful
        if(cookie != None):
            response = 'HTTP/1.1 200 OK\nSet-Cookie: {}={}; path=/\n\n'.format(COOKIE_NAME, cookie)

    return response

def processDelete(headers, id):
    apiRequest = headers[0].split(" ")[1]
    response = UNAUTHORIZED_RESPONSE
    
    if apiRequest == '/api/login': 
        logOut(id)
        response = 'HTTP/1.1 200 OK\nSet-Cookie: {}={}; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT\n\n'.format(COOKIE_NAME, '')
        
    elif id != None and apiRequest.startswith('/api/tweet'): #cannot delete a tweet if not logged in
        uuid = apiRequest.split('/')[-1]
        result = deleteTweet(id,uuid)
        if(result != None):
            response = 'HTTP/1.1 200 OK\n\n'
        
    return response

#Handles the HTTP request
def processRequest(request):
    
    # get headers, body can be accessed by headers[-1] later
    headers = request.split('\r\n')
    response =  METHOD_NOT_ALLOWED_RESPONSE #default to method not allowed response
    
    #check if cookie exists in the headers
    cookieVal = findCookie(headers,request)
    id = checkCookie(cookieVal) #returns user id if cookie is valid and None otherwise
    
    byte_content = None
    
    print(headers[0])
    
    method = headers[0].split(" ")[0]
    if(method == 'GET'):
        response, byte_content = processGet(headers, id)
    elif(method == 'POST'):
        response = processPost(headers,  id)
    elif(method == 'DELETE'):
        response = processDelete(headers,  id)
    return (response, byte_content,)

def clientThread(conn, addr):
    #process clients request on the thread
    print('Connected by', addr)
    
    request = conn.recv(1024).decode()
    response, byteContent = processRequest(request)
    
    conn.sendall(response.encode())
    #send byte content if any was requested
    if(byteContent != None):
        conn.sendall(byteContent)

    conn.close()

###################### COOKIES and "DATABASE" ##############################
def initDB():
    connection = sqlite3.connect("./db/comp3010eeter.db") #opens the db or creates it if it does not exist
    cursor = connection.cursor()
    
    #create tables if they don't exist
    cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT, sessionCookie TEXT, UNIQUE(username))")
    cursor.execute("CREATE TABLE IF NOT EXISTS tweets (id INTEGER PRIMARY KEY, user_id INTEGER, tweet TEXT, uuid TEXT, UNIQUE(uuid))")
    
    #populate users table if it is empty or IGNORE if values already exist
    cursor.execute("""INSERT OR IGNORE INTO users (username, password, sessionCookie) VALUES ("DenysP", "securePassword", "testCookieForDenys"),
                   ("Rick", "bestgrandpa", "testCookieForRick"),
                   ("cTest", "itsasecret", "testCookieForcTest")""")
    
    connection.commit()
    connection.close()
    
def checkCookie(cookie): #returns user id if cookie is valid and None otherwise
    result = None
    if(cookie != None):
        connection = sqlite3.connect("./db/comp3010eeter.db") #connect to db
        cursor = connection.cursor()
        
        result = cursor.execute("SELECT id FROM users WHERE sessionCookie = ?", (cookie,)).fetchone()
        if(result!=None): #if cookie is valid return user id
            result = result[0]
        connection.close()
    return result

def logIn(username, password): #check is username and password are valid, if so returns cookie
    connection = sqlite3.connect("./db/comp3010eeter.db") #connect to db
    cursor = connection.cursor()
    
    cookie = None
    userId = cursor.execute("SELECT id FROM users WHERE username = ? AND password = ?", (username, password)).fetchone()
    if(userId != None): #if user exists give them a unique cookie
        cookie = str(uuid.uuid4())
        cursor.execute("UPDATE users SET sessionCookie = ? WHERE id = ?", (cookie, userId[0]))
        connection.commit()
    connection.close()
    return cookie

def logOut(userId):
    connection = sqlite3.connect("./db/comp3010eeter.db") #connect to db
    cursor = connection.cursor()
    
    cursor.execute("UPDATE users SET sessionCookie = ? WHERE id = ?", ("", userId))
    connection.commit()
    connection.close()

def addTweet(id, tweet):
    connection = sqlite3.connect("./db/comp3010eeter.db") #connect to db
    cursor = connection.cursor()
    
    uniqueIdentifier = str(uuid.uuid4())
    cursor.execute("INSERT INTO tweets (user_id, tweet, uuid) VALUES (?, ?, ?)", (id, tweet, uniqueIdentifier))
    connection.commit()
    connection.close()

def deleteTweet(id, uuid): #id is user id and uuid is the tweet uuid
    connection = sqlite3.connect("./db/comp3010eeter.db") #connect to db
    cursor = connection.cursor()
    
    #try to find the tweet with the given uuid and user id
    result = cursor.execute("SELECT tweet FROM tweets WHERE uuid = ? AND user_id = ?", (uuid, id)).fetchone()
    
    if(result != None):
        cursor.execute("DELETE FROM tweets WHERE uuid = ? AND user_id = ?", (uuid, id))
        connection.commit()
        
    connection.close()
    return result #returns the tweet if it was deleted and None otherwise

def getTweets(): #returns a list of tuples in a form (tweet, user_id)
    connection = sqlite3.connect("./db/comp3010eeter.db") #connect to db
    cursor = connection.cursor()
    
    tweets = cursor.execute("SELECT uuid, user_id, tweet FROM tweets").fetchall()
    connection.close()
    
    return tweets

def getUser(id):
    connection = sqlite3.connect("./db/comp3010eeter.db") #connect to db
    cursor = connection.cursor()
    
    user = cursor.execute("SELECT username FROM users WHERE id = ?", (id,)).fetchone()
    if(user!=None):
        user = user[0]
    return user

def buildJSONtweets(id):
    tweets = getTweets()
    tweetsToReturn = "" #a string of json objects
    
    for tweet in tweets:
        jsonTweet = dict()
        jsonTweet["tweet"] = tweet[2]
        jsonTweet["username"] = getUser(tweet[1])
        jsonTweet["uuid"] = tweet[0]
        
        if id == tweet[1]:
            jsonTweet["button"] = True
        else:
            jsonTweet["button"] = False
        tweetsToReturn += json.dumps(jsonTweet) + "\n"
    return tweetsToReturn

def findCookie( headers, request):
    if COOKIE_NAME in request:
        for header in headers:
            if header.startswith("Cookie"):
                index = header.find(COOKIE_NAME) #find the index of the cookie we are looking for
                header = header[index:] #get the substring starting from the cookie
                header = header.split(";")#split the string into a list of cookies
                for cookie in header:
                    if cookie.startswith(COOKIE_NAME):
                        return cookie.split("=")[1]
    return None

####################################################
########## ____Web-Server-Main____##################
####################################################
print("Initiating database...")
initDB()
print("Database initiated")

#create the socket for the web server
webServerSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
webServerSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

#bind and start listening for clients
webServerSock.bind((HOST, PORT))
webServerSock.listen()
print("\nweb server is listening on port {}".format(PORT))



while True:
    try:
        #accept client connection
        conn, addr = webServerSock.accept()
        
        #handle each client on a separate thread
        thread = threading.Thread(target=clientThread, args=(conn,addr))
        thread.start()
        
        print(threading.active_count())
        
            
    except Exception as e:
        print("\nException caught: {}".format(e))
    except KeyboardInterrupt:
        print("\nKeyboard interrupt caught")
        webServerSock.close()
        sys.exit(0)

