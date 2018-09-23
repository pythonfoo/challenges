#!/usr/bin/env python

# info: changed my solution to brute-force all the things
# Output format: <word>,<line>,<column>,<direction>,<length>
import math
import numpy as np


class WordWithCoords():
    def __init__(self, word, direction, index_x, index_y):
        self.word = word
        self.direction = direction
        self.index_x = index_x
        self.index_y = index_y

    def __repr__(self):
        return "{},{},{},{},{}".format(self.word, self.direction, self.index_y, self.index_x, len(self.word))


def main(infile, wordlist, outfile):
    input_grid= None
    raw_grid = None
    biggusdictus = {}

    # read and sanitize
    with open(infile, 'r') as inf:
        input_grid = inf.read().split("\n")
        input_grid = [s.upper() for s in input_grid]
        raw_grid = [s.upper() for s in inf.read()]

    with open(wordlist, 'r') as wl:
        reference = wl.read().split("\n")
        reference = [s.upper().replace("\r", "") for s in reference]
        for r in reference:
            biggusdictus[r] = True

    max_x = len(input_grid[0])
    max_y = len(input_grid)

    found = []

    #print(input_grid)
    twodgrid = grid_to_2d([list(x) for x in input_grid])
    print(np.triu(twodgrid))



    # NE, diagonal up
    #todo

    # E, left to right
    for i in range(0, max_y):
        for wrd in scan(input_grid[i], direction="NE", x=None, y=i, dictionary=biggusdictus):
            found.append(wrd)

    # SE, diagonal down
    # todo
    #print("diag1")
    #for i in range(max_x):
    #    print(diag(list(input_grid[i:max_x])))
    #print("diag2")
    #for i in range(max_x):
    #    print(diag(transpose(list(input_grid[i:max_x]), max_x=5, max_y =max_y)))





    # down
    transposed_grid = transpose(list(input_grid), max_x, max_y)
    for i in range(0, max_x):
        for wrd in scan(transposed_grid[i], direction="S", x=None, y=i, dictionary=biggusdictus):
            found.append(wrd)





    print(found)

    #grid = [list(input_grid[i]) for i in range(0, max_y)]
    #print(grid[0:3][1])

    #for i in range(0, max_x):
    #    for j in range(0, max_y):
    #        print(list(input_grid[j])[i], i, j)

    #for j in range(0, max_y):
    #    #for i in range(0, max_x):
    #    print("".join(list(input_grid[j])[0:max_x]), i, j)


    #for j in range(0, max_y):
        #for i in range(0, max_x):
    #    print("".join(list(input_grid[0:max_y])[j]),  j)

    #l = list(input_grid)
    #print(l)
    #t= [map(list, map(None, *l))]
    #print(t)


    #t2 = transpose(list(input_grid), max_x, max_y)
   # print(t2)

    #t3 = diag(list(input_grid))
   # print(t3)
    #for  i in range(max_x):
    #    print(diag(list(input_grid[i:max_x])))

    t3 = diag2(list(input_grid))
    print(t3)
    t3 = diag(list(input_grid))
    print(t3)
    #for  i in range(max_x):
    #    print(diag2(list(input_grid[i:max_x])))


    # S, down

    # S, down
    #for i in range(0, max_x):
    #    input_grid[]


    #for i in input_grid:
    #    print(i)
    #    scan(i, bigfatdict)
   #     for s in scan(string=i, valid_words=reference):
   #         print(s)

    #for res in scan(string="abcatabab", valid_words=reference):
    #    print(res)
    #for t in scan(string="abcatalogbazoombcats", valid_words=reference):
    #    print(t)
    with open(outfile, 'w') as out:
        out.write(".")


def grid_to_2d(grid):
    res = np.array(grid)
    print("numpy ", res)
    return np.array(list(grid))


def transpose(lst, max_x, max_y):
    res = []
    i = 0
    while i < max_x:
        j = 0
        col = []
        while j < max_y-1:
            col.append(lst[j][i])
            j = j + 1
        res.append(col)
        i = i + 1
    return ["".join(n) for n in res]


def diag(lst):  # todo cleanup...
    res = []
    i = 0
    while i < len(lst):
        col = []
        j = i
        while j < math.inf:
            try:
                col.append(lst[j][j])
                j = j + 1
                i = i + 1
            except IndexError as e:
                break

        res.append("".join(col))
        i = i+1
    return res


def diag2(lst):  # todo cleanup...
    res = []
    i = 0
    while i < len(lst):
        col = []
        j = i+1
        while j < math.inf:
            try:
                col.append(lst[i][j])
                j = j + 1
                i = i + 1
            except IndexError as e:
                break

        res.append("".join(col))
        i = i+1
    return res






def get_all_substr(input_string):
    # stackoverflow ftw  https://stackoverflow.com/questions/22469997/how-to-get-all-the-contiguous-substrings-of-a-string-in-python
    max_len = len(input_string)
    return [(input_string[i:j + 1], j)for i in range(max_len) for j in range(i, max_len)]


def scan(string, direction, x, y, dictionary):
    #print(get_all_substr(string))
    for (s, j) in get_all_substr(string):
        if s in dictionary:
            yield WordWithCoords(s, direction=direction, index_x=j, index_y=y)

    #for v in valid_words:
    #    if not v:
    #        continue
    #    #print(v, string)
    #    if v in string:
    #        print(v, string)
    #        print(string.index(v))
    #        yield True


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', dest="infile", required=True)
    parser.add_argument('-w', dest="wordlist", required=True)
    parser.add_argument('-o', dest="outfile", required=True)
    results = parser.parse_args()
    main(results.infile, results.wordlist, results.outfile)

