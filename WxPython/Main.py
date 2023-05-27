from hashlib import sha1  # for hashing the password
import random  # for generating a random session ID
import urllib.request  # for making HTTP requests

import Includes.Params as params
import Includes.Secrets as secrets

# global variables
SEQUENCE = 0

# class for user objects
class User:
    def __init__(self, name, recID):
        self.name = name
        self.recID = recID

# class for input/output objects (areas, doors, inputs, outputs, and trouble inputs)
class WxIO:
    def __init__(self, name, recID, statusKey):
        self.name = name
        self.recID = recID
        self.statusKey = statusKey

# class for area objects (inherits from wxIO)
class Area(WxIO):
    def __init__(self, name, recID, statusKey):
            super().__init__(name, recID, statusKey)

# class for door objects (inherits from wxIO)
class Door(WxIO):
    def __init__(self, name, recID, statusKey):
        super().__init__(name, recID, statusKey)

# class for input objects (inherits from wxIO)
class Input(WxIO):
    def __init__(self, name, recID, statusKey):
            super().__init__(name, recID, statusKey)

# class for output objects (inherits from wxIO)
class Output(WxIO):
    def __init__(self, name, recID, statusKey):
            super().__init__(name, recID, statusKey)

# class for trouble input objects (inherits from wxIO)
class TroubleInput(WxIO):
    def __init__(self, name, recID, statusKey):
            super().__init__(name, recID, statusKey)


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
def login(url):
    global SEQUENCE
    sessid = generateSessionID()
    pswdHash = sha1(secrets.password.encode('utf-8')).hexdigest()

    data = runLoginQuery(url, params.init, sessid) # initiate session

    xorUsername = xorFn(secrets.username, (int(data) +1))
    hashXorUsername = sha1(xorUsername.encode('utf-8')).hexdigest().upper()
    xorPswdHash = xorFn(pswdHash, int(data))
    hashXorPswdHash = sha1(xorPswdHash.encode('utf-8')).hexdigest().upper()
    
    loginParams = f"{params.login}&Name={hashXorUsername}&Password={hashXorPswdHash}" # build the login parameters
    data = runLoginQuery(url, loginParams, sessid) # login to session
    SEQUENCE = 0 # reset sequence number

    return sessid

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

# convert a string of key-value pairs to a dictionary
def convertToDict(inputString):
    dictionary = {}

    for item in inputString.split("&"):
        key, value = item.split("=")
        dictionary[int(key)] = value
    return dictionary

# get the key to find the status of an object
def getStatusKey(dictionary, item, dictName):
    statusKey = ""
    for key, value in dictionary.items():
        if value == item:
            statusKey = dictName + str(key)
            break
    return statusKey

def buildObjectList(ioList, name):
    switch = {
        "Area": [],
        "Door": [],
        "Input": [],
        "Output": [],
        "TroubleInput": []
    }
    objectList = switch.get(name, [])
    for key, value in ioList.items():
        statusKey = getStatusKey(ioList, value, name)
        if name == "Area":
            value = Area(value, key, statusKey)
        elif name == "Door":
            value = Door(value, key, statusKey)
        elif name == "Input":
            value = Input(value, key, statusKey)
        elif name == "Output":
            value = Output(value, key, statusKey)
        elif name == "TroubleInput":
            value = TroubleInput(value, key, statusKey)
        else:
            raise ValueError("Invalid object type")
        objectList.append(value)
    return objectList


#* main function
def main():
    url = f"https://{secrets.domain}/PRT_CTRL_DIN_ISAPI.dll?"

    # initiate session and get lists
    sessionID = login(url)
    userList = runQuery(url, sessionID, params.getList, params.users)
    accessLevelList = runQuery(url, sessionID, params.getList, params.accessLevels)
    areaList = runQuery(url, sessionID, params.getList, params.areas)
    doorList = runQuery(url, sessionID, params.getList, params.doors)
    inputList = runQuery(url, sessionID, params.getList, params.inputs)
    outputList = runQuery(url, sessionID, params.getList, params.outputs)
    troubleInputList = runQuery(url, sessionID, params.getList, params.troubleInputs)

    # build objects from lists
    areas = buildObjectList(areaList, "Area")
    doors = buildObjectList(doorList, "Door")
    inputs = buildObjectList(inputList, "Input")
    outputs = buildObjectList(outputList, "Output")
    troubleInputs = buildObjectList(troubleInputList, "TroubleInput")

    #* TESTING AREA
    print("\nAreas: ") #TODO remove this line when done testing
    for item in areas: #TODO remove this line when done testing
        print(f"{item.recID}. {item.name}, {item.statusKey}") #TODO remove this line when done testing
    print("\nDoors: ") #TODO remove this line when done testing
    for item in doors: #TODO remove this line when done testing
        print(f"{item.recID}. {item.name}, {item.statusKey}") #TODO remove this line when done testing
    print("\nInputs: ") #TODO remove this line when done testing
    for item in inputs: #TODO remove this line when done testing
        print(f"{item.recID}. {item.name}, {item.statusKey}") #TODO remove this line when done testing
    print("\nOutputs: ") #TODO remove this line when done testing
    for item in outputs: #TODO remove this line when done testing
        print(f"{item.recID}. {item.name}, {item.statusKey}") #TODO remove this line when done testing
    print("\nTrouble Inputs: ") #TODO remove this line when done testing
    for item in troubleInputs: #TODO remove this line when done testing
        print(f"{item.recID}. {item.name}, {item.statusKey}") #TODO remove this line when done testing
    print("\nUsername: " + secrets.username) #TODO remove this line when done testing
    #print("Password: " + secrets.password) #TODO remove this line when done testing
    print("SessionID: " + sessionID) #TODO remove this line when done testing
    #* END TESTING AREA

    ## OPEN DOOR
    #runQuery(url, sessionID, params.control, params.doors, doors[3].recID, 1)
    ## OPEN DOOOR


if __name__ == '__main__':
    main()