
## Area Status Code Maps
# Status 1 (Area 24hr Status)
alarmStatus1 = {
    0: "24hr Disabled",
    1: "24hr Busy",
    128: "24hr Enabled"
}
# Status 2 (Area Status)
alarmStatus2 = {
    0: "Disarmed", 
    1: "Zone(s) Open Waiting for User",
    2: "Trouble Condition Waiting for User", 
    3: "Bypass Error Waiting for User",
    4: "Bypass Warning Waiting for User",
    5: "User Count Not Zero Waiting for User",
    6: "Unknown",
    127: "Unknown",
    128: "Armed",
    129: "Exit Delay",
    130: "Entry Delay",
    131: "Disarm Delay",
    132: "Code Delay"
}
# Status 3 (Area Notification Bits)
alarmStatus3 = {
    0: "Alarm Activated",
    1: "Siren ACtivated",
    2: "Alarms In Memory",
    3: "Remote Armed",
    4: "Force Armed",
    5: "Instant Armed",
    6: "Partial Armed"
}

## Door Status Code Maps
# Status 1 (Door Lock Status)
doorStatus1 = {
    0: "Locked",
    1: "Unlocked by User",
    2: "Unlocked by Schedule",
    3: "Unlocked by User (Timed)",
    4: "Unlocked by User (Latched)",
    5: "Unlocked by Exit Device",
    6: "Unlocked by Entry Device",
    7: "Unlocked by Operator",
    8: "Unlocked by Operator (Timed)",
    9: "Unlocked by Operator (Latched)",
    10: "Unlocked by Area",
    11: "Unlocked by Fire Alarm",
    12: "Unlocked by Conditional Exception",
    14: "Unlocked By User Using Extended Door Time",
    15: "Unlocked By Exit Device Using Extended Door Time",
    16: "Unlocked By Entry Device Using Extended Door Time",
    17: "Unlocked By Operator Using Extended Door Time",
    18: "Locked Using Extended Door Time",
    19: "Locked down (Entry allowed)",
    20: "Locked down (Exit allowed)",
    21: "Locked down (Entry/ Exit allowed)",
    22: "Locked down (full lockdown)",
    23: "Not Locked (in the locked state but not secure)",
    24: "Not Locked conditional (in the locked state but not secure, with a calendar action active)"
}
# Status 2 (Door Position Status)
doorStatus2 = {
    0: "Closed",
    1: "Open",
    2: "Open Alert",
    3: "Left Open",
    4: "Forced Open",
    5: "Bonding Fault"
}

## Input Status Code Maps
# Status 1 (Input Status)
inputStatus1 = {
    0: "Closed / Off",
    1: "Open / On",
    2: "Tamper",
    3: "Short Circuit"
}
# Status 2 (Input Flags)
inputStatus2 = {
    0: "Input Bypassed",
    1: "Input Bypassed (Latched)",
    2: "Siren Lockout"
}
#inputStatus2 = {
#    0: "",
#    1: "Input Bypassed",
#    2: "Siren Lockout",
#    3: "Input Bypassed (Latched)"
#}