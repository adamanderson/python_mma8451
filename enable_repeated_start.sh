if [ -d "/sys/module/i2c_bcm2708" ]; then
    sudo chmod 666 /sys/module/i2c_bcm2708/parameters/combined
    sudo echo -n 1 > /sys/module/i2c_bcm2708/parameters/combined
else
    echo "Cannot find directory /sys/module/i2c_bcm2708/ for I2C driver. If you "
    echo "are using a newer version of I2C driver, running this script may be "
    echo "unnecessary because newer drivers have repeated-start mode enabled "
    echo "by default."
fi

