import time
import serial
import requests

ser = serial.Serial("COM5", baudrate=115200, timeout=0.1)
time.sleep(3)
def write_data(x):
	ser.write(bytes(x, 'utf-8'))
	data = ser.readline()
	return data

while True:
	r = requests.get("http://127.0.0.1:3000/get_data").json()
	s = r['previous_hash'] + ","
	#print(f"previous_hash: {s}")
	try:
		data = write_data(s)
		s = (data.decode("utf-8")).replace("\r\n","")
		print(s)

		h, n = s.split(",")

		r = requests.post("http://127.0.0.1:3000/block", json={"hash":h, "nonce":n, "sender":"AVR", "receiver":"Atmega328p", "amount":10}).json()
		print(r['message'])

		#break;
	except:
		print("Waiting for arduino's response")