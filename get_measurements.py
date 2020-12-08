''' Module import '''
import honeywell_hpma115s0 as hw
import os, sys, datetime
import pymysql, keys
import pandas as pd
from datetime import datetime

''' function definition  '''

def logger(self, *args):
    """
    All parameters should be on string-type!
    """
    print('[' + str(datetime.now()) + ']', str(' '.join(args)))

def logError(stationCode, er, escapeMessage):

        station_code = stationCode
        update_at = str(datetime.now())
        errors = str(er)
        errorData = '{station_code}, {update_at}, 2, {errors}'

    with open('error.csv', 'a') as f:
        if os.path.isfile('error.csv'):
            f.write('\n')
        else:
            pass
        f.write(errorData)
    
    logger(escapeMessage)
    from sys import exit
    exit()

# Connect to Honeywell HPMA115S0-XXX sensor
try:

    sensor = hw.Honeywell(port="/dev/serial0", baud=9600)

except Exception as e:

    logError(1, e, ('Sensor communication failed! ERROR: ' + str(e)))

logger('Connection to sensor established successfully')

# Get datetime & pollution data from the sensor
try:
    measuredDateime, pm10, pm25 = str(sensor.read()).split(',')
except Exception as e:
    escape('Getting data from sensor failed. ERROR:', e)
logger('measuredDatetime: {measuredDatetime}, PM10: {PM10}, PM2.5: {PM25}')
os.system('echo {measuredTime}, {pm10}, {pm25}')


''' Codes '''
if __name__ == "__main__":
    fileName = 'measurements.csv'
    if os.path.isfile(fileName):
        try:
            df = pd.read_csv(fileName, encoding='utf-8')
        except UnicodeDecodeError:
            df = pd.read_csv(fileName, encoding='cp949')