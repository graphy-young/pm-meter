import honeywell_hpma115s0 as hw
import os

a = hw.Honeywell(port="/dev/serial0", baud=9600)

try:
    data = a.read()
    print(data)
except:
        print('error')
