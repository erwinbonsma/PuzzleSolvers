from collections import namedtuple
import itertools

PieceDef = namedtuple('PieceDef', ['blocks', 'strips'])

# Piece definitions. Should be defined such that a shift_x is possible
piece_defs = [
	PieceDef([0, 1, 9, 18], [0, 16]),
	PieceDef([0, 1, 5, 18], [0, 16]),
	PieceDef([0, 1, 5, 20], [0, 17]),
	PieceDef([1, 2, 20], [0, 17]),
	PieceDef([0, 5, 23], [0, 15]),
	PieceDef([1, 3, 20], [0, 17]),
	PieceDef([1, 18], [0, 16]),
	PieceDef([1, 18], [0, 16]),
	PieceDef([1], [0, 16])
]

class Block:
	def __init__(self, id):
		assert(id >= 0 and id < 27)
		self.z = id % 3
		self.x = (id // 3) % 3
		self.y = (id // 9) % 3

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
		self.x, self.y, self.z = self.z, 2 - self.x, 2 - self.y

	def id(self):
		return 9 * self.y + 3 * self.x + self.z

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
		else:
			assert(False)

	def rotate_y(self):
		if self.orientation == 0:
			self.col = 1 - self.col
		elif self.orientation == 1:
			self.row = 2 - self.row
		elif self.orientation == 2:
			self.col = 1 - self.col
			self.row = 2 - self.row
		else:
			assert(False)

	def rotate_x(self):
		if self.orientation == 0:
			self.row = 2 - self.row
		elif self.orientation == 1:
			self.col = 1 - self.col
			self.row = 2 - self.row
		elif self.orientation == 2:
			self.col = 1 - self.col
		else:
			assert(False)

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

def as_bitstring(piece_def):
	bitstring = 0
	for part in piece_def.blocks:
		bitstring |= 1 << part
	for part in piece_def.strips:
		bitstring |= 1 << (part + 27)
	return bitstring

class Solver:

	def __init__(self, piece_defs):
		self.orientations = []
		for piece_def in piece_defs:
			piece_orientations = [piece_def] if len(self.orientations) == 0 \
				else generate_orientations(piece_def)
			print(piece_orientations)
			self.orientations.append([as_bitstring(pd) for pd in piece_orientations])
		print([[hex(pd) for pd in pds] for pds in self.orientations])
		
	def solve(self, combined = 0, pieces = []):
		if len(pieces) == len(self.orientations):
			print("Solved", combined, pieces)
			self.dump(combined, pieces)
			return
		
		#print(hex(combined), [hex(p) for p in pieces])
		#self.dump(combined, pieces)
		for piece in self.orientations[len(pieces)]:
			if combined & piece == 0:
				self.solve(combined | piece, pieces + [piece])

	def dump(self, combined, pieces):
		for z in range(3):
			line = ""
			for y in range(3):
				if len(line) > 0:
					line += "  "
				for x in range(3):
					if len(line) > 0:
						line += " "
					id = 9 * y + 3 * x + z
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

solver = Solver(piece_defs)
solver.solve()
