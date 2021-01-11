sudo apt-get update -y && sudo apt-get upgrade -y
sudo apt-get install -y libatlas-base-dev rdate vim rdate python-smbus i2c-tools
pip3 install -r requirements.txt
sudo ln -sf /usr/share/zoneinfo/Asia/Seoul /etc/localtime

cd ~
git clone https://github.com/graphy-young/raspmeasure.git

git clone https://github.com/geekworm-com/x750.git
sudo chmod +x ./x750/x750.sh
sudo bash ./x750/x750.sh
rm -rf ~/x750ups.py