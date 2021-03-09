''' Module import '''
from modules import x750ups, ds3231
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

    sFileName = '~/raspmeasure/status.csv'
    sTableName = 'device_status'
    sColumnList = ['station_code', 'device_time', 'battery_voltage', 'battery_capacity', 'ethernet_connection', 
                    'ethernet_IP', 'ethernet_gateway', 'ssid', 'wireless_IP', 'wireless_gateway',
                    'link_quality', 'signal_level', 'signal_percent', 'stored_data', 'cpu_temperature', 
                    'rtc_temperature']
    try:
        connection, cursor = connectDB()

        station_code = getStationCode()
        device_time = str(datetime.now())

        try:
            battery_voltage = x750ups.readVoltage(x750ups.bus)
            battery_capacity = x750ups.readCapacity(x750ups.bus)
        except:
            battery_voltage = None
            battery_capacity = None

        try:
            ethernetInfo = popen("ifconfig eth0 | awk '{$1=$1;print}'").read().split('\n')
            if ethernetInfo[1].startswith('inet '):
                ethernet_connection = True
                ethernet_IP = ethernetInfo[1].split()[1]
                ethernet_gateway = ethernetInfo[1].split()[5]
                logger(f'Ethernet connection detected. IP: {ethernet_IP}, GATEWAY: {ethernet_gateway}')
            else:
                raise Exception
        except:
            logger('No ethernet connection detected. continue to get wireless information')
            ethernet_connection = False
            ethernet_IP = None
            ethernet_gateway = None

        try:
            wirelessInfo = popen("iwconfig wlan0 | awk '{$1=$1;print}'").read().split('\n')
            ssid = re.search('ESSID:"+(\w)+"', wirelessInfo[0]).group(0)[7:-1]
            wirelessInfo2 = popen("ifconfig wlan0 | awk '{$1=$1;print}'").read().split('\n')
            wireless_IP = wirelessInfo2[1].split()[1]
            wireless_gateway = wirelessInfo2[1].split()[5]
            link_quality = int(re.search('Link Quality=+\d\d+/+\d\d', wirelessInfo[5]).group(0)[13:].split('/')[0])
            signal_level = int(re.search('Signal level=-+\d+ dBm', wirelessInfo[5]).group(0)[13:-4])
            signal_percent = (signal_level + 110) * 10 / 7
        except:
            ssid = None
            wireless_IP = None
            wireless_gateway = None
            link_quality = None
            signal_level = None
            signal_percent = None

        stored_data = 0
        cpu_temperature = CPUTemperature().temperature
        rtc_temperature = ds3231.SDL_DS3231(1, 0x68).getTemp()

        if isfile(sFileName):
            logger('Found previous status that could not be stored to DB server. Try again to save those...')
            statusFile = pd.read_csv(sFileName, encoding='utf-8', names=sColumnList)
            statusFile = statusFile.astype({'station_code': 'str'})
            statusFile['station_code'] = statusFile['station_code'].apply(lambda x: '0'+str(x) if int(x) < 10 else x)
            stored_data = len(statusFile)
            statusFile = list(statusFile.values.tolist())
            query = f"INSERT INTO `{sTableName}` ({', '.join(sColumnList)}) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
            cursor.executemany(query, statusFile)
            connection.commit()
            if int(cursor.rowcount) > 1:
                messageVerb = 'were'
            else:
                messageVerb = 'was'
            logger('Previous', str(cursor.rowcount), 'status file', messageVerb, 'inserted.')
            system(f'rm -rf {sFileName}')
            logger(f'{sFileName} deleted.')
        query = f"""INSERT INTO {sTableName} ({', '.join(sColumnList)}) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        cursor.execute(query, [eval(col) for col in sColumnList])
        connection.commit()
        logger(f"status data {station_code}, {device_time}, {battery_voltage}, {battery_capacity}, {ethernet_connection}, {ethernet_IP}, {ethernet_gateway}, {ssid}, {wireless_IP}, {wireless_gateway}, {link_quality}, {signal_level}, {signal_percent}, {stored_data}, {cpu_temperature}, {rtc_temperature} inserted.")

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