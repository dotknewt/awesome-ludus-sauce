#!/usr/bin/bash
brctl setageing vmbr1002 0
ip link set vmbr1002 promisc on
