from enum import Enum
from functools import total_ordering

class ShapeType(Enum):
  Rod = 0,
  Stick = 1,
  RodShifted = 2

pineApplePileShapes = [
  # Rods of length 4
  [ShapeType.Rod, (0, 0), (1, 2), (0, 0), (0, 0)],
  [ShapeType.Rod, (0, 2), (0, 0), (0, 0), (0, 0)],

  # Rods of length 3
  [ShapeType.Rod, (2, 0), (0, 0), (0, 0)],
  [ShapeType.Rod, (0, 0), (1, 1), (0, 0)],
  [ShapeType.Rod, (0, 0), (0, 0), (3, 0)],
  [ShapeType.Rod, (0, 0), (0, 0), (0, 0)],

  # Stick
  [ShapeType.Stick, 3]
]

# The number of parts of each shape
pineApplePilePartNumbers = [2, 1, 2, 2, 1, 1, 1]

tooHardShapes = [
  # Rods of length 4
  [ShapeType.RodShifted, (0, 0), (2, 1), (0, 0), (0, 0)],
  [ShapeType.Rod, (0, 0), (0, 0), (0, 0), (0, 0)],

  # Rods of length 3
  [ShapeType.Rod, (0, 0), (0, 0), (0, 2)],
  [ShapeType.Rod, (0, 0), (1, 1), (0, 0)],
  [ShapeType.Rod, (0, 0), (0, 0), (0, 0)],

  # Sticks
  [ShapeType.Stick, 4],
  [ShapeType.Stick, 3]
]

tooHardPartNumbers = [2, 1, 2, 2, 2, 1, 2]

class Axis(Enum):
  X = 0
  Y = 1
  Z = 2

directionOfAxis = {
  Axis.X: (1, 0, 0),
  Axis.Y: (0, 1, 0),
  Axis.Z: (0, 0, 1)
}

class Orientation(Enum):
  PosX = 0
  NegX = 1
  PosY = 2
  NegY = 3
  PosZ = 4
  NegZ = 5

class UnitType(Enum):
  Rod = 0
  Stick = 1

@total_ordering
class Position:
  # Orientation can be of type Orientation (for rods and puzzle parts) or Axis (for sticks)
  def __init__(self, orientation, location):
    self.orientation = orientation
    self.location = location

  def __eq__(self, other):
    return ((self.orientation, self.location) == (other.orientation, other.location))

  def __ne__(self, other):
    return not (self == other)

  def __lt__(self, other):
    return ((self.orientation, self.location) < (other.orientation, other.location))

  def __str__(self):
    return "%s @ %s" % (self.location, self.orientation)

# Table that defines how the rod and its sticks extend for the various orientations
rodOrientations = {
  Orientation.PosX: {
    'rodDir': (1, 0, 0),
    'stickDirs': [(0, 1, 0), (0, 0, 1)]
  },
  Orientation.NegX: {
    'rodDir': (-1, 0, 0),
    'stickDirs': [(0, 0, 1), (0, 1, 0)]
  },
  Orientation.PosY: {
    'rodDir': (0, 1, 0),
    'stickDirs': [(0, 0, -1), (-1, 0, 0)]
  },
  Orientation.NegY: {
    'rodDir': (0, -1, 0),
    'stickDirs': [(-1, 0, 0), (0, 0, -1)]
  },
  Orientation.PosZ: {
    'rodDir': (0, 0, 1),
    'stickDirs': [(0, -1, 0), (1, 0, 0)]
  },
  Orientation.NegZ: {
    'rodDir': (0, 0, -1),
    'stickDirs': [(1, 0, 0), (0, -1, 0)]
  }
}

def generateLocations(vloc, vdir, vlen):
  return [(vloc[0] + vdir[0] * i, vloc[1] + vdir[1] * i, vloc[2] + vdir[2] * i) for i in range(vlen)]

def axisOfVector(v):
  return Axis.X if v[0] else Axis.Y if v[1] else Axis.Z

