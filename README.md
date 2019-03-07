# pigpiosim

This is a kivy based simulator for pigpio. You can run it instead of pigpiod and it allows to simulate
inputs and see outputs. It listens on the same port pigpiod does (8888) and responds to a very small subset
of pigpio's protocol.

I wrote this tool to allow me to write and test code for a Raspberry Pi project on a virtual machine that obviously
isn't a Raspberry Pi.

