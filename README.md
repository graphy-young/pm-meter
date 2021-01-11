# Raspmeasure
Raspmeasure is a portable measuring device for fine particles. 
This project is a part of research conducting in ENDS LAB in Kookmin University.
Some codes won't be open for security.

# Requirements
* Raspberry Pi 3 or newer (3 model recommended for less voltage use)
  * Raspbian OS or Debian Linux
  * Python 3
* Honeywell HPMA115S0-XXX
* MySQL database server to record measured data

### External libraries
* honeywell-hpma115s0
* pymysql
* pandas

# Memo
* Need `keys.py` which have database connection information in same directory 
* Original Arduino(.ino) file were removed for some hardware changes!
