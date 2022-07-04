from daqimu import daqimu
import time
import numpy as np

# example reads for 5 seconds, result is in y

dev=daqimu() # (or  daqimu(False)) connects with USB interface
#dev=daqimu(True)  # wifi default 192.168.4.1 and port 1234
#dev=daqimu(True,'hostname')  # wifi with dedicated hostname (if device is in local net)
# dev=daqimu(True,("192.168.178.2",1234))  # wifi with dedicated ip address and port
ports = dev.getDevices();
# ---------------------------------- set the measuring parameters
dev.clear()
dev.setSampleRate(100)
dev.addImu6(2,250)
# ---------------------------------- open and start
dev.open(ports[0])
dev.startSampling()
print("please wait 6 seconds")
time.sleep(5)
# ------------------------------------ stop the process
dev.stopSampling()
time.sleep(1) # to be shure to get all data
# -------------------------------------- get data
y = dev.getStreamingData()
dev.close()
print("result is np.array",y.shape)
