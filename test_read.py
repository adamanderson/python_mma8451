from read_accelerometer import read_file, read_for_time
import argparse as ap
from datetime import datetime

P0 = ap.ArgumentParser(description='Script to test reading accelerometer data.',
                       formatter_class=ap.RawTextHelpFormatter)
subparser = P0.add_subparsers(dest='mode')
P1 = subparser.add_parser('readfile', help='Reads a specific data file.')
P1.add_argument('filename', default=None, help='Name of file to read.')
P2 = subparser.add_parser('readtimerange', help='Reads a specific time range '
                          'from all data files in a directory.')
P2.add_argument('datadir', default=None, help='Directory containing data to '
                'search for time range.')
P2.add_argument('starttime', default=None, type=float,
                help='UNIX timestamp of start of time range requested.')
P2.add_argument('stoptime', default=None, type=float,
                help='UNIX timestamp of end of time range requested.')
args = P0.parse_args()

if args.mode == 'readfile':
    data, times, rate = read_file(args.filename)
    print(data)
    print(times)
elif args.mode == 'readtimerange':
    data, times = read_for_time(args.datadir,
                                start=datetime.utcfromtimestamp(args.starttime),
                                stop=datetime.utcfromtimestamp(args.stoptime))
    print(data)
    print(times)
    print(times[0])
    print(times[-1])
