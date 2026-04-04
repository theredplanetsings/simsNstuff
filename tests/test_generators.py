import unittest

import numpy as np

from generators import generate_petroleum_deposits, generate_realistic_deposits


class GeneratorContractTests(unittest.TestCase):
    def test_mineral_generation_is_deterministic(self):
        first = generate_realistic_deposits("Gold", "Orebody systems", 120, 42, 1.0, 3)
        second = generate_realistic_deposits("Gold", "Orebody systems", 120, 42, 1.0, 3)
        self.assertTrue(np.array_equal(first, second))

    def test_mineral_generation_returns_n_by_3(self):
        modes = [
            "Orebody systems",
            "Hydrothermal veins",
            "Sedimentary layers",
            "Contact metamorphic",
            "Placer deposits",
        ]
        for mode in modes:
            coords = generate_realistic_deposits("Copper", mode, 75, 11, 1.2, 4)
            self.assertEqual(coords.shape, (75, 3))

    def test_petroleum_generation_is_deterministic(self):
        first = generate_petroleum_deposits("Oil", 50, 4, 0.6, 42)
        second = generate_petroleum_deposits("Oil", 50, 4, 0.6, 42)
        self.assertTrue(np.array_equal(first, second))

    def test_petroleum_generation_has_three_columns(self):
        types = ["Oil", "Natural Gas", "Oil Shale", "Gas Hydrates"]
        for deposit_type in types:
            coords = generate_petroleum_deposits(deposit_type, 40, 3, 0.5, 7)
            self.assertEqual(coords.ndim, 2)
            self.assertEqual(coords.shape[1], 3)


if __name__ == "__main__":
    unittest.main()
