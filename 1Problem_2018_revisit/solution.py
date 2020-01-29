"""Skeleton code for our solution, to be updated on the day."""

import numpy as np
import os
from datetime import datetime
from time import time

from utils import line_to_data, zip_dir
# import your solution here
# from matheus import matheus_solution
# from ham import ham_solution
from sean import sean_solution


def read_file(input_location):
    """
    Return info from the input_location.

    Returns a tuple ordered as
    R - number of rows in the grid
    C - number of cols in the grid
    F - number of vehicles in the fleet
    N - number of rides
    B - per ride bonus for starting on time
    T - number of steps in the simulation
    M - matrix consisting of N rows and 7 columns.
        Each column describes a ride, and is structured as
        (numbers indicate indices):
        ride 6: from [0, 1] to [2, 3], earliest start 4, latest finish 5
    """
    with open(input_location, 'r') as f:
        R, C, F, N, B, T = line_to_data(
            f.readline(), np_array=False, dtype=int)
        ride_info = np.zeros(shape=(N, 7))
        for i in range(N):
            ride_info[i][:-1] = line_to_data(f.readline(), dtype=int)
            ride_info[i][-1] = i
        info = (R, C, F, N, B, T, ride_info)
    return info


def write_file(output_location, solution):
    """Write to output_location containing the solution."""
    with open(output_location, 'w') as f:
        for row in solution:
            f.write("{}".format(int(len(row))))
            for val in row:
                f.write(" {}".format(int(val)))
            f.write("\n")


def print_solution(solution):
    """TODO this should be updated with things relevant to the solution."""
    # If there is nothing useful, just return
    print("\tSolution is: {}".format(solution))


def run(input_location, output_location, method, **kwargs):
    """Read the file, calculate solution, and write the results."""
    start_time = time()
    info = read_file(input_location)
    solution = method(info, **kwargs)
    solution, score = solution
    write_file(output_location, solution)
    print("\tCompleted in {:.2f} seconds".format(time() - start_time))
    print_solution(score)
    return score


def main(method, filenames, parameter_list, do, seed=1):
    """Parse the input information and run the main loop."""
    np.random.seed(seed)  # to reproduce results

    here = os.path.dirname(os.path.realpath(__file__))

    # Create a new directory for a run to compare to old solutions
    now = datetime.now()
    current_time = now.strftime("%H-%M-%S")
    out_dir = current_time
    out_dir = os.path.join(here, "outputs", out_dir)
    os.makedirs(out_dir, exist_ok=True)

    # Zip up the directory
    zip_loc = os.path.join(out_dir, "_Source.zip")
    zip_dir(here, zip_loc, ".py")

    in_dir = "input_files"
    locations = [os.path.join(here, in_dir, filename)
                 for filename in filenames]
    scores = np.zeros(len(locations))
    with open(os.path.join(out_dir, "Result.txt"), "w") as f:
        for i, (location, parameters) in enumerate(zip(locations, parameter_list)):
            if do[i]:
                print("Working on {} with parameters {} using {}:".format(
                    os.path.basename(location), parameters, method.__name__))
                output_location = os.path.join(
                    out_dir,
                    os.path.basename(location[:-3]) + ".out")
                score = run(location, output_location, method, **parameters)
                scores[i] = score

                f.write("{} {}\n".format(
                    os.path.basename(location)[:-3], score))
        last_str = "Total score: {}".format(np.sum(np.array(scores)))
        f.write(last_str)
        print(last_str)


if __name__ == "__main__":
    """This is where things you should change are."""
    # Change the method here to the desired one
    method = sean_solution

    # # TODO change this to be the actual filenames
    filenames = [
        "a_example.in", "b_should_be_easy.in",
        "c_no_hurry.in", "d_metropolis.in", "e_high_bonus.in"]

    # # TODO change this to specific paramters for each file
    parameter_list = [
        {},
        {},
        {},
        {},
        {}
    ]

    do = [True, True, True, True, True]
    seed = 1
    main(method, filenames, parameter_list, do, seed)
