import honeywell_hpma115s0 as hw
import os

sensor = hw.Honeywell(port="/dev/serial0", baud=9600)

try:
    timestamp, pm10, pm25 = sensor.read()
    #print(data)
    os.system('echo {timestamp}, {pm10}, {pm25}')
    
except:
        print('error occured')