from hashlib import sha1  # for hashing the password
import random  # for generating a random session ID
import urllib.request # for making HTTP requests

import Includes.Params as params
import Includes.Secrets as secrets
import Includes.StatusCodeMaps as codeMaps

# global variables
SEQUENCE = 0

# class for user objects
class User:
    def __init__(self, name, recID):
        self.name = name
        self.recID = recID

# class for input/output objects (areas, doors, inputs, outputs, and trouble inputs)
class WxIO:
    def __init__(self, name, recID, sessid):
        self.name = name
        self.recID = recID
        self.sessid = sessid
        self.url = f"https://{secrets.domain}/PRT_CTRL_DIN_ISAPI.dll?"

# class for area objects (inherits from wxIO)
class Area(WxIO):
    def __init__(self, name, recID, sessid):
            super().__init__(name, recID, sessid)

    def status(self):
        global SEQUENCE
        requestURL = f"{self.url}{self.sessid}Request&Type=Status&SubType=GXT_AREAS_TBL&StartId={self.recID}&EndId={self.recID}&Sequence={SEQUENCE}"
        response = urllib.request.urlopen(requestURL).read().decode('utf-8')
        SEQUENCE += 1
        lst = [int(x) for x in response.split('=')[1].split(',')]
        lst[0] = codeMaps.alarmStatus1.get(lst[0], lst[0])
        lst[1] = codeMaps.alarmStatus2.get(lst[1], lst[1])
        lst[2] = codeMaps.alarmStatus3.get(lst[2], lst[2])
        return lst

# class for door objects (inherits from wxIO)
class Door(WxIO):
    def __init__(self, name, recID, sessid):
        super().__init__(name, recID, sessid)
    def status(self):
        global SEQUENCE
        requestURL = f"{self.url}{self.sessid}Request&Type=Status&SubType=GXT_DOORS_TBL&StartId={self.recID}&EndId={self.recID}&Sequence={SEQUENCE}"
        response = urllib.request.urlopen(requestURL).read().decode('utf-8')
        SEQUENCE += 1
        lst = [int(x) for x in response.split('=')[1].split(',')]
        lst[0] = codeMaps.doorStatus1.get(lst[0], lst[0])
        lst[1] = codeMaps.doorStatus2.get(lst[1], lst[1])
        return lst

# class for input objects (inherits from wxIO)
class Input(WxIO):
    def __init__(self, name, recID, sessid):
            super().__init__(name, recID, sessid)
    def status(self):
        global SEQUENCE
        requestURL = f"{self.url}{self.sessid}Request&Type=Status&SubType=GXT_INPUTS_TBL&StartId={self.recID}&EndId={self.recID}&Sequence={SEQUENCE}"
        response = urllib.request.urlopen(requestURL).read().decode('utf-8')
        SEQUENCE += 1
        lst = [int(x) for x in response.split('=')[1].split(',')]
        lst[0] = codeMaps.inputStatus1.get(lst[0], lst[0])
        lst[1] = codeMaps.inputStatus2.get(lst[1], lst[1])
        return lst

# class for output objects (inherits from wxIO)
class Output(WxIO):
    def __init__(self, name, recID, sessid):
            super().__init__(name, recID, sessid)
    def status(self):
        global SEQUENCE
        requestURL = f"{self.url}{self.sessid}Request&Type=Status&SubType=GXT_PGMS_TBL&StartId={self.recID}&EndId={self.recID}&Sequence={SEQUENCE}"
        response = urllib.request.urlopen(requestURL).read().decode('utf-8')
        SEQUENCE += 1
        lst = [int(x) for x in response.split('=')[1].split(',')]
        #lst[0] = codeMaps.alarmStatus1.get(lst[0], lst[0])
        #lst[1] = codeMaps.alarmStatus2.get(lst[1], lst[1])
        #lst[2] = codeMaps.alarmStatus3.get(lst[2], lst[2])
        return lst

# class for trouble input objects (inherits from wxIO)
class TroubleInput(WxIO):
    def __init__(self, name, recID, sessid):
            super().__init__(name, recID, sessid)
    def status(self):
        global SEQUENCE
        requestURL = f"{self.url}{self.sessid}Request&Type=Status&SubType=GXT_TROUBLEINPUTS_TBL&StartId={self.recID}&EndId={self.recID}&Sequence={SEQUENCE}"
        response = urllib.request.urlopen(requestURL).read().decode('utf-8')
        SEQUENCE += 1
        lst = [int(x) for x in response.split('=')[1].split(',')]
        #lst[0] = codeMaps.alarmStatus1.get(lst[0], lst[0])
        #lst[1] = codeMaps.alarmStatus2.get(lst[1], lst[1])
        #lst[2] = codeMaps.alarmStatus3.get(lst[2], lst[2])
        return lst


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

def buildObjectList(ioList, name, sessid):
    switch = {
        "Area": [],
        "Door": [],
        "Input": [],
        "Output": [],
        "TroubleInput": []
    }
    objectList = switch.get(name, [])
    for key, value in ioList.items():
        if name == "Area":
            value = Area(value, key, sessid)
        elif name == "Door":
            value = Door(value, key, sessid)
        elif name == "Input":
            value = Input(value, key, sessid)
        elif name == "Output":
            value = Output(value, key, sessid)
        elif name == "TroubleInput":
            value = TroubleInput(value, key, sessid)
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
    areas = buildObjectList(areaList, "Area", sessionID)
    doors = buildObjectList(doorList, "Door", sessionID)
    inputs = buildObjectList(inputList, "Input", sessionID)
    outputs = buildObjectList(outputList, "Output", sessionID)
    troubleInputs = buildObjectList(troubleInputList, "TroubleInput", sessionID)

    #* TESTING AREA
    print("\nArea Statuses: ") #TODO remove this line when done testing
    for i in areas: #TODO remove this line when done testing
        print(f"{i.name}: {i.status()}") #TODO remove this line when done testing
    print("\nDoor Statuses: ") #TODO remove this line when done testing
    for i in doors: #TODO remove this line when done testing
        print(f"{i.name}: {i.status()}") #TODO remove this line when done testing
    print("\nInput Statuses: ") #TODO remove this line when done testing
    for i in inputs: #TODO remove this line when done testing
        print(f"{i.name}: {i.status()}") #TODO remove this line when done testing
    print("\nOutput Statuses: ") #TODO remove this line when done testing
    for i in outputs: #TODO remove this line when done testing
        print(f"{i.name}: {i.status()}") #TODO remove this line when done testing
    print("\nTrouble Input Statuses: ") #TODO remove this line when done testing
    for i in troubleInputs: #TODO remove this line when done testing
        print(f"{i.name}: {i.status()}") #TODO remove this line when done testing

    ## OPEN DOOR
    #runQuery(url, sessionID, params.control, params.doors, doors[3].recID, 1) #TODO remove this line when done testing
    ## OPEN DOOOR

    print("\nUsername: " + secrets.username) #TODO remove this line when done testing
    #print("Password: " + secrets.password) #TODO remove this line when done testing
    print("SessionID: " + sessionID) #TODO remove this line when done testing
    #* END TESTING AREA


if __name__ == '__main__':
    main()