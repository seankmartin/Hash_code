import numpy as np


def manhat_dist(a1, a2):
    return np.abs(a1[0] - a2[0]) + np.abs(a1[1] + a2[1])


class Taxi:
    def __init__(self, R, C):
        self.location = np.array([0, 0])
        self.rides = []
        self.rows = R
        self.cols = C
        self.time = -1

    def add_ride(self, ride):
        self.rides.append(ride[-1])

    def move_left(self):
        self.location = np.clip(
            self.location - np.array([1, 0]), 0, self.rows)

    def move_right(self):
        self.location = np.clip(
            self.location + np.array([1, 0]), 0, self.rows)

    def move_up(self):
        self.location = np.clip(
            self.location + np.array([0, 1]), 0, self.cols)

    def move_down(self):
        self.location = np.clip(
            self.location - np.array([0, 1]), 0, self.cols)

    def move_random(self):
        rand = np.random.rand()
        print(rand)
        if rand < 0.25:  # move up
            self.move_up()
        elif rand < 0.5:  # move down
            self.move_down()
        elif rand < 0.75:  # move left
            self.move_left()
        else:  # move right
            self.move_right()

    def next(self, curr_time):
        if self.time >= curr_time:
            pass
        else:
            self.move_random()
            self.time += 1

    def can_reach(self, ride):
        manhat_d = manhat_dist(self.location, [ride[0], ride[1]])
        ride_len = manhat_dist([ride[0], ride[1]], [ride[2], ride[3]])
        can_reach = (self.time + manhat_d + ride_len <= ride[5])
        if can_reach:
            self.add_ride(ride)
            self.location = np.array([ride[2], ride[3]])
            if self.time + manhat_d <= ride[4]:
                self.time = ride[4] + ride_len
            else:
                self.time = self.time + manhat_d + ride_len
        return can_reach

    def __repr__(self):
        return ("Taxi located at [{},{}] time {}".format(
            self.location[0], self.location[1], self.time))


def sean_solution(info, **kwargs):
    R, C, F, N, B, T, M = info
    M_sorted = M[M[:, 4].argsort()]
    taxis = [Taxi(R, C) for t in range(F)]
    for ride in M_sorted:
        for taxi in taxis:
            if taxi.can_reach(ride):
                break
    result = [taxi.rides for taxi in taxis]
    return result
