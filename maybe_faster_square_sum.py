import random

#
# warning: this file uses tabs for indentation, not spaces.
#
# this class takes a previous hamiltonian cycle (length N) for
# the square_sum problem and helps make a new cycle of length N + 1
#
# it is awfully inefficient and is utterly bereft of any
# theoretical support; the author of this code has no idea
# why it works.  though there is likely some connection to
# random graph theory in here somewhere.
#
# this code is in the public domain.
#
# the core idea is that given a hamiltonian cycle that solves the
# problem for N, you can trivially convert this into a
# (non-cycle) solution for N+1.  at that point, just
# randomly perturb the solution until a hamiltonian cycle
# for N+1 is found.  then repeat.
#
# this code has been run on Python 3.6.3 to N=3000 in under 15 minutes
# on a modern desktop CPU. at that point, successive values of N are found
# every second or so.
#
# further work:
#
# the number of perturbations done to find a new hamiltonian cycle
# appears to be fairly constant -- suggesting that indexing of
# the solution ("self.state") will probably make this code run
# significantly faster, as would a C/C++ implementation.
#
# the perturbations here were chosen to always change either end of the
# solution -- so this code is somewhat greedy.  are there perturbations
# that are not as locally greedy, but do a faster job in the end?
#
# is there a more clever way of choosing the cut-points
# for the reversals?  the choice of the cuts and a proof they
# always convert a hamiltonian_cycle(N) into hamiltonian_cycle(N+1)
# would prove the conjecture.
#
class square_sum:

	#
	# the argument must be a hamiltonian path
	#
	def __init__(self, previous_hamiltonian_cycle):

		#
		# new state will be one larger than the old, so:
		#
		N = len(previous_hamiltonian_cycle) + 1

		#
		# set of applicable squares
		#
		# ,,, it may be faster to do integer square-roots
		#
		self.squares = set()
		k = 1
		while True:
			s = k*k
			if s > 2*N - 1:
				break
			self.squares.add(s)
			k += 1

		#
		# the list of edges, indexed by vertex
		#
		self.edges = { vertex: [ o for o in range(1, N + 1)
						if vertex + o in self.squares ]
							for vertex in range(1, N + 1) }

		#
		# now rotate and augment previous hamiltonian cycle to
		# a hamiltonian path (now no longer a cycle!) one size larger
		#
		k = previous_hamiltonian_cycle.index(self.edges[N][0])

		self.state = [ N ]
		self.state += previous_hamiltonian_cycle[k:]
		self.state += previous_hamiltonian_cycle[0:k]

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

		def swap(self, k):
			#
			# swap the first vertex with a random vertex
			#
			a = self.state[0:k]
			b = self.state[k:]
			self.state = [ x for x in reversed(a) ] + b

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
			e = self.edges[ self.state[0] ]
			o = e[random.randrange(len(e))]
			k = self.state.index(o)
			swap(self, k)

	#
	# the canonical representation of cycle starts with "1"
	#
	def canonical(self):

		assert self.is_path

		assert self.is_cycle

		k = self.state.index(1)         # <- the "1"

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
# the first hamiltonian cycle is length 32;  this result is due to Landon Kryger, which
# he published in a comment to https://www.youtube.com/watch?v=7_ph5djCCnM
#
state = [1, 8, 28, 21, 4, 32, 17, 19, 30, 6, 3, 13, 12, 24, 25, 11, 5, 31, 18, 7, 29, 20, 16, 9, 27, 22, 14, 2, 23, 26, 10, 15]
iterations = 0

#
# and now, to 3,000 with it:
#
while True:

	print(len(state), iterations, state)

	if len(state) >= 3000:
		print("Well, I'm bored.")
		break

	ss = square_sum(state)
	iterations = 0
	for i in range(10000):
		ss.step()
		iterations += 1
		if ss.is_cycle:
			break

	if not ss.is_cycle:
		print('Oops.')
		break

	state = ss.canonical()
