import re
import unittest

from gen.build import build_chart, build_hemicycle, build_hemicycle_svg, simulate_congress


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

    def test_hemicycle_svg_has_350_seats(self):
        svg = build_hemicycle_svg([
            {"party": "PP", "seats": 127},
            {"party": "PSOE", "seats": 118},
            {"party": "VOX", "seats": 79},
            {"party": "SUMAR", "seats": 26},
        ])
        self.assertIn("<svg", svg)
        self.assertEqual(svg.count("<circle"), 350)
        self.assertIn('fill="#3b82f6"', svg)  # PP
        self.assertIn("Izquierda", svg)
        self.assertIn("Derecha", svg)

    def test_hemicycle_svg_pads_missing_seats(self):
        svg = build_hemicycle_svg([{"party": "PP", "seats": 200}])
        self.assertEqual(svg.count("<circle"), 350)

    def test_hemicycle_parties_form_wedges(self):
        svg = build_hemicycle_svg([
            {"party": "PP", "seats": 127},
            {"party": "PSOE", "seats": 118},
            {"party": "VOX", "seats": 79},
            {"party": "SUMAR", "seats": 26},
        ])
        self.assertEqual(svg.count("<title>PP</title>"), 127)
        self.assertEqual(svg.count("<title>PSOE</title>"), 118)
        self.assertEqual(svg.count("<title>VOX</title>"), 79)
        self.assertEqual(svg.count("<title>SUMAR</title>"), 26)
        rows = {
            cy for cy in re.findall(
                r'<circle[^>]*cy="([\d.]+)"[^>]*><title>SUMAR</title>', svg
            )
        }
        self.assertGreaterEqual(len(rows), 8)

    def test_build_hemicycle_labels_and_blocks(self):
        entries = [{
            "date": "2026-10-23", "is_current": True,
            "window_start": "2026-10-10",
            "n_polls": 9, "n_houses": 7, "low_n": False,
            "seats": [{"party": "PP", "seats": 200}, {"party": "PSOE", "seats": 150}],
            "blocks": {"right": 200, "left": 150, "others": 0},
            "majority": "right",
        }]
        h = build_hemicycle(entries)[0]
        self.assertIn("hoy", h["label"])
        self.assertEqual(h["majority_label"], "PP + VOX")
        self.assertIn("10 oct 2026", h["window_label"])
        self.assertEqual(h["seat_rows"][0]["color"], "#3b82f6")
        self.assertEqual(h["svg"].count("<circle"), 350)


if __name__ == "__main__":
    unittest.main()
