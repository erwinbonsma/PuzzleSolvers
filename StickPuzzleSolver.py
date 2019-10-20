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
  # the cell where the visit was aborted. Otherwise it returns None.
  def _visitCells(self, part, pos, callback):
    for rodCell in part.rodCells[pos.orientation]:
      print(self.centerLoc, pos.location, rodCell.location)
      p = [self.centerLoc[i] + pos.location[i] + rodCell.location[i] for i in range(3)]
      cell = self._getCell(p)
      if callback(cell, PartType.Rod, rodCell.orientation):
        return cell

    for stickCell in part.stickCells[pos.orientation]:
      print(self.centerLoc, pos.location, stickCell.location)
      p = [self.centerLoc[i] + pos.location[i] + stickCell.location[i] for i in range(3)]
      cell = self._getCell(p)
      if callback(cell, PartType.Stick, stickCell.orientation):
        return cell

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
    del part.pos

  def doesPartFit(self, part, pos, lowestConnectedPart):
    return self._visitCells(
      part, pos,
      lambda cell, contentsIndex: self._checkCell(cell, contentsIndex, lowestConnectedPart)
    )

  def __str__(self):
    return "#rodCells = %d, #stickCells = %d, #filledCells = %d" % (
      self.numCells[PartType.Rod.value],
      self.numCells[PartType.Stick.value],
      self.numFilledCells
    )

def makeParts(numbers, shapes):
  parts = []
  numRodCells = 0
  numStickCells = 0
  for shapeNum in range(len(numbers)):
    for p in range(numbers[shapeNum]):
      part = Part(shapes[shapeNum])
      part.index = len(parts)
      part.shapeNum = shapeNum
      parts.append(part)
      numRodCells += len(part.rodCells[Orientation.X])
      numStickCells += len(part.stickCells[Orientation.X])
      print(numRodCells, numStickCells)

  assert numRodCells == numStickCells

  return parts, numRodCells

def solve():
  if grid.numFilledCells == totalCells:
    print("Solved!")
    return

  # TODO

parts, totalCells = makeParts(pineApplePilePartNumbers, pineApplePileShapes)
print("totalCells =", totalCells)

grid = Grid(8)

grid.addPart(parts[0], Position(Orientation.X, (0, 0, 0)))
print(grid)
grid.removePart(parts[0])
print(grid)

#solve(1)


