import unittest
import renderer
import map

class TestUtilities(unittest.TestCase):
    def test_clamp(self):
        self.assertEqual(renderer.clamp(50, 0, 100), 50)
        self.assertEqual(renderer.clamp(-5, 0, 100), 95)
        self.assertEqual(renderer.clamp(106, 0, 100), 6)
        self.assertEqual(renderer.clamp(2, 0, 1), 0)
        self.assertEqual(renderer.clamp(-1, 0, 1), 1)

class TestBackgroundBuffer(unittest.TestCase):
    def setUp(self):
        self.game_map = map.Map()
        map_data = b'\x00'*(map.Map.section_width * map.Map.section_height)
        map_data += b'\x01'*(map.Map.section_width * map.Map.section_height)
        attr_data = b'\x00'*(map.Map.section_width * map.Map.section_height * 2)
        self.game_map.load(map_data)
        self.game_map.load_attr_map(attr_data)
        self.game_map.load_mapmap(b'\x00\x02\x00\x01\x00\x01')

    def test_map(self):
        self.assertEqual(self.game_map.map_width, 2)
        self.assertEqual(self.game_map.map_height, 1)
        self.assertEqual(len(self.game_map.sections), 2)
        self.assertEqual(len(self.game_map.attr_sections), 2)
