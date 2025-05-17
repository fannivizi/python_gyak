import unittest
import python_gyak.models as models

class TestAPI(unittest.TestCase):
    def setUp(self):
        self.api = models.API()

    def test_get_all(self):
        shows = self.api.get_all()
        self.assertIsInstance(shows, list)
        self.assertGreater(len(shows), 0)

    def test_get_show(self):
        show = self.api.get_show(1)
        self.assertIsInstance(show, dict)
        self.assertEqual(show['id'], 1)

    def test_get_episodes(self):
        seasons = self.api.get_episodes(1)
        self.assertIsInstance(seasons, dict)
        self.assertGreater(len(seasons), 0)

    def test_get_episode(self):
        episode = self.api.get_episode(1)
        self.assertIsInstance(episode, dict)
        self.assertEqual(episode['id'], 1)