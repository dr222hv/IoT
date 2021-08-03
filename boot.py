import machine
from network import WLAN
wlan = WLAN()

if machine.reset_cause() != machine.SOFT_RESET:
    wlan.init(mode=WLAN.STA)

if not wlan.isconnected():
    # change the line below to match your network ssid, security and password
    wlan.connect(ssid, auth=(WLAN.WPA2, password))
    while not wlan.isconnected():
        machine.idle() # save power while waiting

print("WIFI connected succesfully")
print(wlan.ifconfig())