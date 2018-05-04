#!/usr/bin/env python

import os
import numpy as np


def shots2cnv(directory, out_file, station_list, pha_wgt):
    """
    Convert OBS detected active-source shots into VELEST .CNV file.
    Note: uses OBS as source location and shot location as receiver

    Inputs:
        - dir: path of input files named as [sta_code].time and containing the
                following space-delimited columns:
                    - shot
                    - shot_id
                    - shot_lon
                    - shot_lat
                    - offset (km)
                    - travel time (ms)
                    - water depth at shot location (km)
        - outcnv: name of output cnv file
        - station_list: space-delimited station location file containing:
                - station_code
                - lat(dd)
                - long
                - depth (m)
        - pha_wgt: Default phase and weight assignment (e.g. P0)
    """

    # Prepare output file
    w = open(out_file, "w")

    # Set dummy parameters for OBS sources
    dummy_OBS_origin = "121212 1212 12.12"  # date-time string
    dummy_OBS_mag = 9.99  # magnitude
    dummy_azgap = 0.00  # maximum azimuthal gap
    dummy_rms_res = 0.00

    # Read station locations into list
    sta_locs = [(l.split()[0], float(l.split()[1]), float(l.split()[2]),
                 float(l.split()[3])) for l in open(station_list)]

    for file in os.listdir(directory):
        if file.endswith(".time"):
            file_path = os.path.join(directory, file)
            print(file_path)

            station_code = file.split(".")[0]

            # Find matching station location
            for station in sta_locs:
                if station[0] == station_code:
                    sta_lat = station[1]
                    sta_lon = station[2]
                    sta_depth = station[3] / 1000.0

            # Choose whether lats and longs are degrees north or south and
            # east or west
            if sta_lat > 0:
                NS = "N"
            else:
                NS = "S"
            if sta_lon > 0:
                EW = "E"
            else:
                EW = "W"

            # Write origin details
            w.write(station_code)
            w.write("{:} {:7.4f}{:} {:8.4f}{:} {:6.2f} {:6.2f} {:6g} {:9.2f}\n"
                    .format(dummy_OBS_origin, np.abs(sta_lat), NS,
                            np.abs(sta_lon), EW, sta_depth, dummy_OBS_mag,
                            dummy_azgap, dummy_rms_res))

            # Now write the arrivals
            arrival_file = open(file_path, "r")

            # Count number of arrivals in file
            num_shots = sum(1 for line in open(file_path))

            # Skip event if no shots
            if num_shots == 0:
                continue

            # Now write the formatted arrival phases
            for n, arrival in enumerate(arrival_file):
                n = n + 1
                shot_name = arrival.split()[0]
                arrival_time = float(arrival.split()[6]) / 1000.0

                # Regular writing
                if n != num_shots and (n % 6) != 0:
                    w.write("{:4s}{:2s}{:6.2f}".format(shot_name, pha_wgt,
                                                       arrival_time))
                # Add newline character if last shot in file or a factor of 6
                else:
                    w.write("{:4s}{:2s}{:6.2f}\n".format(shot_name, pha_wgt,
                                                         arrival_time))

            # Blank line between events
            w.write("\n")
