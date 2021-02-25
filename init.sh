# Install dependencies
sudo apt-get update -y && sudo apt-get upgrade -y
sudo apt-get install -y libatlas-base-dev rdate vim rdate python-smbus i2c-tools
pip3 install -r requirements.txt
sudo ln -sf /usr/share/zoneinfo/Asia/Seoul /etc/localtime

# Install programs for X750 UPS module
cd ~
git clone https://github.com/geekworm-com/x750.git
sudo chmod +x ./x750/x750.sh
sudo bash ./x750/x750.sh
rm -rf ~/x750ups.py

# Enable SSH
sudo systemctl enable ssh
sudo systemctl start ssh

# Enable I2C communication & Disable Bluetooth
echo "i2c_bcm2835
rtc-ds1307" | sudo tee -a /etc/modules
echo "dtparam=i2c_arm=onå
dtoverlay=i2c-rtc,ds3231,disable-bt" | sudo tee -a /boot/config.txt

# Setup wireless network
sudo mv /etc/wpa_supplicant/wpa_supplicant.conf /etc/wpa_supplicant/wpa_supplicant.conf.bak
echo -e "ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1
country=GB\n
network={
\tssid="$(python3 keys.py ssid)"
\tpsk="$(python3 keys.py wpa_key)"
}" | sudo tee /etc/wpa_supplicant/wpa_supplicant.conf

# Modify hostname with RPi's serial code
sudo cp /etc/hosts /etc/hosts.bak
sudo head -n -1 | sudo tee -a /etc/hosts
echo -e "127.0.1.1\traspmeasure-$(cat /proc/cpuinfo | grep Serial | cut -d ' ' -f 2)" | sudo tee -a /etc/hosts
sudo mv /etc/hostname /etc/hostname.bak
echo "raspmeasure-$(cat /proc/cpuinfo | grep Serial | cut -d ' ' -f 2)" | sudo tee -a /etc/hostname

# Disable GUI boot option
sudo update-rc.d lightdm disable

echo "enable_uart=1" | sudo tee -a /boot/config.txt

echo "ALL PROCESS COMPLETED. RPi WILL REBOOT"
sudo reboot