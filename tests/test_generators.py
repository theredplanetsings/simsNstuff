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

    def test_mineral_generation_returns_empty_array_for_zero_points(self):
        coords = generate_realistic_deposits("Copper", "Placer deposits", 0, 11, 1.2, 4)
        self.assertEqual(coords.shape, (0, 3))

    def test_mineral_generation_rejects_invalid_mode(self):
        with self.assertRaisesRegex(ValueError, "Unsupported mineral mode"):
            generate_realistic_deposits("Copper", "Invalid mode", 10, 11, 1.2, 4)

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

    def test_petroleum_generation_returns_empty_array_for_zero_reservoirs(self):
        coords = generate_petroleum_deposits("Oil", 50, 0, 0.6, 42)
        self.assertEqual(coords.shape, (0, 3))

    def test_petroleum_generation_rejects_invalid_type(self):
        with self.assertRaisesRegex(ValueError, "Unsupported petroleum deposit type"):
            generate_petroleum_deposits("Water", 50, 1, 0.6, 42)


if __name__ == "__main__":
    unittest.main()
