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

def getStationCode():
    """
        Get station code using RPi's CPU seiral code
    """
    try:
        connection = pymysql.connect(host=keys.host, port=keys.port, 
                                    user=keys.userName, password=keys.password, 
                                    database=keys.dbName)
        cursor = connection.cursor()

        rpiSerial = getSerial()

        query = f""" 
                    SELECT station_code
                    FROM station_info
                    WHERE serial_code = '{rpiSerial}'
                """
        cursor.execute(query)
        stationCode = cursor.fetchone()[0]
        logger(f"Station code '{stationCode}' Fetched from DB successfully")

    except Exception as e:
        msg = f'Searching station code from DB failed! error: {[str(e)]}'
        logError(e, msg)

    finally:
        connection.close()

    return stationCode

def logError(er, *args):
    
    stationCode = getStationCode()
    updatedTime = str(datetime.now())
    errors = str(er)
    errorData = f'{stationCode}, {updatedTime}, 2, {errors}'
    escapeMessage = str(' '.join(args))

    try:
        connection = pymysql.connect(host=keys.host, port=keys.port, 
                                    user=keys.userName, password=keys.password, 
                                    database=keys.dbName)
        cursor = connection.cursor()

        eFileName = 'error.csv'
        eTableName = 'command_log'
        eColumnList = ['station_code', 'executed_time', 'file_descriptor', 'command']
        eColumnList = ', '.join(eColumnList)

        if os.path.isfile(eFileName):
            logger('Found previous log that could not be saved properly to DB server. Try again to save those...')

            errorFile = pd.read_csv(eFileName, encoding='utf-8', header=None)
            errorFile = list(errorFile.to_records(index=False))

            query = f"""
                        INSERT INTO {eTableName} ({eColumnList}) 
                        VALUES (%s, %s, %s, %s);
                    """
            cursor.executemany(query, errorFile)
            connection.commit()

            if int(cursor.rowcount) > 1:
                messageVerb = 'were'
            else:
                messageVerb = 'was'
            logger('Previous', str(cursor.rowcount), 'log', messageVerb, 'inserted.')
        query = f"""
                    INSERT INTO device_log (station_code, updated_time, file_descriptor, command) 
                    VALUES ({stationCode}, {updatedTime}, 2, {errors})
                """
        cursor.execute(query)
        connection.commit()

    except Exception as e:
        errorData = f'{stationCode}, {updatedTime}, 2, {e}'

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
    # Connect to Honeywell HPMA115S0-XXX 
    try:
        sensor = hw.Honeywell(port="/dev/serial0", baud=9600)
        logger('Connection to sensor established successfully')

    except Exception as e:
        msg = ('Sensor communication failed! ERROR: ' + str(e))
        logError(e, msg)


    # Sync device's time via remote time server
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
        mColumnList = ('station_code', 'measured_time', 'pm10', 'pm25')
        mColumnList = ', '.join(mColumnList)

        if os.path.isfile(mFileName):
            logger(f'Found previous measurements that could not be sent properly to DB server. Try again to save those...')
            measurementFile = pd.read_csv(mFileName, encoding='utf-8', header=None)
            measurementFile = list(measurementFile.to_records(index=False))
            query = 'INSERT INTO `' + mTableName + f"""` ({mColumnList})
                       VALUES (%s, %s, %s, %s);"""
            cursor.executemany(query, measurementFile)
            connection.commit()
            if int(cursor.rowcount) > 1:
                messageVerb = 'were'
            else:
                messageVerb = 'was'
            logger('Previous', str(cursor.rowcount), 'measurement', messageVerb, 'inserted.')

        query = f"""
                    INSERT INTO {mTableName} ({mColumnList})
                    VALUES ('{getStationCode()}', '{str(datetime.now())}'', {pm10}, {pm25});
                """
        cursor.execute(query)
        connection.commit()
        logger('Sending measurement process ended successfuly!')

    except Exception as e:
        logError(e, 'Sending measurements failed! ERROR: ' + str(e))

    finally:
        connection.close()