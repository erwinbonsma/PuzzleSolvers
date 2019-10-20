from enum import Enum
from functools import total_ordering

pineApplePileShapes = [
  # Rods of length 4
  [(0, 0), (1, 2), (0, 0), (0, 0)],
  [(0, 2), (0, 0), (0, 0), (0, 0)],

  # Rods of length 3
  [(2, 0), (0, 0), (0, 0)],
  [(0, 0), (1, 1), (0, 0)],
  [(0, 0), (0, 0), (3, 0)],
  [(0, 0), (0, 0), (0, 0)],

  # Stick
  [(2, 0)]
]

# The number of parts of each shape
pineApplePilePartNumbers = [2, 1, 2, 2, 1, 1, 1]

class Orientation(Enum):
  X = 0
  Y = 1
  Z = 2

class PartType(Enum):
  Rod = 0
  Stick = 1

@total_ordering
class Position:
  def __init__(self, orientation, location):
    self.orientation = orientation
    self.location = location

  def __eq__(self, other):
    return ((self.orientation, self.location) == (other.orientation, other.location))

  def __ne__(self, other):
    return not (self == other)

  def __lt__(self, other):
    return ((self.orientation, self.location) < (other.orientation, other.location))

# Table that defines how the rod and its sticks extend for the various orientations
partRotations = {
  Orientation.X: {
    'rodDir': (1, 0, 0),
    'stickDirs': [(0, 1, 0), (0, 0, 1)]
  },
  Orientation.Y: {
    'rodDir': (0, 1, 0),
    'stickDirs': [(0, 0, -1), (-1, 0, 0)]
  },
  Orientation.Z: {
    'rodDir': (0, 0, -1),
    'stickDirs': [(1, 0, 0), (0, -1, 0)]
  }
}

def generateLocations(loc, dir, length):
  return [(loc[0] + dir[0] * i, loc[1] + dir[1] * i, loc[2] + dir[2] * i) for i in range(length)]

class Part:
  def __init__(self, shape):
    self.shape = shape

    self.rodCells = {}
    self.stickCells = {}

    self.pos = None

    for rodOrientation in Orientation:
      self.rodCells[rodOrientation] = []
      self.stickCells[rodOrientation] = []

      pr = partRotations[rodOrientation]
      rodDir = pr['rodDir']

      if len(shape) > 1:
        i = 0
        for loc in generateLocations((0, 0, 0), rodDir, len(shape)):
          stickDir = pr['stickDirs'][i % 2]
          self.rodCells[rodOrientation].append(Position(stickDir, loc))
          i += 1

      for i in range(len(shape)):
        pos, neg = shape[i]

        if pos + neg > 0:
          stickDir = pr['stickDirs'][i % 2]
          refLoc = [rodDir[d] * i - stickDir[d] * neg for d in range(3)]
          self.stickCells[rodOrientation].extend(
            [Position(stickDir, loc) for loc in generateLocations(refLoc, stickDir, pos + neg + 1)]
          )

class GridCell:
  def __init__(self):
    self.orientation = None
    self.parts = [None, None]

