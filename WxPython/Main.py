from hashlib import sha1  # for hashing the password
import random  # for generating a random session ID
import urllib.request # for making HTTP requests

import Includes.Params as params
import Includes.Secrets as secrets
import Includes.StatusCodeMaps as codeMaps

## GLOBAL VARIABLES ##
SEQUENCE = 0
STATUS_DICT = {}
AREAS = []
DOORS = []
INPUTS = []
OUTPUTS = []
TROUBLE_INPUTS = []

## CLASSES ##
# parent class for input/output objects (areas, doors, inputs, outputs, and trouble inputs) 
class Wx_IO:
    def __init__(self, name, recID, sessid):
        self.name = name
        self.recID = recID
        self.sessid = sessid
        self.url = f"https://{secrets.domain}/PRT_CTRL_DIN_ISAPI.dll?"
    def status(self):
        return STATUS_DICT[self.statusKey]

# subclass for area objects (inherits from wxIO)
class Area(Wx_IO):
    def __init__(self, name, recID, sessid):
        super().__init__(name, recID, sessid)
        self.statusKey = "Area" + str(self.recID)
    def print_Status(self):
        lst = self.status()[:]
        lst[0] = codeMaps.areaStatus1.get(lst[0], lst[0])
        lst[1] = codeMaps.areaStatus2.get(lst[1], lst[1])
        binary_str = bin(lst[2])[2:].rjust(7, '0')
        lst[2] = [codeMaps.areaStatus3.get(i, i) for i in range(len(binary_str)) if binary_str[i] == '1']
        print(f"{self.name}: {self.statusKey}{self.status()} - {lst}")
    def disarm(self):
        run_Query(self.url, self.sessid, params.control, params.areas, self.recID, 0)
    def disarm_24(self):
        run_Query(self.url, self.sessid, params.control, params.areas, self.recID, 1)
    def disarm_All(self):
        run_Query(self.url, self.sessid, params.control, params.areas, self.recID, 2)
    def arm(self):
        run_Query(self.url, self.sessid, params.control, params.areas, self.recID, 3)
    def arm_Force(self):
        run_Query(self.url, self.sessid, params.control, params.areas, self.recID, 4)
    def arm_Instant(self):
        run_Query(self.url, self.sessid, params.control, params.areas, self.recID, 5)
    def arm_Force_Instant(self):
        run_Query(self.url, self.sessid, params.control, params.areas, self.recID, 6)
    def walk_Test_On(self):
        run_Query(self.url, self.sessid, params.control, params.areas, self.recID, 7)
    def walk_Test_Off(self):
        run_Query(self.url, self.sessid, params.control, params.areas, self.recID, 8)
    def silence_Alarm(self):
        run_Query(self.url, self.sessid, params.control, params.areas, self.recID, 9)
    def arm_Stay(self):
        run_Query(self.url, self.sessid, params.control, params.areas, self.recID, 10)
    def arm_24(self):
        run_Query(self.url, self.sessid, params.control, params.areas, self.recID, 11)

# subclass for door objects (inherits from wxIO)
class Door(Wx_IO):
    def __init__(self, name, recID, sessid):
        super().__init__(name, recID, sessid)
        self.statusKey = "Door" + str(self.recID)
    def print_Status(self):
        lst = self.status()[:]
        lst[0] = codeMaps.doorStatus1.get(lst[0], lst[0])
        lst[1] = codeMaps.doorStatus2.get(lst[1], lst[1])
        print(f"{self.name}: {self.statusKey}{self.status()} - {lst}")
    def lock(self):
        run_Query(self.url, self.sessid, params.control, params.doors, self.recID, 0)
    def unlock(self):
        run_Query(self.url, self.sessid, params.control, params.doors, self.recID, 1)
    def unlock_Latched(self):
        run_Query(self.url, self.sessid, params.control, params.doors, self.recID, 2)
    def lockdown_Entry_Allowed(self):
        run_Query(self.url, self.sessid, params.control, params.doors, self.recID, 3)
    def lockdown_Exit_Allowed(self):
        run_Query(self.url, self.sessid, params.control, params.doors, self.recID, 4)
    def lockdown_Entry_Exit_Allowed(self):
        run_Query(self.url, self.sessid, params.control, params.doors, self.recID, 5)
    def lockdown_Clear(self):
        run_Query(self.url, self.sessid, params.control, params.doors, self.recID, 6)
    def cancel_Conditional_Exception(self):
        run_Query(self.url, self.sessid, params.control, params.doors, self.recID, 7)
    def restore_Conditional_Exception(self):
        run_Query(self.url, self.sessid, params.control, params.doors, self.recID, 8)
    def lockdown_Full(self):
        run_Query(self.url, self.sessid, params.control, params.doors, self.recID, 9)

