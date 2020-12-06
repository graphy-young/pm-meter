''' Module import '''
import honeywell_hpma115s0 as hw
import os, sys, datetime
import pymysql, keys
import pandas as pd



''' function definition  '''
def logger(*args): 
    """
    All parameters should be on string-type!
    """
    from datetime import datetime
    print('[' + str(datetime.now()) + ']', str(' '.join(args)))

def escape(*args):
    logger(*args)
    from sys import exit
    exit()


# Connect to Honeywell HPMA115S0-XXX sensor
try:
    sensor = hw.Honeywell(port="/dev/serial0", baud=9600)
    logger('Connection to sensor established successfully')
except Exception as e:
    escape('Sensor communication failed! ERROR:', str(e))
    

# Get datetime & pollution data from the sensor
try:
    measuredDateime, pm10, pm25 = str(sensor.read()).split(',')
    logger('measuredDatetime: {measuredDatetime}, PM10: {PM10}, PM2.5: {PM25}')
    os.system('echo {measuredTime}, {pm10}, {pm25}')
except Exception as e:
    escape('Getting data from sensor failed. ERROR:', e)


# Database server connection
# need 'keys.py' in same directory
mysql = pymysql.connect(
    host=keys.host, 
    port=keys.port, 
    user=keys.user, 
    password=keys.password, 
    database=keys.dbname)
cursor = mysql.cursor()



''' Codes '''
if __name__ == "__main__":
    fileName = 'measurements.csv'
    if os.path.isfile(fileName):
        try:
            df = pd.read_csv(fileName, encoding='utf-8')
        except UnicodeDecodeError:
            df = pd.read_csv(fileName, encoding='cp949')