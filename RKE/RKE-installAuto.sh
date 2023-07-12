#!/bin/bash

for os in ubuntu centos
do
  my_os=`(cat /etc/os-release | cut -d \" -f 2 | awk 'NR==1{print $1}'| grep -i ${os} )`
  if [ ! -z ${my_os} ]; then
    wget https://raw.githubusercontent.com/Douggy91/Side_Work/master/RKE-installAuto_${os}.sh
    source RKE-installAuto_${os}.sh
  fi
done