# subclass for input objects (inherits from wxIO)
class Input(Wx_IO):
    def __init__(self, name, recID, sessid):
        super().__init__(name, recID, sessid)
        self.statusKey = "Input" + str(self.recID)
    def print_Status(self):
        lst = self.status()[:]
        lst[0] = codeMaps.inputStatus1.get(lst[0], lst[0])
        binary_str = bin(lst[1])[2:].rjust(3, '0')
        lst[1] = [codeMaps.inputStatus2.get(i, i) for i in range(len(binary_str)) if binary_str[i] == '1']
        print(f"{self.name}: {self.statusKey}{self.status()} - {lst}")
    def remove_Bypass(self):
        run_Query(self.url, self.sessid, params.control, params.inputs, self.recID, 0)
    def bypass_Till_Disarm(self):
        run_Query(self.url, self.sessid, params.control, params.inputs, self.recID, 1)
    def bypass(self):
        run_Query(self.url, self.sessid, params.control, params.inputs, self.recID, 2)

# subclass for output objects (inherits from wxIO)
class Output(Wx_IO):
    def __init__(self, name, recID, sessid):
        super().__init__(name, recID, sessid)
        self.statusKey = "PGM" + str(self.recID)
    def print_Status(self):
        lst = self.status()[:]
        lst[0] = codeMaps.outputStatus1.get(lst[0], lst[0])
        print(f"{self.name}: {self.statusKey}{self.status()} - {lst}")

# subclass for trouble input objects (inherits from wxIO)
class Trouble_Input(Wx_IO):
    def __init__(self, name, recID, sessid):
        super().__init__(name, recID, sessid)
        self.statusKey = "TroubleInput" + str(self.recID)
    def print_Status(self):
        lst = self.status()[:]
        lst[0] = codeMaps.troubleInputStatus1.get(lst[0], lst[0])
        binary_str = bin(lst[1])[2:].rjust(2, '0')
        lst[1] = [codeMaps.troubleInputStatus2.get(i, i) for i in range(len(binary_str)) if binary_str[i] == '1']
        print(f"{self.name}: {self.statusKey}{self.status()} - {lst}")

## FUNCTIONS ##
# generate a random 32 character string
def generate_Session_ID():
    sessid = ""
    for i in range(32):
        tval = format(random.randint(0, 15), 'x')
        sessid += tval.upper()
    return sessid

# run a query against the API using the given login parameters
def run_Login_Query(url, queryParams, sessid):
    queryParams += f"&SessionID={sessid}"
    urlParams = url + queryParams
    response = urllib.request.urlopen(urlParams).read().decode('utf-8')
    return response

# xor a string with a number
def xor_Fn(pswd: str, num: int):
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
    sessid = generate_Session_ID()
    pswdHash = sha1(secrets.password.encode('utf-8')).hexdigest()
    data = run_Login_Query(url, params.init, sessid) # initiate session
    xorUsername = xor_Fn(secrets.username, (int(data) +1))
    hashXorUsername = sha1(xorUsername.encode('utf-8')).hexdigest().upper()
    xorPswdHash = xor_Fn(pswdHash, int(data))
    hashXorPswdHash = sha1(xorPswdHash.encode('utf-8')).hexdigest().upper()
    loginParams = f"{params.login}&Name={hashXorUsername}&Password={hashXorPswdHash}" # build the login parameters
    data = run_Login_Query(url, loginParams, sessid) # login to session
    if data.startswith("FAIL"):
        raise ValueError(f"Login failed with error code {data}")
    SEQUENCE = 0 # reset sequence number
    return sessid

