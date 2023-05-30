from hashlib import sha1  # for hashing the password
import random  # for generating a random session ID
import urllib.request # for making HTTP requests

import Includes.Params as params
import Includes.Secrets as secrets
import Includes.StatusCodeMaps as codeMaps

## GLOBAL VARIABLES ##
SEQUENCE = 0
STATUS_DICT = {}

## CLASSES ##
# class for input/output objects (areas, doors, inputs, outputs, and trouble inputs)
class WxIO:
    def __init__(self, name, recID, sessid):
        self.name = name
        self.recID = recID
        self.statusKey = None
        self.sessid = sessid
        self.url = f"https://{secrets.domain}/PRT_CTRL_DIN_ISAPI.dll?"
    def status(self):
        return STATUS_DICT[self.statusKey]

# class for area objects (inherits from wxIO)
class Area(WxIO):
    def __init__(self, name, recID, sessid):
        super().__init__(name, recID, sessid)
        self.statusKey = "Area" + str(self.recID)
    def printStatus(self):
        lst = self.status()[:]
        lst[0] = codeMaps.areaStatus1.get(lst[0], lst[0])
        lst[1] = codeMaps.areaStatus2.get(lst[1], lst[1])
        binary_str = bin(lst[2])[2:].rjust(7, '0')
        lst[2] = [codeMaps.areaStatus3.get(i, i) for i in range(len(binary_str)) if binary_str[i] == '1']
        print(f"{self.name}: {self.statusKey}{self.status()} - {lst}")

# class for door objects (inherits from wxIO)
class Door(WxIO):
    def __init__(self, name, recID, sessid):
        super().__init__(name, recID, sessid)
        self.statusKey = "Door" + str(self.recID)
    def printStatus(self):
        lst = self.status()[:]
        lst[0] = codeMaps.doorStatus1.get(lst[0], lst[0])
        lst[1] = codeMaps.doorStatus2.get(lst[1], lst[1])
        print(f"{self.name}: {self.statusKey}{self.status()} - {lst}")
    def unlock(self):
        runQuery(self.url, self.sessid, params.control, params.doors, self.recID, 1)

# class for input objects (inherits from wxIO)
class Input(WxIO):
    def __init__(self, name, recID, sessid):
        super().__init__(name, recID, sessid)
        self.statusKey = "Input" + str(self.recID)
    def printStatus(self):
        lst = self.status()[:]
        lst[0] = codeMaps.inputStatus1.get(lst[0], lst[0])
        binary_str = bin(lst[1])[2:].rjust(3, '0')
        lst[1] = [codeMaps.inputStatus2.get(i, i) for i in range(len(binary_str)) if binary_str[i] == '1']
        print(f"{self.name}: {self.statusKey}{self.status()} - {lst}")

# class for output objects (inherits from wxIO)
class Output(WxIO):
    def __init__(self, name, recID, sessid):
        super().__init__(name, recID, sessid)
        self.statusKey = "PGM" + str(self.recID)
    def printStatus(self):
        lst = self.status()[:]
        lst[0] = codeMaps.outputStatus1.get(lst[0], lst[0])
        print(f"{self.name}: {self.statusKey}{self.status()} - {lst}")

# class for trouble input objects (inherits from wxIO)
class TroubleInput(WxIO):
    def __init__(self, name, recID, sessid):
        super().__init__(name, recID, sessid)
        self.statusKey = "TroubleInput" + str(self.recID)
    def printStatus(self):
        lst = self.status()[:]
        lst[0] = codeMaps.troubleInputStatus1.get(lst[0], lst[0])
        binary_str = bin(lst[1])[2:].rjust(3, '0')
        lst[1] = [codeMaps.troubleInputStatus2.get(i, i) for i in range(len(binary_str)) if binary_str[i] == '1']
        print(f"{self.name}: {self.statusKey}{self.status()} - {lst}")

## FUNCTIONS ##
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

# build a dictionary of status codes for areas, doors, inputs, outputs, and trouble inputs
def updateStatusDict(url, sessid):
    global STATUS_DICT
    areaStatusList = runQuery(url, sessid, params.getStatus, params.areas)
    doorStatusList = runQuery(url, sessid, params.getStatus, params.doors)
    inputStatusList = runQuery(url, sessid, params.getStatus, params.inputs)
    outputStatusList = runQuery(url, sessid, params.getStatus, params.outputs)
    troubleInputStatusList = runQuery(url, sessid, params.getStatus, params.troubleInputs)
    for i, lst in enumerate([areaStatusList, doorStatusList, inputStatusList, outputStatusList, troubleInputStatusList]):
        tempDict = {}
        statusList = lst.split('&')
        for status in statusList:
            name, values = status.split('=')
            if name in STATUS_DICT:
                STATUS_DICT[name] = list(map(int, values.split(',')))
            else:
                tempDict[name] = list(map(int, values.split(',')))
        STATUS_DICT.update(tempDict)

# build a dictionary of objects from a dictionary of key-value pairs
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

# main function
def main():
    url = f"https://{secrets.domain}/PRT_CTRL_DIN_ISAPI.dll?"

    # initiate session and build status dictionary
    sessionID = login(url)
    updateStatusDict(url, sessionID)

    # build objects
    areas = buildObjectList(runQuery(url, sessionID, params.getList, params.areas), "Area", sessionID)
    doors = buildObjectList(runQuery(url, sessionID, params.getList, params.doors), "Door", sessionID)
    inputs = buildObjectList(runQuery(url, sessionID, params.getList, params.inputs), "Input", sessionID)
    outputs = buildObjectList(runQuery(url, sessionID, params.getList, params.outputs), "Output", sessionID)
    troubleInputs = buildObjectList(runQuery(url, sessionID, params.getList, params.troubleInputs), "TroubleInput", sessionID)

    #* TESTING AREA
    print("\nArea Statuses: ") #TODO remove this line when done testing
    for i in areas: #TODO remove this line when done testing
        i.printStatus() #TODO remove this line when done testing
    print("\nDoor Statuses: ") #TODO remove this line when done testing
    for i in doors: #TODO remove this line when done testing
        i.printStatus() #TODO remove this line when done testing
    print("\nInput Statuses: ") #TODO remove this line when done testing
    for i in inputs: #TODO remove this line when done testing
        i.printStatus() #TODO remove this line when done testing
    print("\nOutput Statuses: ") #TODO remove this line when done testing
    for i in outputs: #TODO remove this line when done testing
        i.printStatus() #TODO remove this line when done testing
    print("\nTrouble Input Statuses: ") #TODO remove this line when done testing
    for i in troubleInputs: #TODO remove this line when done testing
        i.printStatus() #TODO remove this line when done testing

    ## OPEN DOOR
    #doors[3].unlock() #TODO remove this line when done testing
    ## OPEN DOOOR

    print("\n") #TODO remove this line when done testing
    #print("Username: " + secrets.username) #TODO remove this line when done testing
    #print("Password: " + secrets.password) #TODO remove this line when done testing
    print("SessionID: " + sessionID) #TODO remove this line when done testing
    #* END TESTING AREA


if __name__ == '__main__':
    main()