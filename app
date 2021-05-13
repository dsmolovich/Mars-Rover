#!/usr/bin/python3

from nasa import *
import fileinput
import sys

nasa_control = NasaControl()
line_number=0
for line in fileinput.input():
    line_number += 1
    try:
        output = nasa_control.parse_line(line.strip())
        if isinstance(output, tuple):
            print("{}:{} {} {}".format(output[0], output[1], output[2], output[3]))
    except Exception as e:
        print("ERROR: line {} - {}".format(line_number, e), file=sys.stderr)