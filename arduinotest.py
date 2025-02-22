import serial
import time
import serial.tools.list_ports

ports = serial.tools.list_ports.comports()
for port in ports:
	print(port.device)
port = ports[0].device
arduino = serial.Serial(port=port, baudrate=115200, timeout=.1)


def write_read(x):
	arduino.write(bytes(x, 'utf-8'))
	time.sleep(0.05)
	response = arduino.readline()
	return response


while True:
	command = input("Enter your command: ") # Taking input from user
	value = write_read(command + '\n')
	print(value) # printing the value
