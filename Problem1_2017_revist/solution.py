"""Skeleton code for our solution, to be updated on the day."""

import os
from datetime import datetime
from time import time
from copy import copy

import numpy as np

from utils import line_to_data
from utils import zip_dir
from utils import add_params
from hyper_params import return_hyperparam_list

# import your solution here
from matheus import matheus_solution
from ham import ham_solution
from sean import sean_solution


def read_file(input_location):
    """Return info from the input_location."""
    with open(input_location, 'r') as f:
        V, E, R, C, X = line_to_data(f.readline(), np_array=False, dtype=int)
        video_sizes = line_to_data(f.readline(), dtype=np.uint64)
        endpoint_info = []
        for i in range(E):
            line = f.readline()
            Ld, K = line_to_data(line, np_array=False, dtype=int)
            cache_info = []
            for j in range(K):
                c, Lc = line_to_data(f.readline(), np_array=False, dtype=int)
                cache_info.append([c, Lc])
            endpoint_info.append([Ld, K, cache_info])
        request_info = []
        for i in range(R):
            Rv, Re, Rn = line_to_data(f.readline(), np_array=False, dtype=int)
            request_info.append([Rv, Re, Rn])
        info = (V, E, R, C, X, video_sizes, endpoint_info, request_info)
    return info


def write_file(output_location, solution):
    """Write to output_location containing the solution."""
    with open(output_location, 'w') as f:
        f.write("{}\n".format(len(solution)))
        for cache in solution:
            for val in cache:
                f.write("{} ".format(int(val)))
            f.write("\n")


def print_solution(solution):
    """Print things relevant to the solution."""
    # TODO print actually useful things, like summary information.
    return
    print("\tSolution is: {}".format(solution))


def run(input_location, output_location, method, **kwargs):
    """Read the file, calculate solution, and write the results."""
    start_time = time()
    info = read_file(input_location)
    solution, score = method(info, **kwargs)
    write_file(output_location, solution)
    print("\tCompleted in {:.2f} seconds".format(time() - start_time))
    print_solution(solution)
    print("Scored:", score)
    return score


def main(method, filenames, parameter_list, skip, seed):
    """Parse the input information and run the main loop."""

    # Do setup
    here = os.path.dirname(os.path.realpath(__file__))
    np.random.seed(seed)  # to reproduce results
    in_dir = "input_files"
    locations = [os.path.join(here, in_dir, filename)
                 for filename in filenames]
    scores = np.zeros(len(locations))

    # Create a new directory for a run to compare to old solutions
    now = datetime.now()
    current_time = now.strftime("%H-%M-%S")
    out_dir = current_time
    out_dir = os.path.join(here, "outputs", out_dir)
    os.makedirs(out_dir, exist_ok=True)

    # Zip up the directory
    zip_loc = os.path.join(out_dir, "_Source.zip")
    zip_dir(here, zip_loc, ".py")

    # Start the execution loop
    with open(os.path.join(out_dir, "Result.txt"), "w") as f:
        for i, (input_location, params) in enumerate(zip(locations, parameter_list)):

            # Ignore some files optionally
            if skip[i]:
                print("Skipping {}".format(input_location))
                continue

            # Setup and print what is happening
            print("Working on {} with parameters {} using {}:".format(
                os.path.basename(input_location), params, method.__name__))
            output_location = os.path.join(
                out_dir,
                os.path.basename(input_location[:-3]) + ".out")

            # Put anything which may be useful to all solutions here
            params_copy = copy(params)
            params_copy["output_dir"] = out_dir
            params_copy["input_name"] = os.path.basename(input_location)

            # Actual running happens here
            score = run(input_location, output_location, method, **params_copy)

            # Write the achieved score to disk
            scores[i] = score
            f.write("{} {}\n".format(
                os.path.basename(input_location)[:-3], score))

        # What was the final score?
        last_str = "Total score: {}".format(np.sum(scores))
        f.write(last_str)
        print(last_str)


if __name__ == "__main__":
    """This is where things you should change are."""
    # Change the method here to the desired one
    method = sean_solution

    # Decide here if you are doing any searching
    use_hyper_params = True

    # TODO change this to be the actual filenames
    filenames = [
        "example.in", "me_at_the_zoo.in", "trending_today.in",
        "videos_worth_spreading.in", "kittens.in"]

    # TODO change this to specific parameters for each file
    hyper_params = return_hyperparam_list()
    param_list = [{}, {}, {}, {}, {}]
    param_list = add_params(param_list, "iter", ["1", "2", "3", "4", "5"])
    param_list = add_params(param_list, "search", not use_hyper_params)
    if use_hyper_params:
        param_list = add_params(param_list, "objective_args", hyper_params)

    # Indicate which files to run
    skip = [False, False, False, False, False]
    seed = 1  # Set the random seed for reproducibility
    main(method, filenames, param_list, skip, seed)
True