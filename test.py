import honeywell_hpma115s0 as hw
import os

sensor = hw.Honeywell(port="/dev/serial0", baud=9600)

try:
    data = sensor.read()
    print(data)
except:
        print('error occured')
