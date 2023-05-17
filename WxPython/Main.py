from hashlib import sha1  # for hashing the password
import random  # for generating a random session ID
import urllib.request  # for making HTTP requests

import Includes.Params as params
import Includes.Secrets as secrets

# generate a random 32 character string
def generateSessionID():
    SESSID = ""
    for i in range(32):
        tval = format(random.randint(0, 15), 'x')
        SESSID += tval.upper()
    return SESSID

# run a query against the API using the given login parameters
def runLoginQuery(url, queryParams, sessid):
    queryParams += f"&SessionID={sessid}"
    url_params = url + queryParams
    response = urllib.request.urlopen(url_params).read().decode('utf-8')

    return response

# xor a string with a number
def xorFn(pswd: str, num: int):
    numbin = format(num, '032b') # convert number to binary string
    startpos = len(numbin) # start at end of the string (right hand side)
    retval = ""

    for i in range(len(pswd)):
        charcode = ord(pswd[i])  # take character at position i
        startpos = len(numbin) - 8 if startpos == 0 else startpos - 8  # grab 8 bits (if at lhs of string, start again at rhs)
        comp = int(numbin[startpos:startpos + 8], 2)  # convert 8 bits to decimal
        hexcode = format(charcode ^ comp, 'x')  # xor character and 8 bits
        if len(hexcode) == 1:
            hexcode = "0" + hexcode # add leading zero if necessary
        retval += hexcode

    return retval.upper()

# login to the WX API and initiate a session encrypted over HTTPS
def login(url, sessid):
    pswdHash = sha1(secrets.password.encode('utf-8')).hexdigest()

    data = runLoginQuery(url, params.init, sessid) # initiate session

    #* TESTING AREA
    print("Initializadtion response: " + data) #TODO remove this line when done testing
    #* END TESTING AREA

    xorUsername = xorFn(secrets.username, (int(data) +1))
    hashXorUsername = sha1(xorUsername.encode('utf-8')).hexdigest().upper()
    xorPswdHash = xorFn(pswdHash, int(data))
    hashXorPswdHash = sha1(xorPswdHash.encode('utf-8')).hexdigest().upper()
    
    loginParams = f"{params.login}&Name={hashXorUsername}&Password={hashXorPswdHash}" # build the login parameters
    data = runLoginQuery(url, loginParams, sessid) # login to session

    #* TESTING AREA
    print("Login response: " + data) #TODO remove this line when done testing
    #* END TESTING AREA

#*TODO run a query against the API using the given parameters and session ID
def runQuery(url, queryParams, sessid):
    global SEQUENCE

    queryParams = sessid + queryParams + f"&Sequence={SEQUENCE}"
    url_params = url + queryParams

    #* TESTING AREA
    print("Query URL: " + url_params) #TODO remove this line when done testing
    #* END TESTING AREA

    response = urllib.request.urlopen(url_params).read().decode('utf-8')
    SEQUENCE += 1 # increment sequence number

    #* TESTING AREA
    print("Response: " + response) #TODO remove this line when done testing
    #* END TESTING AREA

    return response

#* main function
def main():
    url = f"https://{secrets.domain}//PRT_CTRL_DIN_ISAPI.dll?"
    sessionID = generateSessionID()

    login(url, sessionID)

    #* TESTING AREA
    print("Session ID: " + sessionID) #TODO remove this line when done testing
    print("Username: " + secrets.username) #TODO remove this line when done testing
    print("Password: " + secrets.password) #TODO remove this line when done testing
    print("Sequence: " + str(SEQUENCE)) #TODO remove this line when done testing

    runQuery(url, params.userList, sessionID) #TODO remove this line when done testing
    print("Sequence: " + str(SEQUENCE)) #TODO remove this line when done testing

    runQuery(url, params.areaList, sessionID) #TODO remove this line when done testing
    print("Sequence: " + str(SEQUENCE)) #TODO remove this line when done testing

    runQuery(url, params.doorList, sessionID) #TODO remove this line when done testing
    print("Sequence: " + str(SEQUENCE)) #TODO remove this line when done testing

    runQuery(url, params.inputList, sessionID) #TODO remove this line when done testing
    print("Sequence: " + str(SEQUENCE)) #TODO remove this line when done testing

    runQuery(url, params.outputList, sessionID) #TODO remove this line when done testing
    print("Sequence: " + str(SEQUENCE)) #TODO remove this line when done testing
    #* END TESTING AREA

SEQUENCE = 0

if __name__ == '__main__':
    main()
