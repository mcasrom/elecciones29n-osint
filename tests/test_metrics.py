import os
import re
import unittest

from metrics import moving_average, series_span, spark_summary
from gen.build import build_sparklines


class MetricsTest(unittest.TestCase):
    def test_moving_average_smooths_outlier(self):
        pts = [
            {"date": "2026-10-01", "value": 30.0},
            {"date": "2026-10-02", "value": 30.0},
            {"date": "2026-10-03", "value": 30.0},
            {"date": "2026-10-04", "value": 20.0},
        ]
        ma = moving_average(pts)
        self.assertAlmostEqual(ma[-1]["value"], 27.5, places=2)
        self.assertAlmostEqual(pts[-1]["value"], 20.0, places=2)
        self.assertNotAlmostEqual(ma[-1]["value"], pts[-1]["value"], places=2)

    def test_summary_uses_ma(self):
        pts = [
            {"date": "2026-01-01", "value": 10.0},
            {"date": "2026-01-10", "value": 20.0},
            {"date": "2026-01-20", "value": 30.0},
        ]
        s = spark_summary(pts)
        self.assertAlmostEqual(s["last"], 30.0, places=2)
        self.assertAlmostEqual(s["first"], 10.0, places=2)
        self.assertAlmostEqual(s["delta"], 20.0, places=2)

    def test_series_span(self):
        series = {"PP": [{"date": "2026-07-23"}, {"date": "2026-10-14"}],
                  "PSOE": [{"date": "2026-08-01"}]}
        self.assertEqual(series_span(series), "2026-07-23 – 2026-10-14")

    def test_sparkline_prints_ma_not_last_poll(self):
        series = {"PP": [
            {"date": "2026-10-01", "value": 30.0},
            {"date": "2026-10-02", "value": 30.0},
            {"date": "2026-10-03", "value": 30.0},
            {"date": "2026-10-04", "value": 20.0},
        ]}
        html = build_sparklines(series, [{"party": "PP", "mean": 27.5}])
        m = re.search(r"<b>([0-9.]+)%</b>", html)
        self.assertIsNotNone(m)
        self.assertAlmostEqual(float(m.group(1)), 27.5, places=1)
        self.assertIn("0.0 pts", html)


if __name__ == "__main__":
    unittest.main()
