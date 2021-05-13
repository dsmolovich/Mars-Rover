import re

class UnknownDirection(Exception):
    pass


class OutsideOfThePlateau(Exception):
    pass


class PlateauIsUndefined(Exception):
    pass


class RoverIsUndefined(Exception):
    pass


class ParseError(Exception):
    pass


class Compass:
    directions = ('N', 'E', 'S', 'W')
    pointer = 0

    def __init__(self, direction = 'N'):
        if direction not in self.directions:
            raise UnknownDirection('{} is not in the range N, E, S, W'.format(direction))
        while self.get_direction() != direction:
            self.rotate_clockwise()

    def rotate_clockwise(self):
        self.pointer = (self.pointer + 1) % 4
        return self.get_direction()

    def rotate_counterclockwise(self):
        self.pointer = (self.pointer - 1) % 4
        return self.get_direction()

    def get_direction(self):
        return self.directions[self.pointer]


class Plateau:
    def __init__(self, width, length):
        self.width = int(width)
        self.length = int(length)

    def is_in_range(self, x, y):
        if x < 0:
            return False
        if y < 0:
            return False
        if x > self.width:
            return False
        if y > self.length:
            return False
        return True


class Rover:
    def __init__(self, name, x, y, compass, plateau):
        self.name, self.plateau, self.compass = name, plateau, compass
        x, y = int(x), int(y)
        if not self.plateau.is_in_range(x, y):
            raise OutsideOfThePlateau("Expected rover's landing coordinates ({},{}) are out of plateau's range ({},{})".format(x,y,self.plateau.width,self.plateau.length))
        self.x, self.y = x, y

    def turn_left(self):
        return self.compass.rotate_counterclockwise()

    def turn_right(self):
        return self.compass.rotate_clockwise()

    def move(self):
        current_direction = self.compass.get_direction()
        x, y = self.x, self.y
        if current_direction == 'N':
            y += 1
        elif current_direction == 'S':
            y -= 1
        elif current_direction == 'E':
            x += 1
        elif current_direction == 'W':
            x -= 1
        if not self.plateau.is_in_range(x, y):
            raise OutsideOfThePlateau("Expected rover's destination ({},{}) is out of plateau's range ({},{})".format(x,y,self.plateau.width,self.plateau.length))
        self.x, self.y = x, y
        return (self.x, self.y)

    def report_status(self):
        return (self.name, self.x, self.y, self.compass.get_direction())

    def process_commands(self, directions):
        for direction in directions:
            if direction == 'L':
                self.compass.rotate_counterclockwise()
            elif direction == 'R':
                self.compass.rotate_clockwise()
            else:
                self.move()
        return self.report_status()


class NasaControl:
    plateau = None
    rovers = {}

    def parse_line(self, line):
        # try to read plateau info
        data = self.parse_plateau_config(line)
        if data:
            self.plateau = Plateau(data['width'], data['length'])
            return self.plateau

        # try to read landing info
        data = self.parse_landing_config(line)
        if data:
            if not self.plateau:
                raise PlateauIsUndefined('Plateau must be define before landing')
            compass = Compass(data['direction'])
            rover = Rover(data['name'], data['x'], data['y'], compass, self.plateau)
            self.rovers[data['name']] = rover
            return rover

        # try to read rover instructions info
        data = self.parse_rover_instructions(line)
        if data:
            if data['name'] not in self.rovers:
                raise RoverIsUndefined('Rover "{}" must be landed before accepting any instructions'.format(data['name']))
            rover = self.rovers[data['name']]
            rover_status = rover.process_commands(data['instructions'])
            return rover_status

        raise ParseError("Unable to parse - \"{}\"".format(line))

    def parse_plateau_config(self, str):
        m = re.search('^\s*Plateau\s*:\s*(\d+)\s+(\d+)\s*$', str)
        if not m:
            return False
        width, length = int(m.group(1)), int(m.group(2))
        return {'width': width, 'length': length}

    def parse_landing_config(self, str):
        m = re.search('^\s*(.*?)\s+Landing\s*:\s*(\d+)\s+(\d+)\s+([NESW])\s*$', str)
        if not m:
            return False
        x, y = int(m.group(2)), int(m.group(3))
        return {'name': m.group(1), 'x': x, 'y': y, 'direction': m.group(4)}

    def parse_rover_instructions(self, str):
        m = re.search('^\s*(.*?)\s+Instructions\s*:\s*([MLR]+)\s*$', str)
        if not m:
            return False
        return {'name': m.group(1), 'instructions': m.group(2)}
