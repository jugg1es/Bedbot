#!/bin/bash
c=$2

turnOn() {
	sudo sh -c "echo '1' > /sys/class/gpio/gpio508/value"
}

turnOff() {
	sudo sh -c "echo '0' > /sys/class/gpio/gpio508/value"
}

init() {
	sudo sh -c "echo 508 > /sys/class/gpio/export"
	sudo sh -c "echo 'out' > /sys/class/gpio/gpio508/direction"
}

case $1 in
	on) turnOn ;;
	off) turnOff ;;
	init) init ;;
	*) echo "usage: $0 on|off" > $2
	   exit 1
	   ;;
esac