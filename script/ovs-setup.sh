#!/bin/bash

if [[ $EUID -ne 0 ]]; then
   echo "Root privileges required" 
   exit 1
fi

mkdir -p "/opt/ovs/"
mkdir -p "/opt/ovs/src"

echo "Downloading OpenvSwitch 2.3.1"
curl http://openvswitch.org/releases/openvswitch-2.3.1.tar.gz | tar -xzC "/opt/ovs/src"

echo "Installing OVS"
cd /opt/ovs/openvswitch-2.3.1
./configure --prefix=/opt/ovs/2.3.1 --with-linux=/lib/modules/`uname -r`/build
make
sudo make install
sudo cp /opt/ovs/src/openvswitch-2.3.1/datapath/linux/openvswitch.ko /opt/ovs/2.3.1/sbin

echo "Configuring OVS"
BASEDIR=$(dirname $0)
sudo cp $BASEDIR/ovs-ctl.conf /opt/ovs/ovs-ctl-default.conf
python $BASEDIR/ovs-ctl.py --config 2.3.1

echo "Done!!"
