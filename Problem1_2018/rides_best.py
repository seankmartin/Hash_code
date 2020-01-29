from __future__ import print_function
import sys
import numpy as np


# SEAN MARTIN
# Stefano
# Given a list of pre-booked rides in a city and a fleet of self-driving vehicles, assign the rides to vehicles, so
# that riders get to their destinations on time.

# The objective is to assign rides to vehicles
# Get points for rides that are completed in time, more precisely:

# For every ride that finishes on time (or early), you will earn points proportional to the distance of that ride;
# plus an additional bonus if the ride also started precisely on time.


# Read the file in the required format for hash code
def read_file(filename):
    '''Read File'''

    with open(filename, 'r') as f:
        line = f.readline()
        # Read the first line
        rows, columns, num_vehicles, num_rides, bonus, total_time = [
            int(n) for n in line.split()]

        # Need to change
        # Read num_rides lines and store in a num_rides * 6 array
        rides = np.zeros([num_rides, 6], dtype=int)
        for i in range(num_rides):
            line = f.readline()
            rides[i] = np.fromstring(line, dtype=int, sep=" ")

    # error check
    print(rides)

    return rows, columns, num_vehicles, num_rides, bonus, total_time, rides


def write_file(filename, output):
    # print('Score:', np.sum(dead), file=sys.stderr)
    with open(filename, 'w') as f:
        for e in output:
            f.write('{} '.format(len(e)))
            string = ' '.join(map(str, e))
            f.write(string)
            f.write('\n')
            # [print(' '.join(str(x) for x in e)) for e in output]


def distance(a, b, x, y):
    return abs(a - x) + abs(b - y)


def add_ride(index, ride, cars, car_rides):
    # Add the index
    car_rides[index].append(ride[6])
    cars[index][0] = ride[2]
    cars[index][1] = ride[3]
    distance_from_start = distance(
        cars[index][0], cars[index][1], ride[0], ride[1])
    cars[index][2] += distance_from_start
    if(cars[index][2] < ride[4]):
        cars[index][2] = ride[4]
    cars[index][2] += distance(ride[0], ride[1], ride[2], ride[3])


def main():
    # change the filename here
    filenames = ["a_example.in", "b_should_be_easy.in",
                 "c_no_hurry.in", "d_metropolis.in", "e_high_bonus.in"]
    for filename in filenames:
        rows, columns, num_vehicles, num_rides, bonus, total_time, rides = read_file(
            filename)
        cars = np.zeros((num_vehicles, 4))
        # x, y, timestep, ride-flag
        # List of empty lists
        result = [[] for i in range(num_vehicles)]

        # Add index as a column
        indices = np.array([x for x in range(num_rides)]).reshape(num_rides, 1)
        rides = np.concatenate((rides, indices), axis=1)
        sorted_rides = rides[rides[:, 4].argsort()]
        rides = sorted_rides
        print(rides)
        # car consists of the following
        # 0 current_row, 1 current_col, 2 current_time, 3 ride_flag

        # ride consists of the following
        # 0 start_row, 1 start_col, 2 end_row, 3 end_col, 4 start_time, 5 latest_time, 6 ID
        for ride in rides:
            car = cars[0]
            distance_from_start = distance(car[0], car[1], ride[0], ride[1])
            best_index = 0
            best_distance = distance_from_start + car[2]

            for i in range(num_vehicles):
                car = cars[i]
                distance_from_start = distance(
                    car[0], car[1], ride[0], ride[1])
                start_end_distance = distance(
                    ride[0], ride[1], ride[2], ride[3])
                starts_in_time = False
                arrives_in_time = False
                if distance_from_start + car[2] <= ride[4]:
                    starts_in_time = True
                if distance_from_start + car[2] + start_end_distance <= ride[5]:
                    arrives_in_time = True

                if arrives_in_time and distance_from_start + car[2] < best_distance:
                    best_distance = distance_from_start + car[2]
                    best_index = i
            add_ride(best_index, ride, cars, result)

        outfile = filename[:-2] + "out"
        write_file(outfile, result)


if __name__ == '__main__':
    main()
