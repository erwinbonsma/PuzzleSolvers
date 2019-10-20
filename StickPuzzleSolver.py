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

class UnitType(Enum):
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

def generateLocations(vloc, vdir, vlen):
  return [(vloc[0] + vdir[0] * i, vloc[1] + vdir[1] * i, vloc[2] + vdir[2] * i) for i in range(vlen)]

def orientationOfVector(v):
  return Orientation.X if v[0] else Orientation.Y if v[1] else Orientation.Z

class Part:
  def __init__(self, shape):
    self.shape = shape

    self.cells = {}

    self.pos = None

    for rodOrientation in Orientation:
      self.cells[rodOrientation] = [[], []]
      cells = self.cells[rodOrientation]

      pr = partRotations[rodOrientation]
      rodDir = pr['rodDir']

      if len(shape) > 1:
        for i, loc in enumerate(generateLocations((0, 0, 0), rodDir, len(shape))):
          stickDir = pr['stickDirs'][i % 2]
          stickOrientation = orientationOfVector(stickDir)
          cells[UnitType.Rod.value].append(Position(stickOrientation, loc))

      for i in range(len(shape)):
        pos, neg = shape[i]

        if pos + neg > 0:
          stickDir = pr['stickDirs'][i % 2]
          stickOrientation = orientationOfVector(stickDir)
          refLoc = [rodDir[d] * i - stickDir[d] * neg for d in range(3)]
          cells[UnitType.Stick.value].extend(
            [Position(stickOrientation, loc) for loc in generateLocations(refLoc, stickDir, pos + neg + 1)]
          )

  def findPositionsFitting(self, otherUnitType, stickOrientation):
    myUnitType = UnitType.Rod if otherUnitType == UnitType.Stick else UnitType.Stick
    positions = []

    for rodOrientation in Orientation:
      for pos in self.cells[rodOrientation][myUnitType.value]:
        if pos.orientation == stickOrientation:
          # Found a match.
          relPos = Position(rodOrientation, [-pos.location[i] for i in range(3)])
          positions.append(relPos)

    return positions

class GridCell:
  def __init__(self):
    self.orientation = None
    self.parts = [None, None]

  def __str__(self):
    if self.parts[UnitType.Rod.value]:
      if self.parts[UnitType.Stick.value]:
        return "<GridCell: Filled (%s)>" % (str(self.orientation))
      else:
        return "<GridCell: Rod (%s)>" % (str(self.orientation))
    else:
      if self.parts[UnitType.Stick.value]:
        return "<GridCell: Stick (%s)>" % (str(self.orientation))
      else:
        return "<GridCell: Empty>"

class Grid:
  def __init__(self, size):
    self.size = size
    #self.centerLoc = [size // 2] * 3
    self.cells = [[[GridCell() for i in range(size)] for i in range(size)] for i in range(size)]

    self.numCells = [0, 0]
    self.numFilledCells = 0

  def getCell(self, loc):
    if min(loc) < 0 or max(loc) >= self.size:
      return None
    else:
      return self.cells[loc[0]][loc[1]][loc[2]]

  # Visits all cells that the part covers. For each cell, it invokes the callback.
  #
  # The callback can abort the visit by returning True. If it does so, this method returns
  # the grid location where the visit was aborted. Otherwise it returns None.
  def _visitCells(self, part, pos, callback):
    for unitType in UnitType:
      for cell in part.cells[pos.orientation][unitType.value]:
        print(pos.location, cell.location)
        loc = [pos.location[i] + cell.location[i] for i in range(3)]
        gridCell = self.getCell(loc)
        if (not gridCell) or callback(gridCell, unitType, cell.orientation):
          return loc

    return None

  def _setCell(self, cell, unitType, stickOrientation, part):
    assert not cell.parts[unitType.value]

    cell.parts[unitType.value] = part
    self.numCells[unitType.value] += 1

    if cell.orientation:
      assert cell.orientation == stickOrientation
      self.numFilledCells += 1
    else:
      assert stickOrientation
      cell.orientation = stickOrientation

  def addPart(self, part, pos):
    self._visitCells(
      part, pos,
      lambda cell, unitType, stickOrientation: self._setCell(cell, unitType, stickOrientation, part)
    )
    part.pos = pos

  def _clearCell(self, cell, unitType, stickOrientation, part):
    assert cell.parts[unitType.value] == part
    assert cell.orientation == stickOrientation

    cell.parts[unitType.value] = None
    self.numCells[unitType.value] -= 1

    if cell.parts[1 - unitType.value]:
      self.numFilledCells -= 1
    else:
      cell.orientation = None

  def removePart(self, part):
    self._visitCells(
      part, part.pos,
      lambda cell, unitType, stickOrientation: self._clearCell(cell, unitType, stickOrientation, part)
    )
    part.pos = None

  def _findPartialCell(self, cell, unitType):
    # Abort if the complimentary part is not yet set
    return not cell.parts[1 - unitType.value]

  def findPartialCell(self, part):
    return self._visitCells(
      part, part.pos,
      lambda cell, unitType, stickOrientation: self._findPartialCell(cell, unitType)
    )

  def _checkCell(self, cell, unitType, stickOrientation):
    if cell.parts[unitType.value]:
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
      self.numCells[UnitType.Rod.value],
      self.numCells[UnitType.Stick.value],
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
      numRodCells += len(part.cells[Orientation.X][UnitType.Rod.value])
      numStickCells += len(part.cells[Orientation.X][UnitType.Stick.value])
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
    partialCellLoc = None
    for part in self.parts:
      if part.pos:
        partialCellLoc = self.grid.findPartialCell(part)
        if partialCellLoc:
          break
    return partialCellLoc

  def _fillPartialCell(self, partialCellLoc):
    cell = self.grid.getCell(partialCellLoc)
    unitType = UnitType.Rod if cell.parts[UnitType.Rod.value] else UnitType.Stick
    print("_fillPartialCell", partialCellLoc, unitType, str(cell))

    for part in self.parts:
      if not part.pos:
        # Find all (relative) positions of the puzzle part that fit the given unit
        relPositions = part.findPositionsFitting(unitType, cell.orientation)
        print(relPositions)
        for relPos in relPositions:
          pos = Position(relPos.orientation, [partialCellLoc[i] + relPos.location[i] for i in range(3)])
          if False and self.grid.doesPartFit(part, pos):
            self.grid.addPart(part, pos)
            self.solve()
            self.grid.removePart(part)

  def _solve(self):
    if self._shouldBacktrack():
      return

    partialCellLoc = self._findCellToFill()
    assert partialCellLoc
    print(partialCellLoc)

    self._fillPartialCell(partialCellLoc)

  def solve(self):
    self.grid.addPart(self.parts[0], Position(Orientation.X, [self.grid.size // 2] * 3))
    print(self.grid)

    self._solve()

def makeParts(numbers, shapes):
  parts = []
  for shapeNum in range(len(numbers)):
    for _ in range(numbers[shapeNum]):
      parts.append(Part(shapes[shapeNum]))

  return parts

pineApplePileParts = makeParts(pineApplePilePartNumbers, pineApplePileShapes)

solver = Solver(8, pineApplePileParts)
solver.solve()
