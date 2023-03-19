#!/bin/bash

#echo "press your Ip"
#read my_ip
apt-get install -y net-tools expect
hostnamectl set-hostname RKE-CONS0

my_ip=`ifconfig | grep inet | grep -Ev inet6 | awk 'NR==1{print $2}'`
#my_ip_in=`ifconfig | grep inet | grep -Ev inet6 | awk 'NR==2{print $2}'`

controlArr=()
i=0
answer_con=n

echo "add Control Plane?(y/n)"
read addmore

if [ "$addmore" == "y" ]; then
	while [ "$answer_con" == "n" ]
	do
		echo "press control_ip"
		read control_ip
		controlArr[$i]=$control_ip
		echo "is done? [y/n]"
		read answer_con
		let "i+=1"
	done
fi
workerArr=()
i=0
answer=n

while [ "$answer" == "n" ]
do
	echo "press worker_ip"
	read worker_ip
	workerArr[$i]=$worker_ip
	echo "is done? [y/n]"
	read answer
	let "i+=1"
done

allArr=(${controlArr[@]} ${workerArr[@]}) 

#ssh certification
echo -e "press password\nplease before starting this script,set all node password same password"
read password

echo "use LB?"
read use_LB

if [ "$use_LB" == "y" ]; then
  echo "press LB_ip"
	read LB_ip
else
  $LB_ip=$my_ip
fi

