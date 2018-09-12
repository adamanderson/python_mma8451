from MMA8451 import MMA8451
import struct
from ctypes import create_string_buffer
from datetime import datetime
import os
import logging

class MMA8451DAQ(object):
    def __init__(self):
        # MMA8451 driver object
        self.accelerometer = MMA8451()
        self.accelerometer.begin()

        # create output file
        self.create_file()
        self.max_fsize = 1e8 # bytes
        self.write_header()
        
        # create the output buffer
        self.buffer_size = 4*3 + 12 
        self.buffer_fmt = 'fffd'
        self.buff = create_string_buffer(self.buffer_size)
        

    def acquisition_loop(self):
        '''
        Runs an infinite loop that acquires data from the accelerometer.

        Parameters
        ----------
        None

        Returns
        -------
        None
        '''
        while True:
            # read the data and write to file
            data = self.accelerometer.read()
            if data is not None:
                timestamp = datetime.utcnow().timestamp()
                raw_data = (data['x'], data['y'], data['z'], timestamp)
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
                    self.write_header()
                
    def create_file(self):
        '''
        Creates file for accelerometer data.

        Parameters
        ----------
        None

        Returns
        -------
        None
        '''
        self.fname = datetime.utcnow().strftime('%Y%m%d_%H%M%S_accelerometer.dat')
        self.outfile = open(self.fname, 'wb')
    
    def cleanup(self):
        '''
        Cleanup operations after a KeyboardInterrupt.

        Parameters
        ----------
        None

        Returns
        -------
        None
        '''
        self.outfile.close()

    def write_header(self):
        '''
        Write file header for accelerometer data. Contains timestamp and rate.

        Parameters
        ----------
        None

        Returns
        -------
        None
        '''
        # format: start time, data rate (in Hz)
        header_buffer_size = 8 + 4
        header_buffer_fmt = 'df'
        header_data = (datetime.utcnow().timestamp(), self.accelerometer.rate)
        header_buffer = create_string_buffer(header_buffer_size)
        struct.pack_into(header_buffer_fmt, header_buffer, 0, *header_data)
        self.outfile.write(header_buffer)
        
    def run(self):
        '''
        Wrapper that runs the acquisition loop with handling for
        KeyboardInterrupts.

        Parameters
        ----------
        None

        Returns
        -------
        None
        '''
        try:
            self.acquisition_loop()
        except KeyboardInterrupt:
            self.cleanup()
            
if __name__ == '__main__':
    daq = MMA8451DAQ()
    daq.run()
        
