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
pineApplePilePartNumbers = [2, 1, 2, 2, 1, 1]

class Orientation(Enum):
  X = 0
  Y = 1
  Z = 2

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

    self.rodLoc = {}
    self.stickLoc = {}

    for rodOrientation in Orientation:
      self.rodLoc[rodOrientation] = []
      self.stickLoc[rodOrientation] = []

      pr = partRotations[rodOrientation]
      rodDir = pr['rodDir']

      if len(shape) > 1:
        self.rodLoc[rodOrientation].append(generateLocations((0, 0, 0), rodDir, len(shape)))

      for i in range(len(shape)):
        pos, neg = shape[i]

        if pos != neg:
          stickDir = pr['stickDirs'][i % 2]
          refLoc = [rodDir[d] * i - stickDir[d] * neg for d in range(3)]
          self.stickLoc[rodOrientation].append(generateLocations(refLoc, stickDir, pos + neg + 1))

class Grid:
  def addPart(self, part, position, lowestConnectedPart = -1):
    part.pos = position
    part.lowestConnectedPart = lowestConnectedPart

    # TODO

  def removePart(self, part):
    del part.pos
    del part.lowestConnectedPart

    # TODO

  def getPositions(self, part, fromPart):
    # TODO

    return []
    

def makeParts(numbers, shapes):
  parts = []
  for shapeNum in range(len(numbers)):
    for p in range(numbers[shapeNum]):
      part = Part(shapes[shapeNum])
      part.index = len(parts)
      part.shapeNum = shapeNum
      parts.append(part)

  return parts

def solve(partNumber):
  if partNumber == len(parts):
    print("Solved!")
    return

  part = parts[partNumber]

  sameShape = parts[partNumber].shape == parts[partNumber - 1].shape
  if sameShape:
    startAtPartNumber = parts[partNumber - 1].lowestConnectedPart
  else:
    startAtPartNumber = 0

  for fromPartNumber in range(startAtPartNumber, partNumber):
    positions = grid.getPositions(part, parts[fromPartNumber])

    for pos in positions:
      if not sameShape or pos > parts[partNumber - 1].pos:
        grid.addPart(part, pos, fromPartNumber)
        solve(partNumber + 1)
        grid.removePart(part, pos)

parts = makeParts(pineApplePilePartNumbers, pineApplePileShapes)
grid = Grid()

grid.addPart(parts[0], Position(Orientation.X, (0, 0, 0)))

solve(1) 


