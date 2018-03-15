#import pandas as pd
#import numpy as np
from lib import *
import sys

import heapq

def dist(r0, c0, rN, cN):
    return abs(r0 - rN) + abs(c0 - cN)


def intersect_ranges(range1, range2):
    a, b = range1
    c, d = range2

    return (max(a, c), min(b, d))


def shift_range(range1, ofs):
    a, b = range1
    return (a + ofs, b + ofs)


from collections import defaultdict
import bisect
from datetime import datetime

def main():
    #files = ['a_example', 'b_should_be_easy', 'c_no_hurry', 'd_metropolis', 'e_high_bonus' ]
    files = ['c_no_hurry2.5k']

    for fn in files:
        print('{} Processing {}'.format(datetime.now(), fn))
        rows_num, col_num, vehicles_num, rides_num, ride_bonus, steps_num, rides = load_data(fn + '.in')

        schedule = [{} for x in range(vehicles_num)]

        rides_fs = rides[:]
        rides_fs.sort(key=lambda x: x[1][5], reverse=True)  # sort by finish time

        rides_ss = rides[:]
        rides_ss.sort(key=lambda x: x[1][5])  # sort by end time

        def check_rides():
            starts = set()
            ends  = set()
            for r in rides:
                i, (r0, c0, rN, cN, s, f) = r

                if (r0, c0) in starts:
                    print('dup start')
                else:
                    starts.add((r0, c0))

                if (rN, cN) in ends:
                    print('dup end')
                else:
                    ends.add((rN, cN))


            print('DONE rides check.')

        def dp_chains(taken_rides):
            max_profit_by_cell = defaultdict(tuple)
            next_ride_by_cell = defaultdict(tuple)
            ride_finish_ranges = defaultdict(int)

            tmp_taken = set()

            for r in rides:
                i, (r0, c0, rN, cN, s, f) = r
                max_profit_by_cell[(rN, cN)] = 0
                next_ride_by_cell[(rN, cN)] = None

                ride_time = dist(r0, c0, rN, cN)
                ride_finish_ranges[i] = (s + ride_time, f)

            for r in rides_fs:
                i, (rr0, rc0, rrN, rcN, rs, rf) = r
                if i in taken_rides or i in tmp_taken:
                    continue

                # range
                ride_finish_range = ride_finish_ranges[i]
                cur_time_range = ride_finish_range

                # find first  index of the ride which ends later than current one is finished
                si = bisect.bisect([x[1][5] for x in rides_ss], cur_time_range[0])

                # loop through  'next rides', pick the one with max profit
                max_profit = 0
                max_profit_ride = None
                max_cur_time_range = None
                for nr in rides_ss[si:]:
                    ni, (nr0, nc0, nrN, ncN, ns, nf) = nr
                    ride_finish_range = ride_finish_ranges[ni]

                    if i == ni or ni in taken_rides:
                        continue

                    # TODO: ride could be a part of multiple chains BUT there should be no loops
                    if ni in tmp_taken:
                        continue

                    time_to_ride = dist(rrN, rcN, nr0, nc0)
                    ride_time = dist(nr0, nc0, nrN, ncN)

                    possible_finish_range = intersect_ranges(ride_finish_range, shift_range(cur_time_range, time_to_ride + ride_time))
                    if possible_finish_range[0] > possible_finish_range[1]:
                        continue

                    potential_profit = ride_time            #TODO: Consider potential_profit = ride_time - time_to_ride

                    if cur_time_range[0] + time_to_ride <= ns:
                        potential_profit += ride_bonus
                        possible_finish_range = (possible_finish_range[0], ns)

                    if max_profit_by_cell[(nrN, ncN)] + potential_profit > max_profit:
                        max_profit = max_profit_by_cell[(nrN, ncN)] + potential_profit
                        max_profit_ride = ni
                        max_cur_time_range = (cur_time_range[0], possible_finish_range[1] - time_to_ride - ride_time)

                '''
                ride A also finishes in point X. A is last ride in the chain
                ride B finishes in point X. It starts a chain. Info for X is overwritten.
                ride A is picked as most profitable & fitting ride after ride C.
                => after ride C chain B.. is  actually used and all rides are missed                                
                '''

                max_profit_by_cell[(rrN, rcN)] = max_profit
                next_ride_by_cell[(rrN, rcN)] = max_profit_ride



                tmp_taken.add(max_profit_ride)
                if max_cur_time_range is not None:
                    ride_finish_ranges[i] = max_cur_time_range


            return max_profit_by_cell, next_ride_by_cell, ride_finish_ranges

        def get_ride_chain(max_profit_ride, next_ride_by_cell):
            i = max_profit_ride
            if i is None:
                return []

            res = []

            while True:
                i, (r0, c0, rN, cN, s, f) = rides[i]

                res.append(i)

                if next_ride_by_cell[(rN, cN)] is None:
                    break

                i = next_ride_by_cell[(rN, cN)]



            return res

        def validate(chain):
            cur_time = 0
            car_coords = (0, 0)
            mc = 0
            for ride_ix in chain:
                nr = rides[ride_ix]
                i, (r0, c0, rN, cN, s, f) = nr

                car_r, car_c = car_coords
                time_to_ride = dist(car_r, car_c, r0, c0)
                ride_time = dist(r0, c0, rN, cN)

                if cur_time + time_to_ride + ride_time > f:
                    print('missed ride ' + str(i))
                    mc += 1
                    #return

                car_coords = (rN, cN)
                cur_time += time_to_ride + ride_time

            if mc:
                print('{}/{} rides missed'.format(mc, len(chain)))
                return False

            return True




        def get_schedule():
            taken_rides = set()

            rides_ss1 = rides[:]
            rides_ss1.sort(key=lambda x: x[1][4])  # sort by start time

            for c in range(vehicles_num):
                if c % 10 == 0:
                    print('car {} of {}'.format(c, vehicles_num))

                max_profit_by_cell, next_ride_by_cell, ride_finish_ranges = dp_chains(taken_rides)
                print('#')

                max_profit = 0
                max_profit_ride = None
                for nr in rides_ss1:
                    i, (r0, c0, rN, cN, s, f) = nr

                    if i in taken_rides:
                        continue

                    time_to_ride = dist(0, 0, r0, c0)
                    ride_time = dist(r0, c0, rN, cN)

                    # TODO: consider:
                    # time to start ride is too big to finish the chain in time
                    # PROBABLY it's not a problem? We would partially miss the chain
                    # NO PROBLEM: algorithm skips start of the chain until it finds most profitable chain residual
                    if time_to_ride > ride_finish_ranges[i][1] - ride_time:
                        continue

                    potential_profit = ride_time
                    if time_to_ride <= s:
                        potential_profit += ride_bonus

                    if max_profit_by_cell[(rN, cN)] + potential_profit > max_profit and time_to_ride + ride_time < f:
                        max_profit = max_profit_by_cell[(rN, cN)] + potential_profit
                        max_profit_ride = i


                if max_profit_ride is None:
                    break

                schedule[c] = get_ride_chain(max_profit_ride, next_ride_by_cell)   # update taken rides

                if not validate(schedule[c]):
                    for ri in schedule[c]:
                        print(ri, ride_finish_ranges[ri])

                taken_rides.update(schedule[c])


        def solution():
            get_schedule()

        check_rides()
        solution()

        of = open(fn + '.out', mode='w')
        for s in schedule:
            print(len(s))
            of.write("{} {}\n".format(len(s),' '.join([str(x) for x in s])))

        of.close()





if __name__ == '__main__':
    main()