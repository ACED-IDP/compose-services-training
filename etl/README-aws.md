cat >> ~./bashrc
alias dc='docker compose'
export PS1="\e[0;32m[\u@staging \W]\$ \e[0m"


sudo apt-get remove docker docker-engine docker.io containerd runc
sudo apt-get update
sudo apt-get install     ca-certificates     curl     gnupg     lsb-release
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo   "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
$(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-compose-plugin
sudo usermod -aG docker $USER


sudo apt update
sudo apt install software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt install python3.9
python3.9 --version
sudo apt-get install python3.9-venv

sudo apt install unzip
sudo apt install jq

   

alias h='history | grep $1'

alias h='history | grep $1'
alias dc='docker-compose'
rs () {
  docker-compose stop $1
  docker-compose rm -f $1
  docker-compose up -d $1
  docker-compose logs -f $1
}