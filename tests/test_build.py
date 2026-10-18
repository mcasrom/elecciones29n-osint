import unittest

from gen.build import build_chart, simulate_congress


class BuildTest(unittest.TestCase):
    def test_chart_with_one_point_renders(self):
        parties = [{"party": "PP", "mean": 30}]
        svg = build_chart({"PP": [{"date": "2026-10-11", "value": 30}]}, parties)
        self.assertIn("<svg", svg)
        self.assertIn("<circle", svg)

    def test_chart_without_points_has_placeholder(self):
        svg = build_chart({}, [])
        self.assertIn("Sin datos suficientes", svg)

    def test_chart_renders(self):
        parties = [{"party": "PP", "mean": 30}, {"party": "PSOE", "mean": 27}]
        series = {
            "PP": [
                {"date": "2026-10-04", "value": 31},
                {"date": "2026-10-11", "value": 30},
            ],
            "PSOE": [
                {"date": "2026-10-04", "value": 26},
                {"date": "2026-10-11", "value": 27},
            ],
        }
        svg = build_chart(series, parties)
        self.assertIn("<svg", svg)
        self.assertEqual(svg.count("<circle"), 4)

    def test_dhondt_sums_350(self):
        parties = [
            {"party": "PP", "mean": 31.5},
            {"party": "PSOE", "mean": 26.9},
            {"party": "VOX", "mean": 19.1},
            {"party": "SUMAR", "mean": 5.0},
            {"party": "ERC", "mean": 2.0},
        ]
        seats = simulate_congress(parties)
        self.assertEqual(sum(seats.values()), 350)
        self.assertGreater(seats["PP"], seats["PSOE"])


if __name__ == "__main__":
    unittest.main()
