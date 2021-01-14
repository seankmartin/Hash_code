import os
import time

import numpy as np

# In case doing hyperparam opt
try:
    from hyperopt import fmin, tpe, hp, STATUS_OK, Trials, space_eval
except:
    pass

from utils import save_object


class Book:

    def __init__(self, score, idx):
        self.score = score
        self.idx = idx
        self.scanned = False

    def __repr__(self):
        return ("Book {} with score {}, scanned {}".format(
            self.idx, self.score, self.scanned))


class Library:
    def __init__(self, books, sign_time, books_per_day, days, idx):
        self.books = books
        self.sign_time = sign_time
        self.books_per_day = books_per_day
        self.signed_up = False
        self.idx = idx
        self.score = 0
        self.max_days = days

    # TODO don't pass duplicate books

    def max_books(self, t):
        earliest_start_time = t + self.sign_time
        time_available = self.max_days - earliest_start_time
        if (time_available <= 0):
            return 0
        max_books = time_available * self.books_per_day
        max_books = min(max_books, len(self.books))
        return max_books

    def calc_score(self, t, books):
        max_books = self.max_books(t)

        # TODO consider when need to sort
        score = 0
        i = 0
        j = 0
        while (j != max_books) and (i < (len(self.books))):
            if not books[self.books[i]].scanned:
                score += books[self.books[i]].score
                j = j + 1
            i = i + 1
        self.score = score
        self.calc_overall_score()

    def books_to_scan(self, t, books):
        max_books = self.max_books(t)
        books_to_scan = []
        i = 0
        j = 0
        # for book in books:
        #     print(book)
        while (j != max_books) and (i < (len(self.books))):
            if not books[self.books[i]].scanned:
                # print("adding book {} to lib {}".format(
                #     self.books[i], self.idx
                # ))
                books_to_scan.append(self.books[i])
                j = j + 1
            i = i + 1
        # print("loop ended with j: {} and i: {}".format(j, i))
        # print("max books are", max_books)
        return books_to_scan

    def calc_overall_score(self):
        self.overall_score = (
            (self.a * self.score) - (self.sign_time ** self.b))

    def set_args(self, args):
        self.a, self.b = args

    def __repr__(self):
        return ("Library {} with books {}, takes {} to sign up, {} books per day, is signed up {}".format(
            self.idx, self.books, self.sign_time, self.books_per_day, self.signed_up))


def sean_solution(info, **kwargs):
    """
    This solution is designed to be performed as follows:
    1.  Setup anything, such as arrays or sorting.
        Also break down info into components.
    2.  objective can access anything from the main body part.
        As such, pass anything extra which may be needed
        (such as hyper-params) into objective as args (a dict)
        perform the actual solving logic part here.
    3.  At the end, can search over hyper-paramters (the args)
        That are passed into objective.
        However, if doing a simple function, this part
        can be safely ignored.

    """
    (B, L, D, book_scores, library_info) = info

    # Make the books
    books = []
    for i in range(B):
        books.append(Book(book_scores[i], i))

    # Make the libraries
    libraries = []
    for i in range(L):
        idx, N, T, M, book_ids = library_info[i]
        lib_books = []
        for i in range(N):
            book_idx = book_ids[i]
            lib_books.append(book_idx)
        sorted_lib_books = sorted(
            lib_books, key=lambda x: books[x].score, reverse=True)
        library = Library(sorted_lib_books, T, M, D, idx)
        libraries.append(library)

    # if np.mean(book_scores) == book_scores[0]:
    #     print('not sorting')
    #     should_sort = False
    # else:
    #     should_sort = True
    should_sort = False

    def objective(args):
        """Actually write the solution part here."""
        # TODO Parse out the args if needed
        curr_time = 0
        end_info = []
        sorted_libraries = libraries
        a = args.get("a", 1)
        b = args.get("b", 1)
        for lib in sorted_libraries:
            lib.set_args((a, b))

        if not should_sort:
            for lib in sorted_libraries:
                lib.calc_score(curr_time, books)

            sorted_libraries = sorted(
                sorted_libraries, key=lambda x: x.overall_score, reverse=True)

        while curr_time < D:
            if should_sort:
                for lib in sorted_libraries:
                    lib.calc_score(curr_time, books)

                sorted_libraries = sorted(
                    sorted_libraries, key=lambda x: x.overall_score, reverse=True)
            best_lib = sorted_libraries[0]
            books_to_scan = best_lib.books_to_scan(curr_time, books)
            if (len(books_to_scan) != 0):
                book_ids_out = []
                for b in books_to_scan:
                    book_ids_out.append(b)
                    books[b].scanned = True
                info_to_ret = (best_lib.idx, len(books_to_scan), book_ids_out)
                end_info.append(info_to_ret)

            if len(sorted_libraries) == 1:
                break
            curr_time += best_lib.sign_time
            sorted_libraries = sorted_libraries[1:]

        score = 0
        for i, b in enumerate(books):
            if b.scanned:
                score += b.score
            books[i].scanned = False

        # Return something flexible that can be used with hyperopt
        # Main point is that it has score and solution.
        return {
            'loss': -score,
            'score': score,
            'solution': end_info,
            'eval_time': time.time(),
            'status': STATUS_OK,
        }

    # Ignore this bit if not searching hyper_parameters!
    if kwargs.get("search", True):
        trials = Trials()

        # TODO Setup what values the args searching over can have
        space = hp.choice(
            'args',
            [
                {
                    "a": hp.uniform("a", 0, 10),
                    "b": hp.uniform("b", 0, 10)
                }
            ])

        # TODO If you know the best you do, pass loss_threshold=-best
        # Do hyper-param searching - possible pass per filename num_evals
        best = fmin(
            objective,
            space=space,
            algo=tpe.suggest,
            max_evals=kwargs.get("num_evals", 40),
            trials=trials)

        # Get the best hyper-params from fmin
        print("Best hyper-parameters found were:", best)
        args = space_eval(space, best)
        result = objective(args)

        # Save the trials to disk
        # These trials can be printed using print_trial_info in utils
        out_name = os.path.join(
            kwargs["output_dir"], "_" + kwargs["input_name"][:-2] + "pkl")
        save_object(trials, out_name)

    else:
        # By default, this is just an empty dictionary.
        args = kwargs.get("objective_args")

    result = objective(args)
    return result["solution"], result["score"]
