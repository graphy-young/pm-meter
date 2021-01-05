sudo apt-get update -y && sudo apt-get upgrade -y
sudo apt-get install -y libatlas-base-dev rdate vim rdate
pip3 install -r requirements.txt
sudo ln -sf /usr/share/zoneinfo/Asia/Seoul /etc/localtime