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
        for i in range(9):
            for j in range(9):
                self.constraints[(i, j)] = self.__generate_constraints__(i, j)
                self.assign[(i, j)] = {puzzle[i][j]} if puzzle[i][j] != 0 else set(range(1, 10))
        # infer for assigned values
        for i in range(9):
            for j in range(9):
                if puzzle[i][j] != 0:
                    inference = self.__infer__((i, j))
                    self.__difference__(inference)

    def __generate_constraints__(self, x, y):
        samerow = [(x, i) for i in range(9)]
        samecol = [(i, y) for i in range(9)]
        sameblock = []
        for i in range((x // 3) * 3, (x // 3) * 3 + 3):
            for j in range((y // 3) * 3, (y // 3) * 3 + 3):
                sameblock.append((i, j))
        return [self.Constraint(sameblock), self.Constraint(samerow), self.Constraint(samecol)]

    def __init_inference__(self):
        inference = dict()
        for i in range(9):
            for j in range(9):
                inference[(i, j)] = set()
        return inference

    def __infer__(self, var):
        inference = self.__init_inference__()
        for c in self.constraints[var]:
            assigned = [(x, self.assign[x]) for x in c.vars]
            by_length = [dict(), dict(), dict(), dict(), dict(), dict(), dict(), dict()]
            for idx, value in assigned:
                if len(value) == 1:
                    v = value.pop()
                    for x in c.vars:
                        if x != idx:
                            inference[x].add(v)
                    value.add(v)
                else:
                    value = tuple(value)
                    if value in by_length[len(value)-2]:
                        by_length[len(value) - 2][value].append(idx)
                    else:
                        by_length[len(value) - 2][value] = [idx]
            for i in range(0, 7):
                for value in by_length[i]:
                    idxs = by_length[i][value]
                    if len(idxs) == i+2:
                        for x in c.vars:
                            if x not in idxs:
                                inference[x].update(value)
                    elif len(idxs) > i+2:
                        return None
            for x in c.vars:
                newDomain = self.assign[x] - inference[x]
                if len(newDomain) == 0:
                    return None
        return inference

    # apply minimum remaining value heuristics
    def __get_unassigned_var__(self):
        unassignedVars = []
        for i in range(9):
            for j in range(9):
                if self.ans[i][j] == 0:
                    unassignedVars.append((i, j))
        if len(unassignedVars) == 0:
            return None

        min = unassignedVars[0]
        for var in unassignedVars:
            if len(self.assign[var]) < len(self.assign[min]):
                min = var
        return min

    def __assign_to_sodoku__(self):
        for i in range(9):
            for j in range(9):
                self.ans[i][j] = self.assign[(i, j)].pop()

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

    def solve(self):
        # TODO: Write your code here
        var = self.__get_unassigned_var__()
        if var == None:
            self.__assign_to_sodoku__()
            return self.ans

        self.ans[var[0]][var[1]] = 10

        reversedDomain = list(self.assign[var])
        reversedDomain.reverse()
        for value in reversedDomain:
            domain = self.assign[var]
            self.assign[var] = {value}
            inference = self.__infer__(var)
            if inference is not None:
                self.__clean_inference__(inference)
                self.__difference__(inference)
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
