#!/usr/bin/python

# Dependency: https://github.com/cherezov/orvibo

import binascii
import time
import sys
from orvibo import Orvibo

py3 = sys.version_info[0] == 3

SPA_MAC="DEVICE_MAC_HERE"
ATTEMPTS_TO_TRY=120
WAIT_SECONDS_BETWEEN_ATTEMPTS=30

if len(sys.argv) < 2 or len(sys.argv) > 3:
  sys.exit('Incorrect number of arguments, please specify only ON or OFF and optionally a wait period')

if ("ON" != sys.argv[1] and "OFF" != sys.argv[1]):
  sys.exit('Please specify ON or OFF')

switchToOn = (sys.argv[1] == "ON")

if len(sys.argv) == 3:
  ATTEMPTS_TO_TRY = WAIT_SECONDS_BETWEEN_ATTEMPTS * (ATTEMPTS_TO_TRY / int(sys.argv[2]))
  WAIT_SECONDS_BETWEEN_ATTEMPTS = int(sys.argv[2])
  print("Wait {}, Try {} times".format(WAIT_SECONDS_BETWEEN_ATTEMPTS, ATTEMPTS_TO_TRY))

def getIPForMac(mac):
  for vals in Orvibo.discover().values():
    foundMac = binascii.hexlify(vals[1]).decode('utf-8') if py3 else binascii.hexlify(vals[1])
    if(foundMac == mac):
      print('Found IP={}'.format(vals[0]) )
      return vals[0]
  return None


def getDeviceForMac(mac, attempts, delay):
  attempt = 1
  while attempt <= attempts:
    ip = getIPForMac(mac)
    if ip is not None:
      return Orvibo(ip)
    print('Waiting {}'.format(delay))
    time.sleep(delay)
  else:
    print('Exhausted attempts to find mac: ', mac)
  return None

spaSocket = getDeviceForMac(SPA_MAC, ATTEMPTS_TO_TRY, WAIT_SECONDS_BETWEEN_ATTEMPTS)
print('Spa power state: {}'.format(spaSocket.on))
if (spaSocket.on == switchToOn):
  print('No need to switch state')
else:
  # Once we get here we assume the device never changes IP.
  attemptsTried = 0
  while spaSocket.on != switchToOn:
    try:
      spaSocket.on = not spaSocket.on
      print('Tried to switch state')
    except:
      print('Caught exception trying to switch state, re-checking and trying again if needed.')
    attemptsTried = attemptsTried + 1
    time.sleep(WAIT_SECONDS_BETWEEN_ATTEMPTS)
    # Only give up if we are switching it on, otherwise keep trying forever
    if (switchToOn == True and attemptsTried > ATTEMPTS_TO_TRY):
      print('Giving up after {} attempts tried.'.format(attemptsTried))
      break


