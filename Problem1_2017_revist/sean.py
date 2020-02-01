import os
import time
import operator

import numpy as np

# In case doing hyperparam opt
from hyperopt import fmin, tpe, hp, STATUS_OK, Trials, space_eval

from utils import save_object
from pprint import pprint

# Put classes here that may be useful to store info in


class General:
    def __init__(self, args, idx):
        self.score = 0
        self.idx = idx

    def __repr__(self):
        return ("Thing {} with properties".format(
            self.idx))


class Endpoint:
    def __init__(self, Ld, K, cache_info, idx):
        self.data_center_latency = Ld
        self.num_connected_caches = K
        self.connections = np.zeros(shape=(K, 2), dtype=np.uint64)
        for i, c in enumerate(cache_info):
            self.connections[i] = np.array(c)
        # Sort the caches by closest
        self.connections = sorted(self.connections, key=lambda x: x[1])
        self.idx = idx

    def __repr__(self):
        return ("Endpoint {} with Latency {} and {} caches".format(
            self.idx, self.data_center_latency, self.num_connected_caches))

    def get_best_cache(self, caches, video):
        # print(self.idx, video.size, self.connections)
        best_connection = None
        for connection in self.connections:
            if caches[connection[0]].can_fit(video):
                best_connection = connection
                break
        # print(best_connection)
        return best_connection

    def get_lowest_cache(self, caches, video):
        # print(self.idx, video.size, self.connections)
        lowest_latency = self.data_center_latency
        for connection in self.connections:
            if video.idx in caches[connection[0]].videos:
                if connection[1] < lowest_latency:
                    lowest_latency = connection[1]
        # print(best_connection)
        return lowest_latency

    def connects_to(self, cache):
        for connection in self.connections:
            if cache == connection[0]:
                return True, connection[1]
        return False, 1000000


class Request:
    def __init__(self, Rv, Ro, Rn):
        self.video = Rv
        self.endpoint = Ro
        self.num_requests = Rn
        self.best_latency = self.endpoint.data_center_latency

    def __repr__(self):
        return ("Requesting {} for video {} from endpoint {} ".format(
            self.num_requests, self.video.idx, self.endpoint.idx))

    def priority(self, latency_weight=1, request_weight=1, size_weight=1):
        latency = self.endpoint.data_center_latency - self.best_latency
        latency = self.endpoint.data_center_latency if latency == 0 else latency
        return (
            latency_weight * latency *
            request_weight * self.num_requests -
            (size_weight * self.video.size))

    def score(self):
        # print(
        #     self.num_requests,
        #     self.endpoint.data_center_latency,
        #     self.best_latency)
        score = int(self.num_requests * (
            self.endpoint.data_center_latency - self.best_latency))
        # print(score)
        return score


class Video:
    def __init__(self, size, idx):
        self.size = size
        self.idx = idx


class Cache:
    def __init__(self, size, idx):
        self.size = size
        self.idx = idx
        self.videos = []
        self.filled = 0

    def can_fit(self, video):
        return self.filled + video.size <= self.size

    def add_video(self, video):
        self.videos.append(video.idx)
        self.filled += video.size
        if self.filled > self.size:
            raise ValueError("Filled cache {} too much!".format(
                self.idx))

    def reset(self):
        self.videos = []


