import unittest

from app.config import load_config


class ConfigTests(unittest.TestCase):
    def test_default_config_loads(self) -> None:
        config = load_config()
        self.assertEqual(config.app.name, "IA Offline Portatil")
        self.assertEqual(config.model.context_window, 2048)


if __name__ == "__main__":
    unittest.main()
