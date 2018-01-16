import random

#
# this class takes a previous hamiltonian cycle (length N) for
# the square_sum problem and helps make a new cycle of length N + 1
#
# it is utterly bereft of any theoretical support; the author of
# this code has no idea why it works.  though there is likely
# some connection to random graph theory in here somewhere.
#
# this code is in the public domain.
#
# the core idea is that given a hamiltonian cycle that solves the
# problem for N, you can trivially convert this into a
# (non-cycle) solution for N+1.  at that point, just
# randomly perturb the solution until a hamiltonian cycle
# for N+1 is found.  then repeat.
#
# this code has been run to N=25,000 in 20 minutes on a modern
# desktop CPU.
#
# further work:
#
# the number of perturbations done to find a new hamiltonian cycle
# appears to be fairly constant -- perhaps O(1)?
#
# are there perturbations that would do a more efficient job?
#
# is there a more clever way of choosing the cut-points
# for the reversals?
#
class square_sum:

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
        # initial edges
        #
        def mk_initial_edges(S, N):
            return { vertex: [ o for o in range(1, N + 1)
                    if o != vertex and vertex + o in self.squares ]
                        for vertex in range(1, N + 1) }

        #
        # update edges from previous step
        #
        def mk_update_edges(squares, previous_edges, N):
            new_edges = {}
            new_vertices = []
            for v, e in iter(previous_edges.items()):
                if v + N in squares:
                    new_edges[v] = e + [ N ]
                    new_vertices += [ v ]
                else:
                    new_edges[v] = e
            new_edges[N] = new_vertices
            return new_edges

        #
        # if no previous state, start with the first known cycle
        #
        if previous is None:
            #
            # the first hamiltonian cycle is length 32;  this result is due to Landon Kryger, which
            # he published in a comment to https://www.youtube.com/watch?v=7_ph5djCCnM
            #
            self.state = [1, 8, 28, 21, 4, 32, 17, 19, 30, 6, 3, 13, 12, 24,
                    25, 11, 5, 31, 18, 7, 29, 20, 16, 9, 27, 22, 14, 2, 23, 26, 10, 15]
            N = len(self.state)
            self.squares = mk_squares(N)
            self.edges = mk_initial_edges(self.squares, N)
            return

        #
        # next state is +1 from previous
        #
        N = len(previous.state) + 1
        self.squares = mk_squares(N)
        self.edges = mk_update_edges(self.squares, previous.edges, N)

        #
        # now rotate and augment previous hamiltonian cycle to
        # a hamiltonian path (now no longer a cycle!) one size larger
        #
        k = previous.state.index(self.random_vertex(N))

        self.state = [ N ]
        self.state += previous.state[k:]
        self.state += previous.state[0:k]

    #
    # given a "from" vertex, return a random "to"
    # vertex such that from + to is a square
    #
    def random_vertex(self, from_vertex):
        e = self.edges[from_vertex]
        return e[random.randrange(len(e))]

    #
    # return position of vertex in the current state
    #
    def vertex_index(self, vertex):
        return self.state.index(vertex)

    #
    # self.state is always a solution;  this method randomly perturbs
    # it into another solution
    #
    def step(self):

        def reverse(self):
            #
            # end-to-end reversal of the path
            #
            self.state = [ x for x in reversed(self.state) ]

        def swap(self, index):
            #
            # swap the first vertex with a random vertex
            #
            a = self.state[0:index]
            b = self.state[index:]
            self.state = [ x for x in reversed(a) ] + b

        #
        # be a bit clever about where to swap:  if one exists that
        # can create a cycle, actually do it now
        #
        for q in self.edges[self.state[0]]:
            k = self.vertex_index(q)
            if self.state[k - 1] + self.state[-1] in self.squares:
                swap(self, k)
                return

        #
        # choose either reversal or front-swap
        #
        # this could probably be generalized to any interior
        # sequence, but these two seem to work well enough.
        #
        if random.random() < 0.5:
            #
            # end-to-end flip is still a path
            #
            reverse(self)
        else:
            #
            # randomly swap a front-section
	    #
            to = self.random_vertex(self.state[0])
            to_index = self.vertex_index(to)
            swap(self, to_index)

    #
    # the canonical representation of cycle starts with "1"
    #
    def canonical(self):

        assert self.is_path

        assert self.is_cycle

        k = self.state.index(1)        # <- the "1"

        return self.state[k:] + self.state[0:k]

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
# and now, to 3,000 with it:
#
ss = square_sum()
iterations = 0
while True:

    solution = ss.canonical()

    if len(solution) >= 300000:
        print(len(solution), iterations, solution)
        print("Well, I'm quite bored.")
        break

    if (len(solution) % 256) == 32:
        print(len(solution), iterations, solution)

    ss = square_sum(ss)
    iterations = 0
    for i in range(10000):
        if ss.is_cycle:
            break
        ss.step()
        iterations += 1

    if not ss.is_cycle:
        print('Oops.')
        break

	