#*TODO run a query against the API using the given parameters and session ID
def run_Query(url, sessid, queryType, subType, recID = None, command = None, data1 = None, data2 = None):
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
    urlParams = url + queryParams
    response = urllib.request.urlopen(urlParams).read().decode('utf-8')
    SEQUENCE += 1 # increment sequence number
    if queryType == params.getList:
        return convert_To_Dict(response)
    return response

# convert a string of key-value pairs to a dictionary
def convert_To_Dict(inputString):
    dictionary = {}
    for item in inputString.split("&"):
        key, value = item.split("=")
        dictionary[int(key)] = value
    return dictionary

# build a dictionary of status codes for areas, doors, inputs, outputs, and trouble inputs
def update_Status_Dict(url, sessid):
    global STATUS_DICT
    areaStatusList = run_Query(url, sessid, params.getStatus, params.areas)
    doorStatusList = run_Query(url, sessid, params.getStatus, params.doors)
    inputStatusList = run_Query(url, sessid, params.getStatus, params.inputs)
    outputStatusList = run_Query(url, sessid, params.getStatus, params.outputs)
    troubleInputStatusList = run_Query(url, sessid, params.getStatus, params.troubleInputs)
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
def build_Object_List(ioList, name, sessid):
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
            value = Trouble_Input(value, key, sessid)
        else:
            raise ValueError("Invalid object type")
        objectList.append(value)
    return objectList

# build Global List of all objects
def build_Global_Object_Lists(url, sessionID):
    global AREAS, DOORS, INPUTS, OUTPUTS, TROUBLE_INPUTS
    AREAS = build_Object_List(run_Query(url, sessionID, params.getList, params.areas), "Area", sessionID)
    DOORS = build_Object_List(run_Query(url, sessionID, params.getList, params.doors), "Door", sessionID)
    INPUTS = build_Object_List(run_Query(url, sessionID, params.getList, params.inputs), "Input", sessionID)
    OUTPUTS = build_Object_List(run_Query(url, sessionID, params.getList, params.outputs), "Output", sessionID)
    TROUBLE_INPUTS = build_Object_List(run_Query(url, sessionID, params.getList, params.troubleInputs), "TroubleInput", sessionID)

# main function
def main():
    url = f"https://{secrets.domain}/PRT_CTRL_DIN_ISAPI.dll?"

    # initiate session and build status dictionary
    sessionID = login(url)
    update_Status_Dict(url, sessionID)

    # build objects
    build_Global_Object_Lists(url, sessionID)

    #* TESTING AREA
    print("\nArea Statuses: ") #TODO remove this line when done testing
    for i in AREAS: #TODO remove this line when done testing
        i.print_Status() #TODO remove this line when done testing
    print("\nDoor Statuses: ") #TODO remove this line when done testing
    for i in DOORS: #TODO remove this line when done testing
        i.print_Status() #TODO remove this line when done testing
    print("\nInput Statuses: ") #TODO remove this line when done testing
    for i in INPUTS: #TODO remove this line when done testing
        i.print_Status() #TODO remove this line when done testing
    print("\nOutput Statuses: ") #TODO remove this line when done testing
    for i in OUTPUTS: #TODO remove this line when done testing
        i.print_Status() #TODO remove this line when done testing
    print("\nTrouble Input Statuses: ") #TODO remove this line when done testing
    for i in TROUBLE_INPUTS: #TODO remove this line when done testing
        i.print_Status() #TODO remove this line when done testing

    ## OPEN DOOR
    DOORS[3].unlock() #TODO remove this line when done testing
    ## OPEN DOOOR

    print("\n") #TODO remove this line when done testing
    #print("Username: " + secrets.username) #TODO remove this line when done testing
    #print("Password: " + secrets.password) #TODO remove this line when done testing
    print(f"SessionID: {sessionID}") #TODO remove this line when done testing
    print(f"Sequence: {SEQUENCE}") #TODO remove this line when done testing
    #* END TESTING AREA


if __name__ == '__main__':
    main()