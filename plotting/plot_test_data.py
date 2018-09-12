from scipy.signal import periodogram, welch
from python_mma8451.read_accelerometer import read_file, read_for_time
import matplotlib.pyplot as plt
import numpy as np

data, times, rate = read_file('/home/pi/accelerometer/python_mma8451/20180912_182314_accelerometer.dat')
axes = ['x', 'y', 'z']

for jaxis in range(3):
    plt.figure(jaxis+1)
    # f, psd = periodogram(data[:,jaxis], fs=rate, window='hanning')
    f, psd = welch(data[:,jaxis], fs=rate, nperseg=2048, window='hanning')
    plt.semilogy(f, np.sqrt(psd))
    plt.xlabel('frequency [Hz]')
    plt.ylabel('acceleration ASD [g / rtHz]')
    plt.title('{} axis: {:.1f} ug / rtHz'.format(axes[jaxis],
                                                 1e6*np.mean(np.sqrt(psd[(f>3) & (f<15)]))))
    plt.tight_layout()
    plt.savefig(axes[jaxis] + '_axis_data.png', dpi=200)
plt.show()
