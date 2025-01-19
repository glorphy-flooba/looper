# the only stuff you gotta pip install here is pyaudio and keyboard, the rest is here my default
# to stop the code without closing the terminal, press z and c at the same time
import pyaudio
import keyboard
import numpy as np
import time
import struct
import math

#config, change to your needs
loopbind = 'f19' #what key you hold down to have it loop, i use f19 because its on my mouse
virtualmikeindex = 10 #run the code, look for output device with name "CABLE Input (VB-Audio Virtual C" or similar, and use the index of that
volumethreshold = 0.02 #run the code after setting everything up, look at the numbers it outputs, thats the volume, change this variable to be the volume you want to trigger the loop
samplerate = 44100 #works for me, but 48000 would also be very common

chunk = 1024 #dont change any of this unless you know what your doing (I dont)
format = pyaudio.paInt16

p = pyaudio.PyAudio()

## list available devices
info = p.get_host_api_info_by_index(0)
numdevices = info.get('deviceCount')
for i in range(0, numdevices):
        if (p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
            print("Input Device id ", i, " - ", p.get_device_info_by_host_api_device_index(0, i).get('name'))
            
        if (p.get_device_info_by_host_api_device_index(0, i).get('maxOutputChannels')) > 0:
            print("Output Device id ", i, " - ", p.get_device_info_by_host_api_device_index(0, i).get('name'))
            
input = p.open(format = format,
                channels = 1,
                rate = samplerate,
                input = True,
                frames_per_buffer = chunk)

virtualmike = p.open(format = format,   
                channels = 1,
                rate = samplerate,
                output = True,
                output_device_index = virtualmikeindex)

hearyourself = p.open(format = format,   
                channels = 1,
                rate = samplerate,
                output = True)


def volume(data): #stolen off internet from https://stackoverflow.com/questions/25868428/pyaudio-how-to-check-volume?rq=4 top answer, returns how loud something is in some form i dont understand
    count = len(data)/2
    format = "%dh"%(count)
    shorts = struct.unpack( format, data )
    sum_squares = 0.0
    for sample in shorts:
        n = sample * (1.0/32768)
        sum_squares += n*n
    return math.sqrt( sum_squares / count )


while True:
    if not keyboard.is_pressed(loopbind):
        s = input.read(chunk)
        virtualmike.write(s)
        hearyourself.write(s)
    if keyboard.is_pressed(loopbind): 
        print("waiting for loud")
        while volume(s) < volumethreshold and keyboard.is_pressed(loopbind): #wait intill you actually start saying anything, 0.02 is the volume, it worked for me, change it if required 
            virtualmike.write(s)
            hearyourself.write(s)
            s = input.read(chunk)
            print(volume(s))
        while keyboard.is_pressed(loopbind):
            virtualmike.write(s)
            hearyourself.write(s)
            print(volume(s))
    if keyboard.is_pressed('z') and keyboard.is_pressed('c'): #
        print("ending")
        input.stop_stream()
        input.close()
        virtualmike.stop_stream()
        virtualmike.close()
        hearyourself.stop_stream()
        hearyourself.close()
        p.terminate()
        break
    time.sleep(0.005)


#I wrote this for fun and to learn pyaudio so it probably sucks, also this is my first public github project so everything is probably bad in some way 