echo " 
apt-get install -y expect
expect <<EOF
spawn ssh-keygen -t rsa
set timeout 3
expect \"save the key\"
send \"\\r\"
expect \"passphrase\"
send \"\\r\"
expect \"same passphrase\"
send \"\\r\"
spawn ssh-keygen -t dsa
expect \"save the key\"
send \"\\r\"
expect \"passphrase\"
send \"\\r\"
expect \"same passphrase\"
send \"\\r\"
expect eof
EOF
cat /root/.ssh/*.pub > /root/.ssh/authorized_pub
"> ssh_generate_server.sh

source ssh_generate_server.sh

if [ "$addmore" == "y" ]; then
	for (( i=0; i<${#controlArr[@]};i++)); do
		v=$i
		let "v+=1"
		echo "
		apt-get install expect -y
		expect <<EOF
		spawn ssh-keygen -t rsa
		set timeout 3
		expect \"save the key\"
		send \"\\r\"
		expect \"passphrase\"
		send \"\\r\"
		expect \"same passphrase\"
		send \"\\r\"
		spawn ssh-keygen -t dsa
		expect \"save the key\"
		send \"\\r\"
		expect \"passphrase\"
		send \"\\r\"
		expect \"same passphrase\"
		send \"\\r\"
		expect eof
		EOF
		cat /root/.ssh/*.pub > /root/.ssh/authorized_pub
		expect <<EOF
		spawn scp /root/.ssh/authorized_pub ${my_ip}:/root/.ssh/${controlArr[$i]}_pub
		expect \"connecting\"
		send \"yes\\r\"
		expect \"password\"
		send \"${password}\\r\"
		expect eof
EOF
		" > ssh_generate_s$v.sh

		expect <<EOF 
		spawn ssh ${controlArr[$i]} hostnamectl set-hostname RKE-CONS$v
		expect "connecting"
		send "yes\r"
		expect "password"
		send "${password}\r"

		spawn scp /root/ssh_generate_s$v.sh ${controlArr[$i]}:/root/ssh_generate_s$v.sh
		expect "password"
		send "${password}\r"

		spawn ssh ${controlArr[$i]} source /root/ssh_generate_s$v.sh
		expect "password"
		send "${password}\r"
		expect eof
EOF
	done
fi

for (( i=0; i<${#workerArr[@]};i++)); do
	v=$i
	let "v+=1"
			echo "
		apt-get install expect -y
		expect <<EOF
		spawn ssh-keygen -t rsa
		set timeout 3
		expect \"save the key\"
		send \"\\r\"
		expect \"passphrase\"
		send \"\\r\"
		expect \"same passphrase\"
		send \"\\r\"
		spawn ssh-keygen -t dsa
		expect \"save the key\"
		send \"\\r\"
		expect \"passphrase\"
		send \"\\r\"
		expect \"same passphrase\"
		send \"\\r\"
		expect eof
		EOF
		cat /root/.ssh/*.pub > /root/.ssh/authorized_pub
		expect <<EOF
		spawn scp /root/.ssh/authorized_pub ${my_ip}:/root/.ssh/${workerArr[$i]}_pub
		expect \"connecting\"
		send \"yes\\r\"
		expect \"password\"
		send \"${password}\\r\"
		expect eof
EOF
		" > ssh_generate_a$v.sh
	expect <<EOF 
	spawn ssh ${workerArr[$i]} hostnamectl set-hostname RKE-WORKER$v
	expect "connecting"
	send "yes\r"
	expect "password"
	send "${password}\r"

	spawn scp /root/ssh_generate_a$v.sh ${workerArr[$i]}:/root/ssh_generate_a$v.sh
	expect "password"
	send "${password}\r"

	spawn ssh ${workerArr[$i]} source /root/ssh_generate_a$v.sh
	expect "password"
	send "${password}\r"
	expect eof
EOF
done

cat /root/.ssh/*_pub > /root/.ssh/authorized_keys

for (( i=0; i<${#allArr[@]};i++)); do
        v=$i
        let "v+=1"
        expect <<EOF
	spawn scp /root/.ssh/authorized_keys ${allArr[$i]}:/root/.ssh/authorized_keys
	expect "password"
	send "${password}\r"
	expect eof
EOF
done


#k8s pre setting
echo -e "swapoff -a \napt-get upgrade -y \napt-get dist-upgrade -y \napt-get update -y \nsystemctl stop ufw && ufw disable && iptables -F \napt-get install curl -y \napt-get install -y open-iscsi \napt-get install -y nfs-common \ncurl -sfL https://get.rke2.io | INSTALL_RKE2_TYPE="server" sh - \nsystemctl enable rke2-server.service \nmkdir -p /etc/rancher/rke2" > server.sh

echo -e "swapoff -a \napt-get upgrade -y \napt-get dist-upgrade -y \napt-get update -y \nsystemctl stop ufw && ufw disable && iptables -F \napt-get install curl -y \napt-get install -y open-iscsi \napt-get install -y nfs-common \ncurl -sfL https://get.rke2.io | INSTALL_RKE2_TYPE="agent" sh - \nsystemctl enable rke2-agent.service \nmkdir -p /etc/rancher/rke2" > agent.sh

source server.sh

if [ ! -e /etc/rancher/rke2 ]; then
	mkdir -p /etc/rancher/rke2
	echo -e "cni: \"calico\" \ntls-san:\n  - my-kubernetes-domain.com \n  - another-kubernetes-domain.com" > /etc/rancher/rke2/config.yaml
else
	echo -e "cni: \"calico\" \ntls-san:\n  - my-kubernetes-domain.com \n  - another-kubernetes-domain.com" > /etc/rancher/rke2/config.yaml
fi

systemctl start rke2-server.service


#kubeconfig setting

if [ ! -e ~/.kube ]; then
	mkdir ~/.kube/
fi
cp /etc/rancher/rke2/rke2.yaml ~/.kube/config
export PATH=$PATH:/var/lib/rancher/rke2/bin/
echo 'export PATH=/usr/local/bin:/var/lib/rancher/rke2/bin:$PATH' >> ~/.bashrc
echo 'source <(kubectl completion bash)' >>~/.bashrc
echo 'alias k=kubectl' >>~/.bashrc
echo 'complete -F __start_kubectl k' >>~/.bashrc
source ~/.bashrc
echo 'export CRI_CONFIG_FILE=/var/lib/rancher/rke2/agent/etc/crictl.yaml' >> ~/.bashrc
export CRI_CONFIG_FILE=/var/lib/rancher/rke2/agent/etc/crictl.yaml
/var/lib/rancher/rke2/bin/crictl  ps -a

#token exchange & worker setting
export token=`cat /var/lib/rancher/rke2/server/node-token`
echo -e "server: https://${LB_ip}:9345 \ntoken: ${token} \ncni: \"calico\" \ntls-san:\n  - my-kubernetes-domain.com \n  - another-kubernetes-domain.com" > config.yaml

if [ "$addmore" == "y" ]; then
	for ((i=0; i<${#controlArr[@]};i++)); do
		scp server.sh ${controlArr[$i]}:/root/server.sh
		ssh ${controlArr[$i]} source server.sh
		scp config.yaml ${controlArr[$i]}:/etc/rancher/rke2/config.yaml
		ssh ${controlArr[$i]} systemctl start rke2-server.service
	done
fi

for ((i=0; i<${#workerArr[@]};i++)); do
	scp agent.sh ${workerArr[$i]}:/root/agent.sh
	ssh ${workerArr[$i]} source agent.sh
	scp config.yaml ${workerArr[$i]}:/etc/rancher/rke2/config.yaml
	ssh ${workerArr[$i]} systemctl start rke2-agent.service
done

#cert-manager && rancher setting 
kubectl apply -f https://github.com/jetstack/cert-manager/releases/download/v1.5.4/cert-manager.yaml
kubectl -n cert-manager rollout status deploy/cert-manager
kubectl -n cert-manager rollout status deploy/cert-manager-webhook 
kubectl get pods --namespace cert-manager
curl https://raw.githubusercontent.com/helm/helm/master/scripts/get-helm-3 | bash
helm version --client --short
kubectl create namespace cattle-system
helm repo add rancher-stable https://releases.rancher.com/server-charts/stable
helm repo update
helm search repo rancher-stable

replicas_cnt=`kubectl get nodes | awk 'NR>1'| wc -l`
helm install rancher rancher-stable/rancher --namespace cattle-system --set hostname=${my_ip}.nip.io --set replicas=${replicas_cnt} --set bootstrapPassword="${password}"

curl -sL https://github.com/derailed/k9s/releases/download/v0.26.3/k9s_Linux_x86_64.tar.gz | tar xfz - -C /usr/local/bin k9s
