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

class Part:
  def __init__(self, shapeNum):
    self.shapeNum = shapeNum

class Grid:
  def addPart(self, part, position, lowestConnectedPart = -1):
    part.pos = position
    part.lowestConnectedPart = lowestConnectedPart

    # TODO

  def removePart(self, part):
    del part.pos
    del part.lowestConnectedPart

    # TODO

  def getPositions(part, fromPart):
    # TODO

    return []
    

def makeParts(numbers, shapes):
  # TODO
  return [Part(0)]

def solve(partNumber):
  if partNumber == len(parts):
    print("Solved!")
    return

  part = parts[partNumber]

  sameShape = part[partNumber].shape == part[partNumber - 1].shape
  if sameShape:
    startAtPartNumber = part[partNumber - 1].lowestConnectedPart
  else:
    startAtPartNumber = 0

  for fromPartNumber in range(startAtPartNumber, partNumber):
    positions = grid.getPositions(part, part[fromPartNumber])

    for pos in positions:
      if not sameShape or pos > part[partNumber - 1].pos:
        grid.addPart(part, pos, fromPartNumber)
        solve(partNumber + 1)
        grid.removePart(part, pos)

parts = makeParts(pineApplePilePartNumbers, pineApplePileShapes)
grid = Grid()

grid.addPart(parts[0], Position(Orientation.X, (0, 0, 0)))

solve(1) 


