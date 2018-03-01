import pandas as pd
import numpy as np

def load_data(filename):
    lines = open(filename).readlines()
    rows_num, col_num, vehicles_num, rides_num, ride_bonus, steps_num = [int(val) for val in lines[0].split()]
    data = np.array([[int(x) for x in row.split()] for row in lines[1:]])

    return rows_num, col_num, vehicles_num, rides_num, ride_bonus, steps_num, data
