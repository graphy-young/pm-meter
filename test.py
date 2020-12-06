import honeywell_hpma115s0 as hw
import os
import datetime
import pymysql, keys

def logger(*args): 
    """
    All parameters should be on string-type!
    """
    from datetime import datetime
    print('[' + str(datetime.now()) + ']', str(' '.join(args)))

sensor = hw.Honeywell(port="/dev/serial0", baud=9600)

mysql = pymysql.connect(
    host=keys.host, 
    port=keys.port, 
    user=keys.user, 
    password=keys.password, 
    database=keys.dbname)
cursor = mysql.cursor()

measuredDateime, pm10, pm25 = str(sensor.read()).split(',')
logger('measuredDatetime: {measuredDatetime}, PM10: {PM10}, PM2.5: {PM25}')
os.system('echo {measuredTime}, {pm10}, {pm25}')
