#import pandas as pd
#import numpy as np

def load_data(filename):
    lines = open(filename).readlines()
    rows_num, col_num, vehicles_num, rides_num, ride_bonus, steps_num = [int(val) for val in lines[0].split()]
    data = [(i,[int(x) for x in row.split()]) for i, row in enumerate(lines[1:])]

    return rows_num, col_num, vehicles_num, rides_num, ride_bonus, steps_num, data
