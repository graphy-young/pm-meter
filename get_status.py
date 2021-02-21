''' Module import '''
from modules import x750ups
import keys
import re
import pymysql
import pandas as pd
from get_measurements import logger, logError, getSerial, connectDB, syncTime, getStationCode
from datetime import datetime
from os import popen, system
from os.path import isfile
from gpiozero import CPUTemperature


''' Codes '''
if __name__ == "__main__":
    
    syncTime()

    try:
        connection, cursor = connectDB()

        station_code = getStationCode()
        device_time = str(datetime.now())
        battery_voltage = x750ups.readVoltage(x750ups.bus)
        battery_capacity = x750ups.readCapacity(x750ups.bus)
        wirelessInfo = popen("iwconfig wlan0 | awk '{$1=$1;print}'").read().split('\n')
        ssid = re.search('ESSID:"+(\w)+"', wirelessInfo[0]).group(0)[7:-1]
        link_quality = int(re.search('Link Quality=+\d\d+/+\d\d', wirelessInfo[5]).group(0)[13:].split('/')[0])
        signal_level = int(re.search('Signal level=-+\d+ dBm', wirelessInfo[5]).group(0)[13:-4])
        stored_data = 0
        cpu_temperature = CPUTemperature().temperature # NOTE) RPi CPU 온도 읽기
        rtc_temperature = float(0) # NOTE) RTC 모듈 온도센서에서 온도 읽기

        sFileName = 'status.csv'
        sTableName = 'device_status'
        sColumnList = ['station_code', 'device_time', 'battery_voltage', 'battery_capacity', 'ssid', 
                        'link_quality', 'signal_level', 'stored_data', 'cpu_temperature', 'rtc_temperature']
        
        if isfile(sFileName):
            logger('Found previous status that could not be stored to DB server. Try again to save those...')
            statusFile = pd.read_csv(sFileName, encoding='utf-8', names=sColumnList)
            statusFile = statusFile.astype({'station_code': 'str'})
            statusFile['station_code'] = statusFile['station_code'].apply(lambda x: '0'+str(x) if int(x) < 10 else x)
            stored_data = len(statusFile)
            statusFile = list(statusFile.values.tolist())
            query = f"INSERT INTO `{sTableName}` ({', '.join(sColumnList)}) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
            cursor.executemany(query, statusFile)
            connection.commit()
            if int(cursor.rowcount) > 1:
                messageVerb = 'were'
            else:
                messageVerb = 'was'
            logger('Previous', str(cursor.rowcount), 'status file', messageVerb, 'inserted.')
            system(f'rm -rf {sFileName}')
            logger(f'{sFileName} deleted.')
        query = f"""INSERT INTO {sTableName} ({', '.join(sColumnList)})
                    VALUES ('{station_code}', '{device_time}', {battery_voltage}, {battery_capacity}, '{ssid}', {link_quality}, {signal_level}, {stored_data}, {cpu_temperature}, {rtc_temperature})"""
        cursor.execute(query)
        connection.commit()
        logger(f"status data '{station_code}', '{device_time}', {battery_voltage}, {battery_capacity}, '{ssid}', {link_quality}, {signal_level}, {stored_data}, {cpu_temperature}, {rtc_temperature} inserted.")

    except Exception as e:
        if isfile(sFileName):
            sFileFlag = True
        else:
            sFileFlag = False
        with open(sFileName, 'a', encoding='utf-8') as f:
            if sFileFlag:
                f.write('\n')
            f.write(','.join([str(eval(col)) for col in sColumnList]))
        logger('Status data saved in locally for error while sending data')
        logError(e, 'Sending status failed! ERROR: ' + str(e))

    finally:
        connection.close()
        logger('Connection closed. Quit this module..')