class Grid:
  def __init__(self, size):
    self.size = size
    self.centerLoc = [size // 2] * 3
    self.cells = [[[GridCell() for i in range(size)] for i in range(size)] for i in range(size)]

    self.numCells = [0, 0]
    self.numFilledCells = 0

  def _getCell(self, loc):
    return self.cells[loc[0]][loc[1]][loc[2]]

  # Visits all cells that the part covers. For each cell, it invokes the callback.
  #
  # The callback can abort the visit by returning True. If it does so, this method returns
  # the grid position where the visit was aborted. Otherwise it returns None.
  def _visitCells(self, part, pos, callback):
    for rodCell in part.rodCells[pos.orientation]:
      print(self.centerLoc, pos.location, rodCell.location)
      p = [self.centerLoc[i] + pos.location[i] + rodCell.location[i] for i in range(3)]
      cell = self._getCell(p)
      if callback(cell, PartType.Rod, rodCell.orientation):
        return p

    for stickCell in part.stickCells[pos.orientation]:
      print(self.centerLoc, pos.location, stickCell.location)
      p = [self.centerLoc[i] + pos.location[i] + stickCell.location[i] for i in range(3)]
      cell = self._getCell(p)
      if callback(cell, PartType.Stick, stickCell.orientation):
        return p

    return None

  def _setCell(self, cell, partType, stickOrientation, part):
    assert not cell.parts[partType.value]

    cell.parts[partType.value] = part
    self.numCells[partType.value] += 1

    if cell.orientation:
      assert cell.orientation == stickOrientation
      self.numFilledCells += 1
    else:
      cell.orientation = stickOrientation

  def addPart(self, part, pos):
    self._visitCells(
      part, pos,
      lambda cell, partType, stickOrientation: self._setCell(cell, partType, stickOrientation, part)
    )
    part.pos = pos

  def _clearCell(self, cell, partType, stickOrientation, part):
    assert cell.parts[partType.value] == part
    assert cell.orientation == stickOrientation

    cell.parts[partType.value] = None
    self.numCells[partType.value] -= 1

    if cell.parts[1 - partType.value]:
      self.numFilledCells -= 1
    else:
      cell.orientation = None

  def removePart(self, part):
    self._visitCells(
      part, part.pos,
      lambda cell, partType, stickOrientation: self._clearCell(cell, partType, stickOrientation, part)
    )
    part.pos = None

  def _findPartialCell(self, cell, partType):
    # Abort if the complimentary part is not yet set
    return not cell.parts[1 - partType.value]

  def findPartialCell(self, part):
    return self._visitCells(
      part, part.pos,
      lambda cell, partType, stickOrientation: self._findPartialCell(cell, partType)
    )

  def _checkCell(self, cell, partType, stickOrientation):
    if cell.parts[partType.value]:
      return True # Already filled, abort
    if cell.orientation and cell.orientation != stickOrientation:
      return True # Orientation mismatch, abort
    return False # Do not abort

  def doesPartFit(self, part, pos):
    return not self._visitCells(
      part, pos,
      self._checkCell
    )

  def __str__(self):
    return "#rodCells = %d, #stickCells = %d, #filledCells = %d" % (
      self.numCells[PartType.Rod.value],
      self.numCells[PartType.Stick.value],
      self.numFilledCells
    )

class Solver:
  def __init__(self, gridSize, parts):
    self.grid = Grid(gridSize)
    self.parts = parts
    self.totalCells = self._countPartCells()
    print("totalCells =", self.totalCells)

  def _countPartCells(self):
    numRodCells = 0
    numStickCells = 0

    for part in self.parts:
      numRodCells += len(part.rodCells[Orientation.X])
      numStickCells += len(part.stickCells[Orientation.X])
      print(numRodCells, numStickCells)

    assert numRodCells == numStickCells
    return numRodCells

  def _shouldBacktrack(self):
    if self.grid.numFilledCells == self.totalCells:
      print("Solved!")
      return True

    if self.grid.numFilledCells + sum(self.grid.numCells) > self.totalCells:
      # Too many partial cells remaining to fill them all
      print("Stuck 1")
      return True

    if self.grid.numFilledCells == self.grid.numCells[0]:
      # The partial puzzle is fully connected so any final assembly will consist of multiple parts
      print("Stuck 2")
      return True

    return False

  def _findCellToFill(self):
    partialCell = None
    for part in self.parts:
      if part.pos:
        partialCell = self.grid.findPartialCell(part)
        if partialCell:
          break
    return partialCell

  def _fillPartialCell(self, partialCell):
    for part in self.parts:
      if not part.pos:
        # Find all positions of part that fill the partially filled cell
        positions = []
        for pos in positions:
          if self.grid.doesPartFit(part, pos):
            self.grid.addPart(part, pos)
            self.solve()
            self.grid.removePart(part)

  def _solve(self):
    if self._shouldBacktrack():
      return

    partialCell = self._findCellToFill()
    assert partialCell
    print(partialCell)

    self._fillPartialCell(partialCell)

  def solve(self):
    self.grid.addPart(self.parts[0], Position(Orientation.X, (0, 0, 0)))
    print(self.grid)

    self._solve()

def makeParts(numbers, shapes):
  parts = []
  for shapeNum in range(len(numbers)):
    for p in range(numbers[shapeNum]):
      part = Part(shapes[shapeNum])
      part.index = len(parts)
      part.shapeNum = shapeNum
      parts.append(part)

  return parts

parts = makeParts(pineApplePilePartNumbers, pineApplePileShapes)

solver = Solver(8, parts)
solver.solve()