def sean_solution(info, **kwargs):
    # Do any required setup
    V, E, R, C, X, video_sizes, endpoint_info, request_info = info
    videos = [Video(size, i) for i, size in enumerate(video_sizes)]
    endpoints = [Endpoint(ei[0], ei[1], ei[2], i)
                 for i, ei in enumerate(endpoint_info)]
    request_info.sort(key=operator.itemgetter(0, 1))
    compiled_request_info = []
    i = 0
    while i != len(request_info):
        video = request_info[i][0]
        endpoint = request_info[i][1]
        value = request_info[i][2]
        s = value
        if i != len(request_info) - 1:
            # print(endpoint, request_info[i + 1][1])
            while (request_info[i + 1][1] == endpoint) and (request_info[i + 1][0] == video):
                i += 1
                value = request_info[i][2]
                s += value
                if i == len(request_info) - 1:
                    break
        compiled_request_info.append(
            [request_info[i][0], request_info[i][1], s])
        i += 1

    requests = [Request(videos[ri[0]], endpoints[ri[1]], ri[2])
                for ri in compiled_request_info]
    ids = [[r.video.idx, r.endpoint.idx] for r in requests]
    if len(np.unique(ids, axis=0)) != len(compiled_request_info):
        raise ValueError("Non matching sizes")
    caches = [Cache(X, i) for i in range(C)]

    def objective(args):
        """Actually evaluate a solution here."""
        # Parse out args
        latency_weight = args["latency"]
        request_weight = args["request"]
        size_weight = args["size"]

        # Sort the requests by priority
        request_priorities = np.array([
            r.priority(latency_weight, request_weight, size_weight) for r in requests])
        # print(request_priorities)
        sorted_requests = [x for _, x in sorted(
            zip(request_priorities, requests), key=lambda x: x[0], reverse=True)]

        for i in range(len(sorted_requests)):
            r = sorted_requests[i]
            best_cache = r.endpoint.get_best_cache(caches, r.video)
            if best_cache is not None:
                caches[best_cache[0]].add_video(r.video)
        for i, r in enumerate(sorted_requests):
            sorted_requests[i].best_latency = (
                sorted_requests[i].endpoint.get_lowest_cache(
                    caches, sorted_requests[i].video))

        # This way works, but is terrible as each request is not served
        # Removing changed means score is kept track of during execution
        # But this is actually slower than just calculating after.
        # i = 0
        # while i != len(sorted_requests):
        #     print(i)
        #     r = sorted_requests[i]
        #     i += 1
        #     best_cache = r.endpoint.get_best_cache(caches, r.video)
        #     if best_cache is not None:
        #         caches[best_cache[0]].add_video(r.video)
        #         # sorted_requests[i].best_latency = min(
        #         #     best_cache[1], sorted_requests[i].best_latency)
        #         changed = False
        #         for j in range(len(sorted_requests)):
        #             connect_info = sorted_requests[j].endpoint.connects_to(
        #                 best_cache[0])
        #             if connect_info[0]:
        #                 # print("{} connects to Cache {} in request {}".format(
        #                 #     sorted_requests[j].endpoint,
        #                 #     best_cache[0],
        #                 #     sorted_requests[j]
        #                 # ))
        #                 if sorted_requests[j].video == r.video:
        #                     sorted_requests[j].best_latency = min(
        #                         connect_info[1],
        #                         sorted_requests[j].best_latency)
        #                     changed = True
        #         if changed:
        #             # Sort the requests by priority
        #             request_priorities = np.array([
        #                 r.priority(latency_weight, request_weight, size_weight) for r in requests])
        #             # print(request_priorities)
        #             sorted_requests = [x for _, x in sorted(
        #                 zip(request_priorities, requests), key=lambda x: x[0], reverse=True)]
        #             i = 0
        score = int(np.floor(1000 * (
            np.sum(np.array(
                [r.score() for r in sorted_requests], dtype=np.uint64)) /
            np.sum(np.array(
                [r.num_requests for r in sorted_requests], dtype=np.uint64)))))
        solution = [[cache.idx] + cache.videos for cache in caches]

        return {
            'loss': -score,
            'score': score,
            'solution': solution,
            'eval_time': time.time(),
            'status': STATUS_OK,
        }

    if kwargs.get("search", True):
        trials = Trials()

        # Setup what values the args searching over can have
        space = hp.choice(
            'args',
            [
                {
                    "latency": hp.uniform("arg1", 0, 1),
                    "request": hp.uniform("arg2", 0, 1),
                    "size": hp.uniform("size", 0, 5)
                }
            ])

        # If you know what the best you can do is, pass loss_threshold=-best
        best = fmin(
            objective,
            space=space,
            algo=tpe.suggest,
            max_evals=kwargs.get("num_evals", 10),
            trials=trials)

        # Get the best hyper-params from fmin
        print("Best hyper-parameters found were:", best)
        args = space_eval(space, best)

        # Save the trials to disk
        out_name = os.path.join(
            kwargs["output_dir"], "_" + kwargs["input_name"][:-2] + "pkl")
        save_object(trials, out_name)

    else:
        args = kwargs.get("objective_args")

    best_res = objective(args)
    return best_res["solution"], best_res["score"]
