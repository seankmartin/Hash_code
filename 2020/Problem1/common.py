"""Please place things here which may be useful to everyone."""
import numpy as np
# Put books and libraries here

# Put sorting here of the books


class General:
    """
    These is a template for a general class with some
    things which can be useful.
    """

    def __init__(self, args, idx):
        self.score = 0
        self.idx = idx

    def __repr__(self):
        return ("Thing {} with properties".format(
            self.idx))


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
            self.a * self.score / (self.sign_time ** self.b))

    def set_args(self, args):
        self.a, self.b = args

    def __repr__(self):
        return ("Library {} with books {}, takes {} to sign up, {} books per day, is signed up {}".format(
            self.idx, self.books, self.sign_time, self.books_per_day, self.signed_up))


def solve(info, **kwargs):
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

    sorted_libraries = libraries
    curr_time = 0
    end_info = []

    if np.mean(book_scores) == book_scores[0]:
        print('not sorting')
        should_sort = False
    else:
        should_sort = True

    for lib in sorted_libraries:
        lib.set_args((1, 1))

    if not should_sort:
        for lib in sorted_libraries:
            lib.calc_score(curr_time, books)

        sorted_libraries = sorted(
            sorted_libraries, key=lambda x: x.overall_score, reverse=True)
        # sorted_libraries = sorted(
        #     sorted_libraries, key=lambda x: x.sign_time)

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
    for b in books:
        if b.scanned:
            score += b.score

    return end_info, score
