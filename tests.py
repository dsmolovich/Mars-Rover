import unittest
from nasa import *

class TestCompass(unittest.TestCase):
    def test_rotation(self):
        compass = Compass()
        self.assertEqual(compass.rotate_clockwise(), 'E')
        self.assertEqual(compass.rotate_counterclockwise(), 'N')
        self.assertEqual(compass.rotate_counterclockwise(), 'W')
        self.assertEqual(compass.rotate_counterclockwise(), 'S')
        self.assertEqual(compass.rotate_counterclockwise(), 'E')
        self.assertEqual(compass.rotate_counterclockwise(), 'N')

    def test_set_direction(self):
        with self.assertRaises(UnknownDirection):
            Compass('A')
        compass = Compass('E')
        self.assertEqual(compass.get_direction(), 'E')
        compass = Compass('S')
        self.assertEqual(compass.get_direction(), 'S')

class TestPlane(unittest.TestCase):
    def test_boundaries(self):
        plateau = Plateau(5, 5)
        self.assertEqual(plateau.is_in_range(5,5), True)
        self.assertEqual(plateau.is_in_range(6,5), False)
        self.assertEqual(plateau.is_in_range(5,6), False)
        self.assertEqual(plateau.is_in_range(-1,0), False)
        self.assertEqual(plateau.is_in_range(0,-1), False)

class TestRover(unittest.TestCase):
    def test_rotation(self):
        rover = Rover('Rover1', 1, 2, Compass('N'), Plateau(5, 5))
        self.assertEqual(rover.turn_left(), 'W')
        self.assertEqual(rover.turn_right(), 'N')
        self.assertEqual(rover.turn_right(), 'E')

    def test_movement(self):
        rover = Rover('Rover1', 0, 0, Compass('N'), Plateau(5, 5))
        self.assertEqual(rover.move(), (0, 1))
        self.assertEqual(rover.move(), (0, 2))
        rover = Rover('Rover1', 0, 0, Compass('E'), Plateau(5, 5))
        self.assertEqual(rover.move(), (1, 0))
        self.assertEqual(rover.move(), (2, 0))

    def test_process_commands(self):
        rover = Rover('Rover1', 1, 2, Compass('N'), Plateau(5, 5))
        self.assertEqual(rover.process_commands('LMLMLMLMM'), ('Rover1', 1, 3, 'N'))
        rover = Rover('Rover2', 3, 3, Compass('E'), Plateau(5, 5))
        self.assertEqual(rover.process_commands('MMRMMRMRRM'), ('Rover2', 5, 1, 'E'))

    def test_wrong_landing(self):
        with self.assertRaises(OutsideOfThePlateau):
            Rover('Rover1', -1, -1, Compass('N'), Plateau(5, 5))
            Rover('Rover1', 0, 0, Compass('N'), Plateau(0, 0))

    def test_goes_out_of_plateau(self):
        rover = Rover('Rover1', 0, 0, Compass('S'), Plateau(0, 0))
        with self.assertRaises(OutsideOfThePlateau):
            rover.move()
        rover = Rover('Rover1', 5, 5, Compass('N'), Plateau(5, 5))
        with self.assertRaises(OutsideOfThePlateau):
            rover.move()

class TestNasaControl(unittest.TestCase):
    def test_parse_plateau_config(self):
        nasa_control = NasaControl()
        self.assertEqual(nasa_control.parse_plateau_config('Plateau:5 5'), {'width': 5, 'length': 5})
        self.assertEqual(nasa_control.parse_plateau_config('Plateau: 0 0'), {'width': 0, 'length': 0})
        self.assertEqual(nasa_control.parse_plateau_config('  Plateau : 12    35   '), {'width': 12, 'length': 35})
        self.assertEqual(nasa_control.parse_plateau_config(''), False)

    def test_parse_landing_config(self):
        nasa_control = NasaControl()
        self.assertEqual(nasa_control.parse_landing_config('Rover1 Landing:1 2 N'), {'name': 'Rover1', 'x': 1, 'y': 2, 'direction': 'N'})
        self.assertEqual(nasa_control.parse_landing_config('  Rover1   Landing :  3   5  N'), {'name': 'Rover1', 'x': 3, 'y': 5, 'direction': 'N'})
        self.assertEqual(nasa_control.parse_landing_config(''), False)

    def test_parse_rover_instructions(self):
        nasa_control = NasaControl()
        self.assertEqual(nasa_control.parse_rover_instructions('Rover1 Instructions:LMLMLMLMM'), {'name': 'Rover1', 'instructions': 'LMLMLMLMM'})
        self.assertEqual(nasa_control.parse_rover_instructions('  Rover1   Instructions  : LMLMLMLMM  '), {'name': 'Rover1', 'instructions': 'LMLMLMLMM'})
        self.assertEqual(nasa_control.parse_rover_instructions(''), False)

    def test_parse_line(self):
        nasa_control = NasaControl()

        with self.assertRaises(ParseError):
            nasa_control.parse_line('')

        with self.assertRaises(ParseError):
            nasa_control.parse_line('21900b86b9de9288b4adbf5b05b3826c')

        with self.assertRaises(RoverIsUndefined):
            nasa_control.parse_line('Rover1 Instructions:LMLMLMLMM')


        with self.assertRaises(PlateauIsUndefined):
            nasa_control.parse_line('Rover1 Landing:1 2 N')

        obj = nasa_control.parse_line('Plateau:5 7')
        self.assertEqual(obj.width, 5)
        self.assertEqual(obj.length, 7)

        obj = nasa_control.parse_line('Rover1 Landing:1 2 N')
        self.assertEqual(obj.name, 'Rover1')
        self.assertEqual(obj.x, 1)
        self.assertEqual(obj.y, 2)
        self.assertEqual(obj.compass.get_direction(), 'N')

        obj = nasa_control.parse_line('Rover1 Instructions:LMLMLMLMM')
        self.assertEqual(obj[0], 'Rover1')
        self.assertEqual(obj[1], 1)
        self.assertEqual(obj[2], 3)
        self.assertEqual(obj[3], 'N')


if __name__ == '__main__':
    unittest.main()