import unittest

from scripts.newsletter_provincia import province_block


class NewsletterProvinceTest(unittest.TestCase):
    def setUp(self):
        self.prov = {"madrid": {
            "nombre": "Madrid", "slug": "madrid", "escanos_2026": 38,
            "electores_2026": 5536913, "participacion_2023": 69.66,
            "resultados": [{"candidaturas": [
                {"acronimo": "PP", "votos": 100, "escanos": 16},
                {"acronimo": "PSOE", "votos": 90, "escanos": 10},
            ]}],
            "marginales": {"2023-07-23": {"ultimo": {"etiqueta": "PARTIDO POPULAR - PP"}, "margen_votos": None}},
        }}

    def test_province_block(self):
        html, text = province_block("madrid", self.prov)
        self.assertIn("Tu provincia: Madrid", html)
        self.assertIn("38 diputados", text)
        self.assertIn("PP 16 · PSOE 10", text)

    def test_unknown_province(self):
        self.assertEqual(province_block("nope", self.prov), ("", ""))


if __name__ == "__main__":
    unittest.main()
