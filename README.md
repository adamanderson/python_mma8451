# python_mma8451
Python driver for the MMA8451 on Raspberry Pi. Currently requires python3 and tested on Raspberry Pi 3.

# Setup Notes
In order for higher-rate readout to not fill up the FIFO buffer on the chip, you may need to increase the I2C clock speed. With the FIFO buffer enabled, I did not encounter data loss with a clock rate of 200kHz on a Raspberry Pi 3 at 400Hz sampling. There were some losses with 800Hz sampling, although this may be possible to mitigate by setting a higher clock rate. To set the clock rate to 200kHz, for example, edit `/boot/config.txt` such that the following lines are present:
```
dtparam=i2c_arm=on
dtparam=i2c_arm_baudrate=200000
```

It is also necessary to run the script `init_i2c.sh` in order to configure the I2C driver for repeated start queries. This is necessary so that data for all sensor axes can be read once before they are updated. This script will need to be run upon each restart of the Raspberry Pi.
