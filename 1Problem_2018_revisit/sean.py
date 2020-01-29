import numpy as np


def manhat_dist(a1, a2):
    return np.abs(a1[0] - a2[0]) + np.abs(a1[1] - a2[1])


class Taxi:
    def __init__(self, R, C, B, idx):
        self.location = np.array([0, 0])
        self.rides = []
        self.rows = R
        self.cols = C
        self.bonus = B
        self.time = 0
        self.score = 0
        self.taxi_num = idx

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
        return can_reach, manhat_d

    def add_ride(self, ride):
        manhat_d = manhat_dist(self.location, [ride[0], ride[1]])
        ride_len = manhat_dist([ride[0], ride[1]], [ride[2], ride[3]])
        self.location = np.array([ride[2], ride[3]])
        bonus = 0
        if self.time + manhat_d <= ride[4]:
            self.time = ride[4] + ride_len
            bonus = self.bonus
        else:
            self.time = self.time + manhat_d + ride_len
        self.rides.append(ride[-1])
        self.score = self.score + ride_len + bonus

    def __repr__(self):
        return ("Taxi {} located at [{},{}] time {}".format(
            self.taxi_num, self.location[0], self.location[1], self.time))


def sean_solution(info, **kwargs):
    R, C, F, N, B, T, M = info
    M_sorted = M[M[:, 4].argsort()]
    taxis = [Taxi(R, C, B, i) for i in range(F)]
    for ride in M_sorted:
        best_dist, best_taxi = 100000000, None
        for taxi in taxis:
            can_reach, dist = taxi.can_reach(ride)
            if can_reach:
                if dist == 1:
                    best_taxi = taxi
                    break
                elif dist < best_dist:
                    best_dist = dist
                    best_taxi = taxi
        if best_taxi is not None:
            best_taxi.add_ride(ride)
            # print(best_taxi)
            # input("Press Enter to continue")

    result = [taxi.rides for taxi in taxis]
    score = np.sum([taxi.score for taxi in taxis])
    return result, score
