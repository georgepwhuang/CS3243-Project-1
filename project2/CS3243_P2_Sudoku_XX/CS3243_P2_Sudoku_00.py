# CS3243 Introduction to Artificial Intelligence
# Project 2

import sys
import copy

# Running script: given code can be run with the command:
# python file.py, ./path/to/init_state.txt ./output/output.txt


class Sudoku(object):
    class Constraint(object):
        def __init__(self, x):
            self.vars = set(x)

    def __init__(self, puzzle):
        # you may add more attributes if you need
        self.puzzle = puzzle  # self.puzzle is a list of lists
        self.ans = copy.deepcopy(puzzle)  # self.ans is a list of lists

        self.assign = dict()
        self.constraints = dict()
        self.currC = None
        self.constraint_list = self.__generate_constraints__()
        self.currR = None
        for i in range(9):
            for j in range(9):
                self.constraints[(i, j)] = self.__get_constraints__(i, j)
                self.assign[(i, j)] = {puzzle[i][j]} if puzzle[i][j] != 0 else set(range(1, 10))
        # infer for assigned values
        for i in range(9):
            for j in range(9):
                if puzzle[i][j] != 0:
                    inference = self.__infer__((i, j))
                    self.__difference__(inference)

    def __generate_constraints__(self):
        samecol = [self.Constraint([(x, i) for i in range(9)]) for x in range(9)]
        samerow = [self.Constraint([(i, y) for i in range(9)]) for y in range(9)]
        sameblock = []
        for x in range(3):
            for y in range(3):
                block = []
                for i in range(x * 3, x * 3 + 3):
                    for j in range(y * 3, y * 3 + 3):
                        block.append((i, j))
                sameblock.append(self.Constraint(block))
        return [samecol, samerow, sameblock]

    def __get_constraints__(self, x, y):
        block_no = x // 3 * 3 + y // 3
        return [self.constraint_list[0][x], self.constraint_list[1][y], self.constraint_list[2][block_no]]

    def __init_inference__(self):
        inference = dict()
        for i in range(9):
            for j in range(9):
                inference[(i, j)] = set()
        return inference

    def __get_inference_size__(self, inference):
        if inference is None:
            return 0
        sol = sum([len(value) for value in inference.values()])
        return sol

    def __infer__(self, var):
        inference = self.__init_inference__()
        for c in self.constraints[var]:
            assigned = [(x, self.assign[x]) for x in c.vars]
            by_length = [dict(), dict(), dict(), dict(),
                         dict(), dict(), dict(), dict()]
            for idx, value in assigned:
                if len(value) == 1:
                    v = value.pop()
                    for x in c.vars:
                        if x != idx:
                            inference[x].add(v)
                    value.add(v)
                else:
                    value = tuple(value)
                    if value in by_length[len(value) - 2]:
                        by_length[len(value) - 2][value].append(idx)
                    else:
                        by_length[len(value) - 2][value] = [idx]
            for i in range(0, 7):
                for value in by_length[i]:
                    idxs = by_length[i][value]
                    if len(idxs) == i + 2:
                        for x in c.vars:
                            if x not in idxs:
                                inference[x].update(value)
                    elif len(idxs) > i + 2:
                        return None
            for x in c.vars:
                newDomain = self.assign[x] - inference[x]
                if len(newDomain) == 0:
                    return None
        return inference

    # apply least constraining value heuristics
    def __sort_domain__(self, pos):
        valueDomain = []
        for val in self.assign[pos]:
            self.assign[pos] = {val}
            inference = self.__infer__(pos)
            if inference is not None:
                self.__clean_inference__(inference)
                size = self.__get_inference_size__(inference)
                valueDomain.append((size, val, inference))
        valueDomain.sort(key=lambda x: x[0])
        return valueDomain

    def __all_assigned__(self, id, type="col"):
        for i in range(9):
            if type == "col" and self.ans[i][id] == 0:
                return False
            elif type == "row" and self.ans[id][i] == 0:
                return False
        return True

    def __set_currId__(self):
        mrv_id = self.__getMRV_col__()

        if mrv_id and mrv_id[0] == "row":
            self.currR = mrv_id[1]
            self.currC = None
        elif mrv_id:
            self.currC = mrv_id[1]
            self.currR = None
        else:
            self.currC = None
            self.currR = None

    # apply minimum remaining value heuristics
    def __get_unassigned_var__(self):
        if (not self.currR and not self.currC):
            self.__set_currId__()
        elif self.currR and self.__all_assigned__(self.currR, "row"):
            self.__set_currId__()
        elif self.currC and self.__all_assigned__(self.currC, "col"):
            self.__set_currId__()

        if self.currC is None and self.currR is None:
            return None

        min = None
        if self.currC is not None:
            for i in range(9):
                l = len(self.assign[(i, self.currC)])
                if self.ans[i][self.currC] != 0:
                    continue
                if not min:
                    min = (i, self.currC)
                    continue
                if l < len(self.assign[min]):
                    min = (i, self.currC)
        elif self.currR is not None:
            for i in range(9):
                l = len(self.assign[(self.currR, i)])
                if self.ans[self.currR][i] != 0:
                    continue
                if not min:
                    min = (self.currR, i)
                    continue
                if l < len(self.assign[min]):
                    min = (self.currR, i)

        return min

    def __getMRV_col__(self):
        crvs = []
        rrvs = []
        for i in range(9):
            crv = 0
            rrv = 0
            for j in range(9):
                if self.ans[j][i] == 0:
                    var = (j, i)
                    crv += len(self.assign[var])
                if self.ans[i][j] == 0:
                    var = (i, j)
                    rrv += len(self.assign[var])
            crvs.append(crv)
            rrvs.append(rrv)

        if max(crvs) == 0:
            return None

        crvs = [81 if x == 0 else x for x in crvs]
        rrvs = [81 if x == 0 else x for x in rrvs]
        min_crv = min(crvs)
        min_rrv = min(rrvs)

        if min_crv < min_rrv:
            return ("col", crvs.index(min_crv))
        else:
            return ("row", rrvs.index(min_rrv))

    def __assign_to_sodoku__(self):
        for key in self.assign:
            self.ans[key[0]][key[1]] = self.assign[key].pop()

    def __difference__(self, inference):
        for key, value in inference.items():
            if len(value) != 0:
                self.assign[key] = self.assign[key] - value

    def __union__(self, inference):
        for key, value in inference.items():
            if len(value) != 0:
                self.assign[key] = self.assign[key].union(value)

    def __clean_inference__(self, inference):
        for key, value in inference.items():
            if len(value) != 0:
                inference[key] = self.assign[key].intersection(value)

    def __is_arc_consistent__(self):
        for i in range(9):
            numUnassignR = 0
            numUnassignC = 0
            rowDomain = set()
            colDomain = set()
            for j in range(9):
                if self.ans[i][j] == 0:
                    numUnassignR += 1
                    rowDomain = rowDomain.union(self.assign[(i, j)])
                if self.ans[j][i] == 0:
                    numUnassignC += 1
                    colDomain = colDomain.union(self.assign[(j, i)])
            if len(rowDomain) < numUnassignR or len(colDomain) < numUnassignC:
                return False

        return True

    def solve(self):
        # TODO: Write your code here
        var = self.__get_unassigned_var__()
        if var is None:
            self.__assign_to_sodoku__()
            return self.ans

        self.ans[var[0]][var[1]] = 10

        domain = self.assign[var]
        sortedDomain = self.__sort_domain__(var)
        for size, value, inference in sortedDomain:
            self.assign[var] = {value}
            if inference is not None:
                self.__difference__(inference)
                if self.__is_arc_consistent__():
                    result = self.solve()
                    if result is not None:
                        return result
                self.__union__(inference)
        self.assign[var] = domain

        self.ans[var[0]][var[1]] = 0
        return None

    # you may add more classes/functions if you think is useful
    # However, ensure all the classes/functions are in this file ONLY
    # Note that our evaluation scripts only call the solve method.
    # Any other methods that you write should be used within the solve() method.


if __name__ == "__main__":
    # STRICTLY do NOT modify the code in the main function here
    if len(sys.argv) != 3:
        print ("\nUsage: python CS3243_P2_Sudoku_XX.py input.txt output.txt\n")
        raise ValueError("Wrong number of arguments!")

    try:
        f = open(sys.argv[1], 'r')
    except IOError:
        print ("\nUsage: python CS3243_P2_Sudoku_XX.py input.txt output.txt\n")
        raise IOError("Input file not found!")

    puzzle = [[0 for i in range(9)] for j in range(9)]
    lines = f.readlines()

    i, j = 0, 0
    for line in lines:
        for number in line:
            if '0' <= number <= '9':
                puzzle[i][j] = int(number)
                j += 1
                if j == 9:
                    i += 1
                    j = 0

    sudoku = Sudoku(puzzle)
    ans = sudoku.solve()

    with open(sys.argv[2], 'a') as f:
        for i in range(9):
            for j in range(9):
                f.write(str(ans[i][j]) + " ")
            f.write("\n")
