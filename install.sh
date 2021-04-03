#!/bin/bash
if [ -z `which pip` ]  ; then
   echo "Error: python-pip not install."
   exit 1 
fi

pip install --upgrade pip
if [ `ansible --version | head -1 | cut -f2 -d' '|cut -c1-3` != "2.9" ]; then
   echo "Error: The script only supports ansible 2.9."
   exit 1
fi

ANSIBLE_LOCATION=`pip show ansible | grep Location | cut -f2 -d':'`
ANSIBLE_PATH="$ANSIBLE_LOCATION/ansible"

if [ -z "$ANSIBLE_LOCATION" ] ; then
    echo "Error: Can not get Ansible dist-packages location."
    exit 1
else
    echo "Ansible dist-packages path:$ANSIBLE_PATH"
fi

echo "Huawei S Series modules path:$ANSIBLE_PATH/modules/network/huawei_s"
mkdir -p $ANSIBLE_PATH/modules/network/huawei_s
mkdir -p $ANSIBLE_PATH/module_utils/network/huawei_s

echo "Copying files ..."
if [ -d "./plugins/modules" ]; then
    cp -rf ./plugins/modules/* $ANSIBLE_PATH/modules/network/huawei_s
fi

if [ -d "./plugins/action" ]; then
    cp -rf ./plugins/action/huawei_s.py $ANSIBLE_PATH/plugins/action
fi

if [ -d "./plugins/cliconf" ]; then
    cp -rf ./plugins/cliconf/huawei_s.py $ANSIBLE_PATH/plugins/cliconf
fi

if [ -d "./plugins/doc_fragments" ]; then
    cp -rf ./plugins/doc_fragments/huawei_s.py $ANSIBLE_PATH/plugins/doc_fragments
fi

if [ -d "./plugins/terminal" ]; then
    cp -rf ./plugins/terminal/huawei_s.py $ANSIBLE_PATH/plugins/terminal
fi

if [ -d "./plugins/module_utils" ]; then
    cp -rf ./plugins/module_utils/network/huawei_s/* $ANSIBLE_PATH/module_utils/network/huawei_s
fi

echo "Huawei S series Ansible 2.9 library installed."