class Shape:
  def __init__(self, shapeDefinition):
    self.cellsByOrientation = {}

    shapeType = shapeDefinition[0]
    if shapeType == ShapeType.Rod:
      self._makeRodCells(shapeDefinition[1:])
    elif shapeType == ShapeType.RodShifted:
      self._makeRodCells(shapeDefinition[1:], 1)
    elif shapeType == ShapeType.Stick:
      self._makeStickCells(shapeDefinition[1])
    else:
      assert False

  def _makeRodCells(self, shapeDefinition, offset = 0):
    for rodOrientation in Orientation:
      cells = [[], []]
      self.cellsByOrientation[rodOrientation] = cells

      dirs = rodOrientations[rodOrientation]
      rodDir = dirs['rodDir']

      for i, loc in enumerate(generateLocations((0, 0, 0), rodDir, len(shapeDefinition))):
        stickDir = dirs['stickDirs'][(i + offset) % 2]
        stickOrientation = axisOfVector(stickDir)
        cells[UnitType.Rod.value].append(Position(stickOrientation, loc))

      for i, stickExtension in enumerate(shapeDefinition):
        pos, neg = stickExtension
        if pos + neg > 0:
          stickDir = dirs['stickDirs'][(i + offset) % 2]
          stickOrientation = axisOfVector(stickDir)
          refLoc = [rodDir[d] * i - stickDir[d] * neg for d in range(3)]
          cells[UnitType.Stick.value].extend(
            [Position(stickOrientation, loc) for loc in generateLocations(refLoc, stickDir, pos + neg + 1)]
          )

  def _makeStickCells(self, stickLen):
    for stickOrientation in Axis:
      cells = [[], []]
      self.cellsByOrientation[stickOrientation] = cells

      stickDir = directionOfAxis[stickOrientation]
      cells[UnitType.Stick.value].extend(
        [Position(stickOrientation, loc) for loc in generateLocations([0] * 3, stickDir, stickLen)]
      )

  def findPositionsFitting(self, otherUnitType, stickOrientation):
    myUnitType = UnitType.Rod if otherUnitType == UnitType.Stick else UnitType.Stick
    positions = []

    for orientation in self.cellsByOrientation:
      for pos in self.cellsByOrientation[orientation][myUnitType.value]:
        if pos.orientation == stickOrientation:
          # Found a match.
          relPos = Position(orientation, [-pos.location[i] for i in range(3)])
          positions.append(relPos)

    return positions

  def dump(self):
    for orientation in self.cellsByOrientation:
      print(orientation)
      cells = self.cellsByOrientation[orientation]
      for unitType in UnitType:
        print("%s: %s" % (unitType, [str(pos) for pos in cells[unitType.value]]))

