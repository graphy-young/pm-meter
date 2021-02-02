import x750ups
import keys
import re
import pymysql
import pandas as pd
from get_measurements import logger, logError, getSerial, connectDB
from datetime import datetime
from os import popen
from os.path import isfile

stationCode = getSerial()
updated_at = str(datetime.now())
batteryVoltage = x750ups.readVoltage(x750ups.bus)
batteryCapacity = x750ups.readCapacity(x750ups.bus)
wirelessInfo = popen("iwconfig wlan0 | awk '{$1=$1;print}'").read().split('\n')
ssid = re.search('ESSID:"+(\w)+"', wirelessInfo[0]).group(0)[7:-1]
linkQuality = re.search('Link Quality=+\d\d+/+\d\d', wirelessInfo[5]).group(0)[13:]
signalLevel = re.search('Signal level=-+\d+ dBm', wirelessInfo[5]).group(0)[13:-4]
#remainingData = # 전송 안된 데이터 개수 읽기
#deviceTemperature = # RTC 모듈 온도센서에서 온도 읽기
deviceTime = str(datetime.now())

if __name__ == "__main__":
    try:
        connection, cursor = connectDB()

        sFileName = 'status.csv'
        sTableName = 'device_status'
        sColumnList = ('station_code', 'device_time', 'battery_voltage', 'battery_capacity', 'ssid', 'link_quality', 'signal_level', 'stored_data', 'cpu_temperature', 'rtc_temperature')
        sColumnList = ', '.join(sColumnList)

        if isfile(sFileName):
            logger('Found previous status that could not be stored to DB server. Try again to save those...')
            statusFile = pd.read_csv(sFileName, encoding='utf-8', header=None)
            statusFile = list(statusFile.to_records(index=False))
            query = 'INSERT INTO `' + sTableName + """` (stationCode, updated_at, batteryVoltage, batteryCapacity, ssid, linkQuality, signalLevel, remainingData, deviceTemperature, deviceTime) 
                       VALUES (%s, %s, %s, %s)"""
            cursor.executemany(query, statusFile)
            connection.commit()
            if int(cursor.rowcount) > 1:
                messageVerb = 'were'
            else:
                messageVerb = 'was'
            logger('Previous', str(cursor.rowcount), 'status file', messageVerb, 'inserted.')
        query = f"""INSERT INTO {sTableName} (stationCode, updated_at, batteryVoltage, batteryCapacity, ssid, linkQuality, signalLevel, remainingData, deviceTemperature, deviceTime)
                    VALUES ({stationCode}, {updated_at}, {batteryVoltage}, {batteryCapacity}, {ssid}, {linkQuality}, {signalLevel}, {remainingData}, {deviceTemperature}, {deviceTime})"""
        cursor.execute(query)
        connection.commit()
    except Exception as e:
        logError(e, 'Sending status failed! ERROR: ' + str(e))
    finally:
        connection.close()
        logger('Connection closed. Quit this module..')