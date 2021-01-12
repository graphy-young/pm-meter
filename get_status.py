import x750ups
from get_measurements import logger, logError, getSerial
from datetime import datetime
from os import system

if __name__ == "__main__":
    stationCode = getSerial()
    updated_at = str(datetime.now())[:-7]
    batteryVoltage = x750ups.readVoltage()
    batteryCapacity = x750ups.readCapacity()
    ssid = system("iwconfig wlan0 | grep ESSID:"*" | awk '{$1=$1;print}' | cut -f 2 -d '"'")
    linkQuality = system("iwconfig wlan0 | grep Link | awk '{$1=$1;print}' | cut -f 2 -d '=' | cut -f 1 -d " "")
    signalLevel = system("iwconfig wlan0 | grep Link | awk '{$1=$1;print}' | cut -f 3 -d '=' | cut -f 1 -d " "")
    remainingData = # 전송 안된 데이터 개수 읽기
    deviceTemperature = # RTC 모듈 온도센서에서 온도 읽기
    deviceTime = str(datetime.now())
    ### db 모델 변경하기