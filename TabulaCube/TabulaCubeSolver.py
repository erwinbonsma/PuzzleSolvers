# (C) 2021, Erwin Bonsma
#
# This is a simple solver for Yavuz Demirhan's Tabula Cube

from collections import namedtuple
import itertools

PieceDef = namedtuple('PieceDef', ['blocks', 'strips'])

# Piece definitions. Should be defined such that a shift_x is possible
piece_defs = [
	PieceDef([0, 3, 6, 15], [0, 16]),
	PieceDef([0, 6, 15, 25], [0, 16]),
	PieceDef([6, 15, 18, 25], [0, 17]),
	PieceDef([15, 18, 24], [0, 17]),
	PieceDef([0, 6, 25], [0, 16]),
	PieceDef([7, 15, 18], [0, 17]),
	PieceDef([0, 15], [0, 16]),
	PieceDef([0, 15], [0, 16]),
	PieceDef([15], [0, 16])
]

class Block:
	def __init__(self, id):
		assert(id >= 0 and id < 27)
		self.x = id % 3
		self.y = (id // 3) % 3
		self.z = (id // 9) % 3

	def shift_x(self):
		self.x += 1
		assert(self.x < 3)

	def rotate_y(self):
		self.x = 2 - self.x
		self.z = 2 - self.z

	def rotate_x(self):
		self.y = 2 - self.y
		self.z = 2 - self.z

	def reorient(self):
		self.x, self.y, self.z = self.z, self.x, self.y

	def id(self):
		return self.x + 3 * self.y + 9 * self.z

class Strip:
	def __init__(self, id):
		assert(id >= 0 and id < 18)
		self.col = id % 2
		self.row = (id % 6) // 2
		self.orientation = id // 6

	def shift_x(self):
		if self.orientation == 0:
			self.col += 1
			assert(self.col < 2)
		elif self.orientation == 1:
			assert(False)
		elif self.orientation == 2:
			self.row -= 1
			assert(self.row >= 0)

	def rotate_y(self):
		if self.orientation == 0:
			self.col = 1 - self.col
		elif self.orientation == 1:
			self.row = 2 - self.row
		elif self.orientation == 2:
			self.col = 1 - self.col
			self.row = 2 - self.row

	def rotate_x(self):
		if self.orientation == 0:
			self.row = 2 - self.row
		elif self.orientation == 1:
			self.col = 1 - self.col
			self.row = 2 - self.row
		elif self.orientation == 2:
			self.col = 1 - self.col

	def reorient(self):
		self.orientation = (self.orientation + 1) % 3

	def id(self):
		return 6 * self.orientation + self.col + 2 * self.row

def generate_orientations(piece_def):
	orientations = []
	for i in range(24):
		blocks = [Block(id) for id in piece_def.blocks]
		strips = [Strip(id) for id in piece_def.strips]

		for part in itertools.chain(blocks, strips):
			if i % 2 == 1:
				part.shift_x()
			if (i // 2) % 2 == 1:
				part.rotate_y()
			if (i // 4) % 2 == 1:
				part.rotate_x()

			for j in range(i // 8):
				part.reorient()

		orientations.append(PieceDef(
			[block.id() for block in blocks],
			[strip.id() for strip in strips]
		))
	return orientations

def to_bits(piece_def):
	bits = 0
	for part in piece_def.blocks:
		bits |= 1 << part
	for part in piece_def.strips:
		bits |= 1 << (part + 27)
	return bits

class Solver:
	def __init__(self, piece_defs):
		self.orientations = [
			[to_bits(pd2) for pd2 in generate_orientations(pd)] for pd in piece_defs
		]

	def solve(self):
		# Only consider two orientations for the first piece
		for first_piece in self.orientations[0][0:2]:
			self._solve(first_piece, [first_piece])

	def _solve(self, combined, pieces):
		if len(pieces) == len(self.orientations):
			self._dump(combined, pieces)
			return

		for piece in self.orientations[len(pieces)]:
			if combined & piece == 0:
				self._solve(combined | piece, pieces + [piece])

	def _dump(self, combined, pieces):
		for z in range(3):
			line = ""
			for y in range(3):
				if len(line) > 0:
					line += "  "
				for x in range(3):
					if len(line) > 0:
						line += " "
					id = x + 3 * (2 - y) + 9 * z
					bit = (1 << id)
					char = None
					if combined & bit:
						for i, piece in enumerate(pieces):
							if piece & bit:
								assert(char is None)
								char = chr(ord('A') + i)
					else:
						char = '_'
					line += char
			print(line)
		print()

solver = Solver(piece_defs)
solver.solve()
