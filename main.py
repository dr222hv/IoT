#My first project
import time
import machine
from machine import ADC
from machine import Pin
from dht import DHT
import pycom

#pin for DHT11
th = DHT(Pin('P23', mode=Pin.OPEN_DRAIN))

#pins for leds and an array with all of them
led_red = Pin('P22', mode=Pin.OUT, pull=Pin.PULL_UP) 
led_yellow = Pin('P21', mode=Pin.OUT, pull=Pin.PULL_UP) 
led_green = Pin('P20', mode=Pin.OUT, pull=Pin.PULL_UP) 
leds = [led_green, led_yellow, led_red] #only for convenience

#pins, read, for the moisture sensor. Add more as needed
ao_pins = ['P18'] #valid pins are P13-P20
for p in ao_pins:
    set = Pin(p, mode=Pin.IN)

#power to the moisture sensor
vcc_pins = ['P4']

time.sleep(2)

#get data from DHT11
def read_env_data(res):
    result = th.read()
    while not result.is_valid():
        time.sleep(0.5)
        result = th.read()
    #add these values to the res list
    res.append(result.temperature)
    res.append(result.humidity)

#get data from soil moisture sensor using pin p_in for data and p_out for power
def measure_soil(p_in, p_out):
    adc = ADC(bits=12) #bits = 12 => value 0-4095
    a_pin = adc.channel(pin=p_in, attn=ADC.ATTN_11DB)
    p_out = Pin(p_out, mode=Pin.OUT, pull=Pin.PULL_DOWN)
    p_out.value(1)
    time.sleep(2)
    volts = a_pin.value()
    p_out.value(0)
    return volts

def fetch_all_soil_moisture(res):
    #fetch values from soil moisture sensors
    for ao, vcc in zip(ao_pins, vcc_pins):    #loop over every pair of pins (data, power) for the soil moisture sensors
        sum = 0
        soil = 0
        for j in range(0,10):   #measure 10 times and calculate mean    
            sum += measure_soil(ao, vcc)
        soil = sum/10

        if machine.wake_reason()[0] == machine.PWRON_WAKE: # if woken by button or power on, we want to signal the moisture via the LEDs
        #Whether 1000-1999 is a reasonable level I so far do not know. Worth calibrating in the future.
            if soil < 1000:
                led_yellow.value(1)
            elif soil < 2000:
                led_green.value(1)
            else:
                led_red.value(1)
            time.sleep(10)
            #shut down the leds
            for led in leds:
                led.value(0)
        res.append(int(soil))      #add the mean to the result list. int since decimals don't matter
        time.sleep(2)

def main():
    res = [] #create a list for sensor data
    #fetch temperature and relative humidity from DHT11
    read_env_data(res)
   
    #fetch values from soil moisture sensors
    fetch_all_soil_moisture(res)

    counter = 1
    for i in res:
        print(counter, i)
        pybytes.send_signal(counter, i)
        counter = counter + 1
        time.sleep(1)
    time.sleep(2)

main()

machine.deepsleep(1000*60*20) #sleep for 20 minutes