import smbus
from time import sleep

MMA8451_DEFAULT_ADDRESS  = 0x1D

MMA8451_REG_OUT_X_MSB    = 0x01
MMA8451_REG_SYSMOD       = 0x0B
MMA8451_REG_WHOAMI       = 0x0D
MMA8451_REG_XYZ_DATA_CFG = 0x0E
MMA8451_REG_PL_STATUS    = 0x10
MMA8451_REG_PL_CFG       = 0x11
MMA8451_REG_CTRL_REG1    = 0x2A
MMA8451_REG_CTRL_REG2    = 0x2B
MMA8451_REG_CTRL_REG4    = 0x2D
MMA8451_REG_CTRL_REG5    = 0x2E
REG_F_SETUP              = 0x09
REG_F_STATUS             = 0x00

# write flags
FLAG_ACTIVE                = 0x01
FLAG_LOWNOISE              = 0x04
FLAG_RATE_50HZ             = 0x20
FLAG_RATE_200Hz            = 0x10
FLAG_RATE_400HZ            = 0x08
FLAG_RATE_800HZ            = 0x00
FLAGS_RATE                 = {50:FLAG_RATE_50HZ, 200:FLAG_RATE_200Hz,
                              400:FLAG_RATE_400HZ, 800:FLAG_RATE_800HZ}
FLAG_8BIT                  = 0x02
FLAG_FIFO_STOP_ON_OVERFLOW = 0x80

# read bit masks
MASK_FIFO_OVERFLOW         = 0x80
MASK_FIFO_COUNTS           = 0x3f

MMA8451_RANGES = {'2g': 0b00, '4g': 0b01, '8g': 0b10}
MMA8451_RESOLUTION = {'high': 0x02}
MMA8451_CALIBRATION = {'2g': 1./4096, '4g': 1./2048, '8g': 1./1024}

class MMA8451(object):
    def __init__(self, address=MMA8451_DEFAULT_ADDRESS,
                 sensor_range='2g', rate=400):
        self.bus = smbus.SMBus(1)
        self.addr = address
        self.range = sensor_range
        self.resolution = 'high'
        self.rate = rate
        self.rate_bit = FLAGS_RATE[self.rate]
            
        
    def begin(self):
        '''
        Initialize the settings of the accelerometer before beginning data
        acquisition. Data acquisition will fail without running this beforehand.

        Parameters
        ----------
        None

        Returns
        -------
        None
        '''
        # check device status
        device_id = self.bus.read_byte_data(self.addr,
                                            MMA8451_REG_WHOAMI)
        assert hex(device_id) != 0x1A, 'WHO_AM_I register is not expected value (0x1A).'
        sleep(0.1)
        
        # reset
        self.bus.write_byte_data(self.addr, MMA8451_REG_CTRL_REG2, 0x40)
        sleep(0.1)

        # set active, low-noise mode, and 50Hz data rate
        self.bus.write_byte_data(self.addr, MMA8451_REG_CTRL_REG1, 0x00) # reset
        self.bus.write_byte_data(self.addr, MMA8451_REG_CTRL_REG1,
                                 FLAG_ACTIVE | FLAG_LOWNOISE |
                                 self.rate_bit)
        
        # set range
        self.bus.write_byte_data(self.addr, MMA8451_REG_XYZ_DATA_CFG,
                                 MMA8451_RANGES[self.range])
        sleep(0.1)
        
        # set resolution
        self.bus.write_byte_data(self.addr, MMA8451_REG_CTRL_REG2,
                                 MMA8451_RESOLUTION[self.resolution])

        # enable the data-ready interrupt
        self.bus.write_byte_data(self.addr, MMA8451_REG_CTRL_REG4, 0x00) # reset
        self.bus.write_byte_data(self.addr, MMA8451_REG_CTRL_REG4, 0x01)

        # route the data-ready interrupt to pin INT1
        self.bus.write_byte_data(self.addr, MMA8451_REG_CTRL_REG5, 0x00) # reset
        self.bus.write_byte_data(self.addr, MMA8451_REG_CTRL_REG5, 0x01)

        # set FIFO
        self.bus.write_byte_data(self.addr, REG_F_SETUP, 0x00) # reset
        self.bus.write_byte_data(self.addr, REG_F_SETUP, FLAG_FIFO_STOP_ON_OVERFLOW)
        
    def read(self):
        '''
        Read one sample from the accelerometer.

        Parameters
        ----------
        None

        Returns
        -------
        acc_cal : dict
            Accelerometer data in units of m/s^2.
        '''
        overflow, counts = self.check_fifo()
        if counts > 0:
            data = self.bus.read_i2c_block_data(self.addr, MMA8451_REG_OUT_X_MSB, 6)
        
            acc = {'x':0, 'y':0, 'z': 0}

            max_val = 2 ** (14 - 1) - 1
            signed_max = 2**14

            for jaxis, axis in enumerate(['x', 'y', 'z']):
                x = ((data[2*jaxis] << 8) | data[2*jaxis+1]) >> 2
                x -= signed_max if x > max_val else 0
                acc[axis] = int(x)

            calibration = MMA8451_CALIBRATION[self.range]
            acc_cal = dict()
            for axis in ['x', 'y', 'z']:
                acc_cal[axis] = float(acc[axis]) * calibration

            return acc_cal
        
    def check_fifo(self):
        '''
        Check the status of the FIFO buffer on the accelerometer.

        Parameters
        ----------
        None

        Returns
        -------
        overflow : int
            Flag indicating whether the FIFO has overflowed. NB: I have never
            been able to get this to read `True` with the default accelerometer
            settings. Do not rely on this!
        counts : int
            Number of samples currently piled up in the FIFO buffer.
        '''
        status = self.bus.read_byte_data(self.addr, REG_F_STATUS)
        overflow = status & MASK_FIFO_OVERFLOW
        counts = status & MASK_FIFO_COUNTS
        
        return overflow, counts
