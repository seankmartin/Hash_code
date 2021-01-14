import numpy as np
import os


def read_pizza(input_location):
    """
    Will return M, N, slices - int, int, ndarray

    M is the Max number of slices we can have
    N is the number of different types of pizza
    """
    def line_to_int(line, use_np=True):
        l = [int(x) for x in line.split(" ")]
        if use_np:
            return np.array(l)
        else:
            return l

    with open(input_location, 'r') as f:
        M, N = line_to_int(f.readline(), use_np=False)
        slices = line_to_int(f.readline())
    return M, N, slices

def sum_from_highest(M, slices):
    if np.sum(slices) < M:
        return slices
    total = 0
    temp = np.array([])
    for j in range(len(slices)-1, -1, -1):
        sl = slices[j]
        total += sl
        if total <= M:
            temp = np.append(temp, j)
        else:
            total -= sl
    return temp

def permute_slices(M, slices, num_permutes):
    indices = np.array([j for j in range(slices.size)])
    best_val = 0
    best_arr = []
    for i in range(num_permutes):
        perm = np.random.permutation(indices)
        total = 0
        temp = np.array([])
        for j in perm:
            sl = slices[j]
            total += sl
            if total <= M:
                temp = np.append(temp, j)
            else:
                total -= sl
        if total > best_val:
            best_val = total
            best_arr = temp
            if best_val == M:
                return best_arr
    return best_arr

def write_pizza(output_location, pizzas):
    with open(output_location, 'w') as f:
        f.write(str(len(pizzas))+"\n")
        for p_val in pizzas:
            f.write("{} ".format(int(p_val)))

def main(input_location, num_permutes):
    M, N, slices=read_pizza(input_location)
    result = permute_slices(M, slices, num_permutes)
    output_location=input_location[:-3] + ".out"
    write_pizza(output_location, result)


if __name__ == "__main__":
    num_permutes = 100000
    in_dir="input_files"
    for location in os.listdir(in_dir):
        location_abs=os.path.join(in_dir, location)
        if os.path.isfile(location_abs):
            if location_abs[-2:] == "in":
                main(location_abs, num_permutes)
