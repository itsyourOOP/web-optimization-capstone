
import serial
from time import sleep


def read_power():

  sd = serial.Serial("/dev/ttyUSB0", 115200, timeout=1)
  #sd.open()
  sd.flushInput()
  sd.flushOutput()

  resp = str(sd.read(150))
  resp = resp.split('\\r\\n')
  power = float(resp[len(resp)//2].split(',')[2])

  sd.close()

  return power

while True:

  power = read_power()
  print(power)

  sleep(0.2)
