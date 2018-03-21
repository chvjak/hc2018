def dist1(r0, c0, rN, cN):
    return abs(r0 - rN) + abs(c0 - cN)


def load_data(filename):
    lines = open(filename).readlines()
    rows_num, col_num, vehicles_num, rides_num, ride_bonus, steps_num = [int(val) for val in lines[0].split()]
    data = [(i,[int(x) for x in row.split()]) for i, row in enumerate(lines[1:])]

    return rows_num, col_num, vehicles_num, rides_num, ride_bonus, steps_num, data

def evaluate(filename):
    rows_num, col_num, vehicles_num, rides_num, ride_bonus, steps_num, rides = load_data(filename + '.in')

    lines = open(filename + '.out').readlines()
    chains = [([int(x) for x in row.split()]) for row in lines]

    score = 0
    time_now = 0
    car_pos = (0, 0)
    for chain in chains:
        for ride_ix in chain[1:]:
            i, (r0, c0, rN, cN, s, f) = rides[ride_ix]

            score += dist1(r0, c0, rN, cN)
            time_now += dist1(*car_pos, r0, c0)

            if time_now <= s:
                score += ride_bonus

            time_now += dist1(r0, c0, rN, cN)
            car_pos = (rN, cN)

            rides_num -= 1

    print('{} rides left'.format(rides_num))
    return score

print(evaluate('d_metropolis'))
print(evaluate('e_high_bonus'))
