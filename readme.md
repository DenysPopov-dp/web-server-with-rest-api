## **Instructions**
#### **by Denys Popov**
---
### Part 1
---
### Usernames, Passwords and default cookies(for auto log in for testing)

Username: DenysP 
Password: securePassword
Cookie: testCookieForDenys

Username: Rick
Password: bestgrandpa
Cookie: testCokieForRick

Username: cTest
Password: itsasecret
Cookie: testCookieForcTest

### **web_server.py | Server**
- *To use - type the following in the command line :* `python web_server.py` or `python3 web_server.py`
- runs on `127.0.0.1:8080`
- The default cookies are created when the DB is created. So if you logged in with any of the users and want to restore the default cookie, you need to delete the database file in ./db/ and restart the server.

---
### Part 2 
---
- Before testing delete the db file in ./db/ (if it is there) and restart the server, so that the users have default cookies set up for testing. If db file is not in ./db/ then just start the server.


### **test.c**
- preset cookie for user cTest is: `testCookieForcTest`
- make sure that the test is running on te same serve, since the server runs on localhost and the test is hardcoded to connect to localhost. BOTH on PORT `8080`
- to run use:
  - (1) `make`
  - (2) `test <defaultCookie> "<the tweet you want to post>"`. Example of use: `test testCookieForcTest "this is my test tweet. Bye now!"`
  - (3) the test will create the tweet with POST as a user "cTest" and assert that the tweet was created with GET

---
### Part 3
---
### **test.py**
- preset cookie for user cTest is: `testCookieForcTest`
- preset cookie for user DenysP is: `testCookieForDenys`
- to run use:
  - `python test.py` or `python3 test.py`
  - the test will try to delete the post, created by cTest in **part 2**, with DELETE as user DenysP and assert with GET that the tweet was NOT deleted. Then the test will delete the test as user cTest and assert with GET that the tweet was deleted.