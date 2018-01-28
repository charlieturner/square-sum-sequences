import random
import datetime
import array
from math import ceil, floor, sqrt

#
# this code takes a previous hamiltonian cycle (length N) for
# the square-sum problem and makes a new cycle of length N + 1
#
# it is utterly bereft of any theoretical support; the author of
# this code has no idea why it works.
#
# this code is in the public domain.
#
# the core idea is that given a hamiltonian cycle that solves the
# problem for N, you can trivially convert this into a
# (non-cycle) solution for N+1.  at that point, just
# randomly perturb the solution until a hamiltonian cycle
# for N+1 is found.  then repeat.
#
# while this code has been run to N in excess of 100,000,
# the more significant observation is that the amount of work
# -- the number of perturbations -- done per step appears
# to be independent of the size of the solution.
#

class square_sum:

    #
    # constant-memory edge list
    #
    class square_edge:

        def __init__(self, v, N):
            self.define(v, N)

        def __getitem__(self, k):

            #
            # end-of-list for generators
            #
            if k >= self.limit:
                raise IndexError

            #
            # skip the hole
            #
            if k >= self.hole:
                k += 1

            #
            # the k'th edge is (n0 + k)**2 - vertex
            #
            n = self.n0 + k
            return n*n - self.vertex

        def __len__(self):
            return self.limit

        def __repr__(self):
            #
            # a debugging convenience
            #
            return str([x for x in self])

        def define(self, v, N):

            assert N >= 1 and v >= 1 and v <= N

            #
            # the vertex number
            #
            self.vertex = v

            #
            # the next square after the vertex number is n0
            #
            self.n0 = int(ceil(sqrt(self.vertex + 1)))

            #
            # how many squares
            #
            L = N if self.vertex < N else N - 1
            self.limit = int(floor(sqrt(self.vertex + L) - self.n0)) + 1

            #
            # remove the 'v + v == square' hole
            #
            k = int(round(sqrt(2*self.vertex)))
            if k*k == 2*self.vertex:
                self.hole = k - self.n0
                self.limit -= 1
            else:
                self.hole = self.limit

    #
    # the argument must be a hamiltonian path
    #
    def __init__(self, previous = None):

        #
        # set of applicable squares
        #
        # ,,, it may be faster to do integer square-roots
        #
        def mk_squares(N):
            S = set()
            k = 1
            while True:
                s = k*k
                if s > 2*N - 1:
                    break
                S.add(s)
                k += 1
            return S

        #
        # edges
        #
        def mk_edges(S, N):
            return { vertex: square_sum.square_edge(vertex, N) for vertex in range(1, N + 1) }

        #
        # force construction of new index
        #
        self.index = None
        self.iterations = 0

        #
        # if no previous state, start with the first known cycle
        #
        if previous is None:

            #
            # the first hamiltonian cycle is length 32;  this result is due to Landon Kryger, which
            # he published in a comment to https://www.youtube.com/watch?v=7_ph5djCCnM
            #
            self.state = array.array('I', [1, 8, 28, 21, 4, 32, 17, 19, 30, 6, 3, 13, 12, 24,
                    25, 11, 5, 31, 18, 7, 29, 20, 16, 9, 27, 22, 14, 2, 23, 26, 10, 15])
            N = len(self.state)
            self.squares = mk_squares(N)
            self.edges = mk_edges(self.squares, N)
            return

        #
        # next state is +1 from previous
        #
        N = len(previous.state) + 1
        self.squares = mk_squares(N)
        self.edges = mk_edges(self.squares, N)

        #
        # now rotate and augment previous hamiltonian cycle to
        # a hamiltonian path (now no longer a cycle!) one size larger
        #
        k = previous.state.index(self.random_vertex(N))

        self.state = array.array('I')
        self.state.append(N)
        self.state.extend(previous.state[k:])
        self.state.extend(previous.state[0:k])

    def __len__(self):
        return len(self.state)

    #
    # given a "from" vertex, return a random "to"
    # vertex such that
    #
    #    from_vertex + to_vertex == square
    #
    def random_vertex(self, from_vertex):
        E = self.edges[from_vertex]
        to_vertex = E[random.randrange(len(E))]
        return to_vertex

    #
    # return position of vertex in the current state
    #
    def vertex_index(self, vertex):
        #
        # if needed, build new index
        #
        if self.index is None:
            self.index = { self.state[i]: i for i in range(len(self.state)) }

        #
        # O(1) instead of O(n)
        #
        return self.index[vertex]

    def right_reverse(self, at):
        #
        # reverse of [at+1:] is possible because the caller has proven that:
        #
        #    state[at] + state[-1] == square
        #
        a = self.state[at+1:]
        a.reverse()
        self.state = self.state[0:at+1]
        self.state.extend(a)

        #
        # update index
        #
        for i in range(at+1, len(self.state)):
            self.index[self.state[i]] = i;

    def left_reverse(self, at):
        #
        # reverse of [0:at] is possible because the caller has proven that:
        #
        #    state[0] + state[at] == square
        #
        a = self.state[0:at]
        a.reverse()
        a.extend(self.state[at:])
        self.state = a

        #
        # update index
        #
        for i in range(at):
            self.index[self.state[i]] = i;

    #
    # self.state is always a solution;  this method randomly perturbs
    # it into another solution
    #
    def perturb(self):

        self.iterations += 1

        #
        # if we have this situation:
        #
        #    A ... B C ... D
        #
        # where A + C and B + D are square, we can then
        # reverse A ... B to get:
        #
        #    B ... A C ... D
        #
        # which is a hamiltonian cycle
        #
        for q in self.edges[self.state[0]]:
            k = self.vertex_index(q)
            if self.state[k - 1] + self.state[-1] in self.squares:
                self.left_reverse(k)
                return

        #
        # reverse either end at random
        #
        if random.random() < 0.5:
            #
            # when given
            #
            #    A ... B X ... D
            #
            # where B + D is square, then reverse X ... D
            # and we get
            #
            #    A ... B D ... X
            #
            # which is also a solution
            #
            to = self.random_vertex(self.state[-1])
            self.right_reverse(self.vertex_index(to))
        else:
            #
            # the left/right mirror image of the above
            #
            to = self.random_vertex(self.state[0])
            self.left_reverse(self.vertex_index(to))

    #
    # the canonical representation of cycle starts with "1"
    #
    def canonical(self):

        assert self.is_path

        assert self.is_cycle

        one = self.vertex_index(1)        # <- the "1"

        #
        # rotate the one to be first
        #
        return self.state[one:] + self.state[0:one]

    @property
    def is_path(self):

        #
        # verify each number appears exactly once
        #
        used = set()
        for i in self.state:
            if i < 1 or i > len(self.state):
                return False
            if i in used:
                return False
            used.add(i)

        #
        # verify each adjacency sums to a square
        #
        for i in range(1,len(self.state)):
            if self.state[i - 1] + self.state[i] not in self.squares:
                return False

        return True

    #
    # given it is a path, is the current state a hamiltonian cycle?
    #
    @property
    def is_cycle(self):
        return self.state[0] + self.state[-1] in self.squares


#
# the grind begins
#
def status_report(ss):
    solution = ss.canonical()
    print(datetime.datetime.now(), len(solution), ss.iterations, solution)

ss = square_sum()
while True:

    N = len(ss)

    if N >= 300000:
        status_report(ss)
        break

    if (N % 256) == 32:
        status_report(ss)

    ss = square_sum(ss)
    for i in range(10000):
        if ss.is_cycle:
            break
        ss.perturb()

    assert ss.is_cycle
