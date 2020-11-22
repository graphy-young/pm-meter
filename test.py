import honeywell_hpma115s0 as hw
import os
import datetime

sensor = hw.Honeywell(port="/dev/serial0", baud=9600)

timestamp, pm10, pm25 = str(sensor.read()).split(',')
print(timestamp)
print(pm10)
print(pm25)
#os.system('echo {timestamp}, {pm10}, {pm25}')
