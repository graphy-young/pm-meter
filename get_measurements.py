''' Module import '''
import honeywell_hpma115s0 as hw
import pymysql
import keys
import pandas as pd
from os import system
from os.path import isfile
from datetime import datetime


''' function definition  '''
def logger(*args):
    """
        Print log message with excecuting file name, timestamp.
        *** All parameters should be on string-type!
    """
    message = f"[{__file__} {str(datetime.now())}] {str(' '.join(args))}"
    print(message)

######### 나중에 추가하기
def dbLogger(*args):
    connectDB()

def getSerial():
  """ 
    Extract serial from /proc/cpuinfo file what RPi OS having in itself
    This works only Rasberry Pi OS(former named Raspbian)
  """
  cpuSerial = "0000000000000000" # 16 bytes

  try:
    f = open('/proc/cpuinfo','r') # Read Raspberry Pi's hardware info

    for line in f:
      if line[0:6]=='Serial': 
          cpuSerial = line[10:26]
    f.close()

  except Exception as e:
    msg = f"Getting Serial code from RPi failed! ERROR: : {[str(e)]}"
    logError(e, msg)
    #cpuSerial = "UNKNOWN_SERIAL0"

  return cpuSerial

def syncTime():
    """ 
        Sync device's time via remote time server
    """
    try:
        system('sudo rdate -s time.bora.net')
        logger('System time sync got successful')

    except Exception as e:
        msg = (f'time sync got failed! ERROR: {str(e)}')
        logError(e, msg)

def connectDB():
    """
       Connect to MySQL database server, returning connection & cursor objects. 
    """
    try:
        connection = pymysql.connect(host=keys.host, port=keys.port, 
                                    user=keys.userName, password=keys.password, 
                                    database=keys.dbName)
        cursor = connection.cursor()
        logger('DB connection Established.')
        return connection, cursor
    except Exception as e:
        msg = (f'DB connection failed! ERROR: {str(e)}')
        logError(e, msg)

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

        query = f"SELECT station_code FROM station_info WHERE serial_code = '{rpiSerial}';"
        cursor.execute(query)
        stationCode = cursor.fetchone()[0]
        logger(f"Station code '{stationCode}' Fetched from DB successfully")

    except Exception as e:
        msg = f'Searching station code from DB failed! ERROR: {[str(e)]}'
        logError(e, msg)

    finally:
        connection.close()

    return stationCode

"""def convertEscape(targetText):
    escapeDict = {"'": "\'", '"': '\"', "\": '''\\''', 
                    "%": "\%", "_": '\_'}
    transTable = targetText.maketrans(escapeDict)
    translatedText = targetText.translate(transTable)
    return translatedText"""

def logError(er, *args):
    
    station_code = getStationCode()
    execution_time = str(datetime.now())
    errors = str(er)
    escapeMessage = str(' '.join(args))

    try:
        connection, cursor = connectDB()

        eFileName = 'error.csv'
        eTableName = 'command_log'
        eColumnList = ['station_code', 'execution_time', 'file_descriptor', 'command']

        if isfile(eFileName):
            logger('Found previous log that could not be saved properly to DB server. Try again to save those...')
            errorFile = pd.read_csv(eFileName, encoding='utf-8', names=eColumnList, delimiter="\t")
            errorFile = errorFile.astype({'station_code': 'str'})
            # When pandas reads csv without any dtype parameter, it reads station code under 10 as integer 0, not '00'.
            errorFile['station_code'] = errorFile['station_code'].apply(lambda x: '0'+str(x) if int(x) < 10 else x)
            errorFile = list(errorFile.values.tolist())
            for row in errorFile:
                row[3] = connection.escape_string(row[3])
            query = f"INSERT INTO {eTableName} ({', '.join(eColumnList)}) VALUES (%s, %s, %s, %s);"
            cursor.executemany(query, errorFile)
            connection.commit()
            if int(cursor.rowcount) > 1:
                messageVerb = 'were'
            else:
                messageVerb = 'was'
            logger('Previous', str(cursor.rowcount), 'log', messageVerb, 'inserted.')
            system(f'rm -rf {eFileName}')
            logger('error.csv deleted.')
        query = f"INSERT INTO {eTableName} ({', '.join(eColumnList)}) VALUES ('{station_code}', '{execution_time}', 2, '{connection.escape_string(errors)}');"
                
        cursor.execute(query)
        connection.commit()
        logger(f"Error data '{station_code}', {execution_time}, 2, {errors} insertion success.")

    except Exception as e:
        logger(f'Error logging process failed due to ERROR: {str(e)}')
        with open(eFileName, 'a', encoding='utf8') as f:
            if isfile(eFileName):
                f.write('\n')
            f.write(f'{station_code}\t{execution_time}\t2\t{errors}')
        logger(f"Error data '{station_code}', {execution_time}, 2, {errors} saved locally in {eFileName}")

    finally:
        connection.close()
        logger('Connection closed. Sending error process ended.')

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

    syncTime()

    # Get datetime & pollution data from the sensor
    try:
        measured_time, pm10, pm25 = str(sensor.read()).split(',')
        logger(f'[DATA] measured_time: {measured_time}, PM10: {pm10}, PM25: {pm25}')

    except Exception as e:
        msg = 'Getting data from sensor failed. ERROR:' + str(e)
        logError(str(e), msg)


    try:
        connection, cursor = connectDB()

        station_code = getStationCode()

        mFileName = 'measurements.csv'
        mTableName = 'air_quality'
        mColumnList = ['station_code', 'measured_time', 'pm10', 'pm25']

        if isfile(mFileName):
            logger(f'Found previous measurements that could not be sent properly to DB server. Try again to save those...')
            measurementFile = pd.read_csv(mFileName, encoding='utf-8', names=mColumnList)
            measurementFile = measurementFile.astype({'station_code': 'str'})
            measurementFile['station_code'] = measurementFile['station_code'].apply(lambda x: '0'+str(x) if int(x) < 10 else x)
            measurementFile = list(measurementFile.values.tolist())
            query = f"INSERT INTO `{mTableName}` ({', '.join(mColumnList)}) VALUES (%s, %s, %s, %s);"
            cursor.executemany(query, measurementFile)
            connection.commit()
            if int(cursor.rowcount) > 1:
                messageVerb = 'were'
            else:
                messageVerb = 'was'
            logger('Previous', str(cursor.rowcount), 'measurement', messageVerb, 'inserted.')
            system(f'rm -rf {mFileName}')
            logger(f'{mFileName} deleted. Continue to next step!')

        query = f"INSERT INTO {mTableName} ({', '.join(mColumnList)}) VALUES ('{station_code}', '{measured_time}', {pm10}, {pm25});"
        cursor.execute(query)
        connection.commit()
        logger(f"'{station_code}', {measured_time}, {pm10}, {pm25} inserted.")


    except Exception as e:
        logError(e, 'Sending measurements failed! ERROR: ' + str(e))
        # Save measurement to local drive when error occurs
        with open(mFileName, 'a', encoding='utf-8') as f:
            if isfile(mFileName):
                f.write('\n')
            f.write(','.join([station_code, measured_time, pm10, pm25]))

    finally:
        connection.close()
        logger('Sending measurements process ended successfuly! Connection closed.')