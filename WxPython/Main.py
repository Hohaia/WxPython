from hashlib import sha1  # for hashing the password
import random  # for generating a random session ID
import urllib.request  # for making HTTP requests

import Includes.Params as params
import Includes.Secrets as secrets

# generate a random 32 character string
def generateSessionID():
    sessid = ""
    for i in range(32):
        tval = format(random.randint(0, 15), 'x')
        sessid += tval.upper()
    return sessid

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

    xorUsername = xorFn(secrets.username, (int(data) +1))
    hashXorUsername = sha1(xorUsername.encode('utf-8')).hexdigest().upper()
    xorPswdHash = xorFn(pswdHash, int(data))
    hashXorPswdHash = sha1(xorPswdHash.encode('utf-8')).hexdigest().upper()
    
    loginParams = f"{params.login}&Name={hashXorUsername}&Password={hashXorPswdHash}" # build the login parameters
    data = runLoginQuery(url, loginParams, sessid) # login to session

#*TODO run a query against the API using the given parameters and session ID
def runQuery(url, sessid, queryType, subType, recID = None, command = None, data1 = None, data2 = None):
    global SEQUENCE

    queryParams = f"{sessid}{queryType}{subType}"
    if recID is not None:
        queryParams += f"&RecId={recID}"
    if command is not None:
        queryParams += f"&Command={command}"
    if data1 is not None:
        queryParams += f"&Data1={data1}"
    if data2 is not None:
        queryParams += f"&Data2={data2}"
    queryParams += f"&Sequence={SEQUENCE}"
    url_params = url + queryParams

    response = urllib.request.urlopen(url_params).read().decode('utf-8')
    SEQUENCE += 1 # increment sequence number

    # TODO handle exceptions for invalid queries

    #* TESTING AREA
    print(f"Query: {url_params}") #TODO remove this line when done testing
    #* END TESTING AREA

    if queryType == params.getList:
        return convertToDict(response)

    return response

#* convert a string of key-value pairs to a dictionary
def convertToDict(inputString):
    dictionary = {}

    for item in inputString.split("&"):
        key, value = item.split("=")
        dictionary[int(key)] = value
    return dictionary

#* get the record ID from a dictionary
def getRecID(list, rec):
    # initialize the key to None
    recID = None

    # loop through the dictionary using enumerate to get both index and key
    for index, key in enumerate(list.keys()):
        if list[key] == rec:
            recID = key
            break

    return recID


#* main function
def main():
    url = f"https://{secrets.domain}/PRT_CTRL_DIN_ISAPI.dll?"
    sessionID = generateSessionID()

    login(url, sessionID)
    userList = runQuery(url, sessionID, params.getList, params.users)
    areaList = runQuery(url, sessionID, params.getList, params.areas)
    doorList = runQuery(url, sessionID, params.getList, params.doors)
    inputList = runQuery(url, sessionID, params.getList, params.inputs)
    outputList = runQuery(url, sessionID, params.getList, params.outputs)
    troubleInputList = runQuery(url, sessionID, params.getList, params.troubleInputs)

    #* TESTING AREA
    print("Session ID: " + sessionID) #TODO remove this line when done testing
    print("Username: " + secrets.username) #TODO remove this line when done testing
    print("Password: " + secrets.password + "\n") #TODO remove this line when done testing
    print("\nUsers:") #TODO remove this line when done testing
    for key, value in userList.items(): #TODO remove this line when done testing
        print(f"{key}. {value}") #TODO remove this line when done testing
    print("\nAreas:") #TODO remove this line when done testing
    for key, value in areaList.items(): #TODO remove this line when done testing
        print(f"{key}. {value}") #TODO remove this line when done testing
    print("\nDoors:") #TODO remove this line when done testing
    for key, value in doorList.items(): #TODO remove this line when done testing
        print(f"{key}. {value}") #TODO remove this line when done testing
    print("\nInputs:") #TODO remove this line when done testing
    for key, value in inputList.items(): #TODO remove this line when done testing
        print(f"{key}. {value}") #TODO remove this line when done testing
    print("\nOutputs:") #TODO remove this line when done testing
    for key, value in outputList.items(): #TODO remove this line when done testing
        print(f"{key}. {value}") #TODO remove this line when done testing
    print("\nTrouble Inputs:") #TODO remove this line when done testing
    for key, value in troubleInputList.items(): #TODO remove this line when done testing
        print(f"{key}. {value}") #TODO remove this line when done testing
    print("\n") #TODO remove this line when done testing

    test = runQuery(url, sessionID, params.control, params.doors, getRecID(doorList, "Josiah"), 1) #TODO remove this line when done testing
    print(f"Response: {test}") #TODO remove this line when done testing
    print(f"Sequence: {SEQUENCE}\n") #TODO remove this line when done testing
    #* END TESTING AREA


SEQUENCE = 0

if __name__ == '__main__':
    main()