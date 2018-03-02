#import pandas as pd
#import numpy as np
from lib import *
import sys

import heapq

class PQ:
    def __init__(self):
        self.data = []

    def enq(self, key, val):
        heapq.heappush(self.data, (-key, val))

    def deq(self):
        key, val = heapq.heappop(self.data)

        return val

    def __len__(self):
        return len(self.data)



def dist(r0, c0, rN, cN):
    return abs(r0 - rN) + abs(c0 - cN)




from collections import defaultdict
import bisect

def main():
    #files = ['a_example', 'b_should_be_easy', 'c_no_hurry', 'd_metropolis', 'e_high_bonus' ]
    files = ['e_high_bonus']

    for fn in files:
        rows_num, col_num, vehicles_num, rides_num, ride_bonus, steps_num, rides = load_data(fn + '.in')

        schedule = [{} for x in range(vehicles_num)]

        rides_fs = rides[:]
        rides_fs.sort(key=lambda x: x[1][5], reverse=True)  # sort by finish time

        rides_ss = rides[:]
        rides_ss.sort(key=lambda x: x[1][5])  # sort by end time

        def dp_chains(taken_rides):
            max_profit_by_cell = defaultdict(tuple)
            next_ride_by_cell = defaultdict(tuple)

            tmp_taken = set()

            for r in rides:
                i, (r0, c0, rN, cN, s, f) = r
                max_profit_by_cell[(rN, cN)] = 0

            for r in rides_fs:
                i, (rr0, rc0, rrN, rcN, rs, rf) = r
                if i in taken_rides:
                    continue

                ride_time = dist(rr0, rc0, rrN, rcN)

                cur_time = rs + ride_time        # TODO: it could be a range = {sf + ride_time, rf}. IF we ACTUALLY take anything else then rf - then we should update rf

                # find first  index of the ride which ends later than current one is finished
                si = bisect.bisect([x[1][5] for x in rides_ss], cur_time)

                # loop through  'next rides', pick the one with max profit
                max_profit = 0
                max_profit_ride = None
                for nr in rides_ss[si:]:
                    ni, (nr0, nc0, nrN, ncN, ns, nf) = nr

                    if i == ni or ni in taken_rides or ni in tmp_taken:
                        continue

                    time_to_ride = dist(rrN, rcN, nr0, nc0)
                    ride_time = dist(nr0, nc0, nrN, ncN)

                    if cur_time + time_to_ride + ride_time > nf:
                        continue

                    potential_profit = ride_time
                    if cur_time + time_to_ride <= ns:
                        potential_profit += ride_bonus

                    if max_profit_by_cell[(nrN, ncN)] + potential_profit > max_profit:
                        max_profit = max_profit_by_cell[(nrN, ncN)] + potential_profit
                        max_profit_ride = ni

                max_profit_by_cell[(rrN, rcN)] = max_profit
                next_ride_by_cell[(rrN, rcN)] = max_profit_ride
                tmp_taken.add(max_profit_ride)


            return max_profit_by_cell, next_ride_by_cell

        def get_ride_chain(max_profit_ride, next_ride_by_cell):
            i = max_profit_ride
            if i is None:
                return []

            res = set()

            while True:
                i, (r0, c0, rN, cN, s, f) = rides[i]
                if i in res:
                    break

                res.add(i)

                if next_ride_by_cell[(rN, cN)] is None:
                    break

                i = next_ride_by_cell[(rN, cN)]



            return res


        def get_schedule():
            taken_rides = set()

            rides_ss1 = rides[:]
            rides_ss1.sort(key=lambda x: x[1][4])  # sort by start time

            for c in range(vehicles_num):
                max_profit_by_cell, next_ride_by_cell = dp_chains(taken_rides)


                max_profit = 0
                max_profit_ride = None
                for nr in rides_ss1:
                    i, (r0, c0, rN, cN, s, f) = nr

                    if i in taken_rides:
                        continue

                    time_to_ride = dist(0, 0, r0, c0)
                    ride_time = dist(r0, c0, rN, cN)

                    potential_profit = ride_time
                    if time_to_ride <= s:
                        potential_profit += ride_bonus

                    if max_profit_by_cell[(rN, cN)] + potential_profit > max_profit and time_to_ride + ride_time < f:
                        max_profit = max_profit_by_cell[(rN, cN)] + potential_profit
                        max_profit_ride = i


                if max_profit_ride is None:
                    break

                schedule[c] = get_ride_chain(max_profit_ride, next_ride_by_cell)   # update taken rides
                taken_rides.update(schedule[c])


        def solution0():
            # TODO: improve key

            pq = PQ()
            for r in rides:
                i, (r0, c0, rN, cN, s, f) = r
                ride_time = dist(r0, c0, rN, cN)

                pq.enq(ride_time, r)

            schedule = [[] for x in range(vehicles_num)]

            def most_profitable_ride(c, t, car_pos):
                tmp = []
                found = False
                while len(pq):
                    r = pq.deq()

                    i, (r0, c0, rN, cN, s, f) = r

                    ride_time = dist(r0, c0, rN, cN)
                    time_to_ride = dist(*car_pos[c], r0, c0)

                    if t + time_to_ride + ride_time <= f:
                        found = True
                        break
                    else:
                        tmp.append((ride_time, r))

                for t1, r1 in tmp:
                    pq.enq(t1, r1)

                if found:
                    return r
                else:
                    return None

            def closest_ride(c, t, car_pos, taken_rides):
                pq = PQ()

                # find first  index of the ride which ends later than current one is finished
                si = bisect.bisect([x[1][5] for x in rides_ss], t)
                for r in rides_ss[si:]:
                    i, (r0, c0, rN, cN, s, f) = r

                    if i in taken_rides:
                        continue

                    ride_time = dist(r0, c0, rN, cN)
                    time_to_ride = dist(*car_pos[c], r0, c0)
                    time_to_ride = time_to_ride if time_to_ride > 0 else 0.1

                    if t + time_to_ride + ride_time <= f:
                        value = 10 * ride_time / time_to_ride
                        if t + time_to_ride <= s:
                            value += ride_bonus / time_to_ride

                        pq.enq(value, r)

                if len(pq):
                    return pq.deq()
                else:
                    return None


            car_pos = [(0, 0)] * vehicles_num
            taken_rides = set()
            for c in range(vehicles_num):
                t = 0
                car_pos[c] = (0, 0)
                print('#')
                while t < steps_num and len(pq):
                    print('.', end='')
                    #r = most_profitable_ride(c, t, car_pos)
                    r = closest_ride(c, t, car_pos, taken_rides)
                    if r is None:
                        break

                    i, (r0, c0, rN, cN, s, f) = r

                    schedule[c].append(i)
                    taken_rides.add(i)

                    ride_time = dist(r0, c0, rN, cN)
                    time_to_ride = dist(*car_pos[c], r0, c0)

                    t += max(time_to_ride, s - t) + ride_time
                    car_pos[c] = (rN, cN)
            return schedule


        def solution1():
            get_schedule()

        schedule = solution0()
        #solution1()

        of = open(fn + '.out', mode='w')
        for s in schedule:
            print(len(s))
            of.write("{} {}\n".format(len(s),' '.join([str(x) for x in s])))

        of.close()





if __name__ == '__main__':
    main()