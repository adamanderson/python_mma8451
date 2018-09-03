from MMA8451 import MMA8451
import struct
from ctypes import create_string_buffer
from datetime import datetime
import os
import logging

class MMA8451DAQ(object):
    def __init__(self):
        # create output file
        self.create_file()
        self.max_fsize = 1e5 # bytes

        # create the output buffer
        self.buffer_size = 4*3 # 3 axes with a 32-bit float for each
        self.buffer_fmt = 'fff'
        self.buff = create_string_buffer(self.buffer_size)
        
        # MMA8451 driver object
        self.accelerometer = MMA8451()
        self.accelerometer.begin()

    def acquisition_loop(self):
        while True:
            # read the data and write to file
            data = self.accelerometer.read()
            if data is not None:
                raw_data = (data['x'], data['y'], data['z'])
                struct.pack_into(self.buffer_fmt, self.buff, 0, *raw_data)
                self.outfile.write(self.buff)

                # monitor the FIFO for backlogged data
                overflow, counts = self.accelerometer.check_fifo()
                if counts >= 32:
                    raise RuntimeError('MMA8451 FIFO buffer is full. '
                                       'Exiting to avoid data loss.')
                if counts > 10:
                    logging.warning('MMA8451 FIFO buffer has {} of 32 '
                                    'entries filled.'.format(counts))
                
                # check the file size and open a new file if necessary
                if os.stat(self.fname).st_size > self.max_fsize:
                    self.cleanup()
                    self.create_file()
                
    def create_file(self):
        self.fname = datetime.utcnow().strftime('%Y%m%d_%H%M%S_accelerometer.dat')
        self.outfile = open(self.fname, 'wb')
    
    def cleanup(self):
        self.outfile.close()
        
    def run(self):
        try:
            self.acquisition_loop()
        except KeyboardInterrupt:
            self.cleanup()
            
if __name__ == '__main__':
    daq = MMA8451DAQ()
    daq.run()
        