class Part:
  def __init__(self, shape, index):
    self.shape = shape
    self.index = index
    self.pos = None

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
    self.cells = [[[GridCell() for i in range(size)] for i in range(size)] for i in range(size)]

    self.numCells = [0, 0]
    self.numFilledCells = 0

  def getCell(self, loc):
    if min(loc) < 0 or max(loc) >= self.size:
      return None
    else:
      return self.cells[loc[0]][loc[1]][loc[2]]

  # Visits all grid cells that the shape covers when located and oriented as specified by "pos".
  # For each cell (and unit type) the callback is invoked.
  #
  # The callback can abort the visit by returning True. If it does so, this method returns
  # the grid location where the visit was aborted. Otherwise it returns None.
  def _visitCells(self, shape, pos, callback):
    cells = shape.cellsByOrientation[pos.orientation]
    for unitType in UnitType:
      for cell in cells[unitType.value]:
        #print(pos.location, cell.location)
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
      part.shape, pos,
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
      part.shape, part.pos,
      lambda cell, unitType, stickOrientation: self._clearCell(cell, unitType, stickOrientation, part)
    )
    part.pos = None

  def _findPartialCell(self, cell, unitType):
    # Abort if the complimentary part is not yet set
    return not cell.parts[1 - unitType.value]

  def findPartialCell(self, part):
    return self._visitCells(
      part.shape, part.pos,
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
      part.shape, pos,
      self._checkCell
    )

  def __str__(self):
    return "<Grid #rodCells = %d, #stickCells = %d, #filledCells = %d>" % (
      self.numCells[UnitType.Rod.value],
      self.numCells[UnitType.Stick.value],
      self.numFilledCells
    )

  def dump(self):
    for y in range(self.size):
      for z in range(self.size):
        lines = ["", ""]
        for x in range(self.size):
          cell = self.getCell([x, self.size - y - 1, self.size - z - 1])
          for unitType in range(2):
            if x > 0:
              lines[unitType] += " "
            if cell.parts[unitType]:
              lines[unitType] += chr(65 + cell.parts[unitType].index + unitType * 32)
            else:
              lines[unitType] += "."
        print(lines[0], "   ", lines[1])
      print()

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
      for orientation in part.shape.cellsByOrientation:
        cells = part.shape.cellsByOrientation[orientation]
        numRodCells += len(cells[UnitType.Rod.value])
        numStickCells += len(cells[UnitType.Stick.value])
        break # Only need to count cells in one orientation

    assert numRodCells == numStickCells
    return numRodCells

  def _shouldBacktrack(self):
    if self.grid.numFilledCells == self.totalCells:
      print("Solved!")
      self.grid.dump()
      return True

    if sum(self.grid.numCells) - self.grid.numFilledCells > self.totalCells:
      # Too many partial cells remaining to fill them all
      #print("Stuck 1")
      return True

    if self.grid.numFilledCells == self.grid.numCells[0]:
      # The partial puzzle is fully connected so any final assembly will consist of multiple parts
      #print("Stuck 2")
      return True

    return False

  def _findCellToFill(self):
    for part in self.parts:
      if part.pos:
        partialCellLoc = self.grid.findPartialCell(part)
        if partialCellLoc:
          return partialCellLoc
    return None

  def _fillPartialCell(self, partialCellLoc, level):
    cell = self.grid.getCell(partialCellLoc)
    unitType = UnitType.Rod if cell.parts[UnitType.Rod.value] else UnitType.Stick
    #print("_fillPartialCell", partialCellLoc, unitType, str(cell))
    #if level > 7:
    #  print("%d. %s" % (level, self.grid))

    if self.grid.numFilledCells > self.bestNumFilled:
      self.bestNumFilled = self.grid.numFilledCells
      print("Best sofar =", self.bestNumFilled)
      self.grid.dump()

    lastShape = None
    for i, part in enumerate(self.parts):
      if (
        # Part is still available
        not part.pos and
        # It's a different shape
        not part.shape is lastShape
      ):
        lastShape = part.shape

        # Find all (relative) positions of the puzzle part that fit the given unit
        relPositions = part.shape.findPositionsFitting(unitType, cell.orientation)
        for relPos in relPositions:
          pos = Position(relPos.orientation, [partialCellLoc[i] + relPos.location[i] for i in range(3)])
          if self.grid.doesPartFit(part, pos):
            #print("%sPart %d @ %s" % ("  " * level, i, relPos))
            self.grid.addPart(part, pos)
            self._solve(level + 1)
            self.grid.removePart(part)

  def _solve(self, level = 1):
    if self._shouldBacktrack():
      return

    partialCellLoc = self._findCellToFill()
    assert partialCellLoc
    #print(partialCellLoc)

    self._fillPartialCell(partialCellLoc, level)

  def solve(self, firstPartPos = None):
    if not firstPartPos:
      firstPartPos = Position(Orientation.PosX, [self.grid.size // 2] * 3)
    self.grid.addPart(self.parts[0], firstPartPos)

    self.bestNumFilled = 0
    self._solve()

def makeParts(shapeDefinitions, shapeCounts):
  parts = []
  for i, shapeDefinition in enumerate(shapeDefinitions):
    shape = Shape(shapeDefinition)
    for _ in range(shapeCounts[i]):
      parts.append(Part(shape, len(parts)))

  return parts

pineApplePileParts = makeParts(pineApplePileShapes, pineApplePilePartNumbers)
tooHardParts = makeParts(tooHardShapes, tooHardPartNumbers)

if False:
  grid = Grid(4)
  parts = pineApplePileParts
  parts[7].shape.dump()

  grid.addPart(parts[9], Position(Axis.Z, [1, 0, 1]))
  grid.addPart(parts[3], Position(Orientation.PosX, [0, 0, 2]))
  grid.addPart(parts[4], Position(Orientation.NegZ, [0, 1, 3]))
  grid.addPart(parts[7], Position(Orientation.PosY, [1, 0, 3]))
  grid.dump()

#solver = Solver(4, pineApplePileParts)
#solver.solve(Position(Orientation.PosX, [0, 2, 2]))

for z in [1, 2]:
  solver = Solver(4, tooHardParts)
  solver.solve(Position(Orientation.PosX, [0, 1, z]))
