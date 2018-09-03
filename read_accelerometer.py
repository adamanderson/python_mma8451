import numpy as np
import struct
import os
import logging
from glob import glob

header_size = 12
block_size = 24

def read_header(f):
    data = struct.unpack('df', f.read(header_size))
    start = data[0]
    rate = data[1]
    return start, rate


def read_file(fname):
    nbytes = os.stat(fname).st_size
    nblocks = (nbytes-header_size) / block_size

    acc_data = np.zeros((nblocks, 3))
    times = np.zeros(nblocks)

    jblock = 0
    with open(fname, 'rb') as f:
        # read header
        start, rate = read_header(f)
        
        # read body
        while True:
            rawdata = f.read(block_size)
            if not rawdata:
                break
            data = struct.unpack('fffd', rawdata)
            acc_data[jblock,:] = data[:3]
            times[jblock] = data[3]
            jblock += 1
            
    if jblock != nblocks:
        logging.warning('Number of samples in file is different than expected '
                       '({} vs. {} expected). Possible file corruption.'
                       .format(jblock, nblocks))
        
    return acc_data, times, rate


def read_for_time(datadir, start, stop):
    fnames = np.sort(glob(os.path.join(datadir, '*accelerometer.dat')))
    start_times = np.zeros(len(fnames))
    all_data = np.empty((0,3), float)
    all_times = np.array([])

    start_ts = start.timestamp()
    stop_ts = stop.timestamp()
    
    for jf, fname in enumerate(fnames):
        with open(fname, 'rb') as f:
            start, rate = read_header(f)
            start_times[jf] = start

    ind_times = np.arange(0,len(fnames))
    ind_times = ind_times[(start_times > start_ts) & (start_times < stop_ts)]
    if len(ind_times) != 0:
        if np.min(ind_times) != 0:
            ind_times = np.insert(ind_times, 0, np.min(ind_times)-1)
        if np.max(ind_times) != len(fnames)-1:
            ind_times = np.insert(ind_times, 0, np.max(ind_times)+1)
    else:
        if start_ts < np.min(start_times) and \
           stop_ts < np.min(start_times):
            ind_times = np.array([0])
        elif start_ts > np.max(start_times) and \
             stop_ts > np.max(start_times):
            ind_times = np.array([len(fnames)-1])

    for fname in fnames[ind_times]:
        acc_data_in_file, times_in_file, rate = read_file(fname)
        all_data = np.append(all_data, acc_data_in_file[(times_in_file > start_ts) &
                                                        (times_in_file < stop_ts),:],
                             axis=0)
        all_times = np.append(all_times, times_in_file[(times_in_file > start_ts) &
                                                       (times_in_file < stop_ts)])
        
    return all_data, all_times
