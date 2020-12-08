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

    stationCode = str(stationCode)
    updated_at = str(datetime.now())
    errors = str(er)
    errorData = '{station_code}, {updated_at}, 2, {errors}'

    try:
        connection = pymysql.connect(host=keys.host, port=keys.port, 
                                user=keys.userName, password=keys.password, 
                                database=keys.dbName)
        cursor = connection.cursor()
        if os.path.isfile('error.csv'):
            errorFile = pd.read_csv('error.csv', encoding='utf-8')
            # DataFrame to MySQL server 기능넣기
        query = """INSERT INTO device_log (stationCode, updated_at, file_descriptor, command) 
                    VALUES ({stationCode}, {updated_at}, 2, {errors})"""
        cursor.execute(query)
        connection.commit()
    except Exception as e:
        with open('error.csv', 'a', encoding='utf8') as f:
            if os.path.isfile('error.csv'):
                f.write('\n')
            else:
                pass
            f.write(errorData)
    finally:
        connection.close()

    logger(escapeMessage)
    from sys import exit
    exit()

# Connect to Honeywell HPMA115S0-XXX sensor
try:
    sensor = hw.Honeywell(port="/dev/serial0", baud=9600)
except Exception as e:
    msg = ('Sensor communication failed! ERROR: ' + str(e))
    logError('1', e, msg)
logger('Connection to sensor established successfully')


# Get datetime & pollution data from the sensor
try:
    measuredDateime, pm10, pm25 = str(sensor.read()).split(',')
except Exception as e:
    msg = 'Getting data from sensor failed. ERROR:' + str(e)
    logError('1', str(e), msg)
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