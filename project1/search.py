# search.py
# ---------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
#
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


"""
In search.py, you will implement generic search algorithms which are called by
Pacman agents (in searchAgents.py).
"""

from game import Actions
import util


class SearchProblem:
    """
    This class outlines the structure of a search problem, but doesn't implement
    any of the methods (in object-oriented terminology: an abstract class).

    You do not need to change anything in this class, ever.
    """

    def getStartState(self):
        """
        Returns the start state for the search problem.
        """
        util.raiseNotDefined()

    def isGoalState(self, state):
        """
          state: Search state

        Returns True if and only if the state is a valid goal state.
        """
        util.raiseNotDefined()

    def getSuccessors(self, state):
        """
          state: Search state

        For a given state, this should return a list of triples, (successor,
        action, stepCost), where 'successor' is a successor to the current
        state, 'action' is the action required to get there, and 'stepCost' is
        the incremental cost of expanding to that successor.
        """
        util.raiseNotDefined()

    def getCostOfActions(self, actions):
        """
         actions: A list of actions to take

        This method returns the total cost of a particular sequence of actions.
        The sequence must be composed of legal moves.
        """
        util.raiseNotDefined()


def tinyMazeSearch(problem):
    """
    Returns a sequence of moves that solves tinyMaze.  For any other maze, the
    sequence of moves will be incorrect, so only use this for tinyMaze.
    """
    from game import Directions
    s = Directions.SOUTH
    w = Directions.WEST
    return [s, s, w, s, w, w, s, w]


def depthFirstSearch(problem):
    """
    Search the deepest nodes in the search tree first.

    Your search algorithm needs to return a list of actions that reaches the
    goal. Make sure to implement a graph search algorithm.

    To get started, you might want to try some of these simple commands to
    understand the search problem that is being passed in:

    print "Start:", problem.getStartState()
    print "Is the start a goal?", problem.isGoalState(problem.getStartState())
    print "Start's successors:", problem.getSuccessors(problem.getStartState())
    """
    explored = set()
    path = dict()  # {to: (from, act)}
    frontier = util.Stack()  # store edge
    start = problem.getStartState()
    frontier.push(start)
    while not frontier.isEmpty():
        u = frontier.pop()
        explored.add(u)

        if problem.isGoalState(u):
            return genActionFromPath(start, u, path)

        for v in problem.getSuccessors(u):
            if v[0] not in explored:
                frontier.push(v[0])
                path[v[0]] = (u, v[1])


def genActionFromPath(start, end, path):
    actions = []
    curr = end
    while curr != start:
        action = path[curr][1]
        actions.append(action)
        curr = path[curr][0]
    actions.reverse()
    return actions


def breadthFirstSearch(problem):
    """Search the shallowest nodes in the search tree first."""
    frontier = util.PriorityQueueWithFunction(lambda x: x[2])
    explored = dict()
    origin = (problem.getStartState(), None, 0)
    frontier.push(origin)
    explored[problem.getStartState()] = None
    while not frontier.isEmpty():
        u = frontier.pop()
        if problem.isGoalState(u[0]):
            cur = u
            result = [u[1]]
            while explored[cur[0]] != origin:
                cur = explored[cur[0]]
                result.append(cur[1])
            result.reverse()
            return result
        for v in problem.getSuccessors(u[0]):
            if not v[0] in explored.keys():
                explored[v[0]] = u
                frontier.push(v)


def uniformCostSearch(problem):
    """Search the node of least total cost first."""
    "*** YOUR CODE HERE ***"
    explored = set()
    path = dict()  # {to: (from, act)}
    frontier = util.PriorityQueue()  # store edge
    gHat = dict()
    start = problem.getStartState()
    frontier.push(start, 0)
    gHat[start] = 0
    while not frontier.isEmpty():
        u = frontier.pop()
        explored.add(u)

        if problem.isGoalState(u):
            return genActionFromPath(start, u, path)

        for v in problem.getSuccessors(u):
            if v[0] not in explored:
                updateGHatAndPath(gHat, path, u, v)
                frontier.update(v[0], gHat[v[0]])


def updateGHatAndPath(gHat, path, fron, action):
    (to, act, cost) = action
    if to in gHat:
        path[to] = (fron, act) if gHat[fron] + cost < gHat[to] else path[to]
        gHat[to] = min(gHat[to], gHat[fron] + cost)
    else:
        gHat[to] = gHat[fron] + cost
        path[to] = (fron, act)


def nullHeuristic(state, problem=None):
    """
    A heuristic function estimates the cost from the current state to the nearest
    goal in the provided SearchProblem.  This heuristic is trivial.
    """
    return 0


def aStarSearch(problem, heuristic=nullHeuristic):
    """Search the node that has the lowest combined cost and heuristic first."""
    frontier = util.PriorityQueue()
    explored = set()
    cost = dict()
    predecessor = dict()
    origin = problem.getStartState()
    frontier.push(origin, 0 + heuristic(origin, problem))
    explored.add(origin)
    cost[origin] = 0
    predecessor[origin] = None
    while not frontier.isEmpty():
        u = frontier.pop()
        if problem.isGoalState(u):
            cur = u
            result = []
            while predecessor[cur] != None:
                cur = predecessor[cur]
                result.append(cur[1])
                cur = cur[0]
            result.reverse()
            return result
        explored.add(u)
        for v in problem.getSuccessors(u):
            if not v[0] in explored:
                if not v[0] in cost.keys() or cost[v[0]] > cost[u] + v[2]:
                    cost[v[0]] = cost[u] + v[2]
                    frontier.update(v[0], cost[v[0]] +
                                    heuristic(v[0], problem))
                    predecessor[v[0]] = (u, v[1])


# Abbreviations
bfs = breadthFirstSearch
dfs = depthFirstSearch
astar = aStarSearch
ucs = uniformCostSearch
