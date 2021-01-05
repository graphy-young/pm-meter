''' Module import '''
import honeywell_hpma115s0 as hw
import os, sys, datetime
import pymysql
import keys
import pandas as pd
from datetime import datetime


''' function definition  '''
def logger(*args):
    """
        All parameters should be on string-type!
    """
    message = '[' + str(datetime.now()) + '] ' + str(' '.join(args))
    #os.system(f'echo {message}')
    print(message)

def getSerial():
  """ 
    Extract serial from cpuinfo file
  """
  cpuSerial = "0000000000000000" # 16 bytes
  try:
    f = open('/proc/cpuinfo','r')
    for line in f:
      if line[0:6]=='Serial':
        cpuSerial = line[10:26]
    f.close()
  except:
    cpuSerial = "UNKNOWN_SERIAL0"
  return cpuSerial

def logError(er, *args):
    stationCode = getSerial()
    updatedAt = str(datetime.now())
    errors = str(er)
    errorData = f'{stationCode}, {updatedAt}, 2, {errors}'
    escapeMessage = str(' '.join(args))
    try:
        connection = pymysql.connect(host=keys.host, port=keys.port, 
                                    user=keys.userName, password=keys.password, 
                                    database=keys.dbName)
        cursor = connection.cursor()
        eFileName = 'error.csv'
        if os.path.isfile(eFileName):
            logger('Found previous log that could not be saved properly to DB server. Try again to save those...')
            errorFile = pd.read_csv(eFileName, encoding='utf-8', header=None)
            errorFile = list(errorFile.to_records(index=False))
            query = """INSERT INTO device_log (stationCode, updated_at, file_descriptor, command) 
                        VALUES (%s, %s, %s, %s)"""
            cursor.executemany(query, errorFile)
            connection.commit()
            if int(cursor.rowcount) > 1:
                messageVerb = 'were'
            else:
                messageVerb = 'was'
            logger('Previous', str(cursor.rowcount), 'log', messageVerb, 'inserted.')
        query = f"""INSERT INTO device_log (stationCode, updated_at, file_descriptor, command) 
                    VALUES ({stationCode}, {updatedAt}, 2, {errors})"""
        cursor.execute(query)
        connection.commit()
    except Exception as e:
        errorData = f'{stationCode}, {updatedAt}, 2, {e}'
        with open(eFileName, 'a', encoding='utf8') as f:
            if os.path.isfile(eFileName):
                f.write('\n')
            f.write(errorData)
    finally:
        connection.close()
    logger(escapeMessage)
    from sys import exit
    exit()



""" Codes """
if __name__ == "__main__":
    # Connect to Honeywell HPMA115S0-XXX sensor
    try:
        sensor = hw.Honeywell(port="/dev/serial0", baud=9600)
        logger('Connection to sensor established successfully')
    except Exception as e:
        msg = ('Sensor communication failed! ERROR: ' + str(e))
        logError(e, msg)

    try:
        os.system('sudo rdate -s time.bora.net')
        logger('System time sync got successful')
    except Exception as e:
        msg = ('time sync got failed! Error: ' + str(e))
        logError(e, msg)

    # Get datetime & pollution data from the sensor
    try:
        measuredDatetime, pm10, pm25 = str(sensor.read()).split(',')
        logger(f'[DATA] measuredDatetime: {measuredDatetime}, PM10: {pm10}, PM25: {pm25}')
    except Exception as e:
        msg = 'Getting data from sensor failed. ERROR:' + str(e)
        logError(str(e), msg)

    try:
        connection = pymysql.connect(host=keys.host, port=keys.port, 
                                    user=keys.userName, password=keys.password, 
                                    database=keys.dbName)
        cursor = connection.cursor()
        mFileName = 'measurements.csv'
        mTableName = 'air_quality'
        if os.path.isfile(mFileName):
            logger(f'Found previous {mTableName} that could not be sent properly to DB server. Try again to save those...')
            measurementFile = pd.read_csv(mFileName, encoding='utf-8', header=None)
            measurementFile = list(measurementFile.to_records(index=False))
            query = 'INSERT INTO `' + mTableName + """` (stationCode, measuredDatetime, pm10, pm25) 
                       VALUES (%s, %s, %s, %s)"""
            cursor.executemany(query, measurementFile)
            connection.commit()
            if int(cursor.rowcount) > 1:
                messageVerb = 'were'
            else:
                messageVerb = 'was'
            logger('Previous', str(cursor.rowcount), 'measurement', messageVerb, 'inserted.')
        query = f"""INSERT INTO {mTableName} (stationCode, measuredDatetime, pm10, pm25)
                    VALUES ({getSerial()}, {str(datetime.now())}, {pm10}, {pm25})"""
        cursor.execute(query)
        connection.commit()
    except Exception as e:
        logError(e, 'Sending measurements failed! ERROR: ' + str(e))
    finally:
        connection.close()

    fileName = 'measurements.csv'
    if os.path.isfile(fileName):
        try:
            df = pd.read_csv(fileName, encoding='utf-8')
        except UnicodeDecodeError:
            df = pd.read_csv(fileName, encoding='cp949')