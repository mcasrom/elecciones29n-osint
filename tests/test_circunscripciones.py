import json
import os
import unittest

from gen import circunscripciones

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class CircunscripcionesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.oficial = json.load(open(os.path.join(ROOT, "data", "congreso-oficial.json"), encoding="utf-8"))
        cls.escanos = json.load(open(os.path.join(ROOT, "data", "escanos_2026.json"), encoding="utf-8"))
        cls.censo = json.load(open(os.path.join(ROOT, "data", "censo_2026.json"), encoding="utf-8"))
        cls.pages = circunscripciones.build_pages(cls.oficial, cls.escanos, cls.censo)

    def test_52_paginas(self):
        self.assertEqual(len(self.pages), 52)
        slugs = [p["slug"] for p in self.pages]
        self.assertEqual(len(slugs), len(set(slugs)))
        self.assertIn("madrid", slugs)
        self.assertIn("barcelona", slugs)
        self.assertIn("teruel", slugs)
        self.assertIn("a-coruna", slugs)
        self.assertIn("baleares", slugs)

    def test_datos_minimos(self):
        for p in self.pages:
            self.assertEqual(len(p["resultados"]), 2)
            self.assertIn("2023-07-23", p["marginales"])
            self.assertIn("2019-11-10", p["marginales"])
            self.assertGreater(p["escanos_2026"], 0)
            self.assertGreater(p["electores_2026"], 0)
            self.assertEqual(p["calc"]["escanos"], p["escanos_2026"])
            self.assertIn("2023-07-23", p["calc"]["years"])
            self.assertIn("2019-11-10", p["calc"]["years"])

    def test_marginales(self):
        m = next(p for p in self.pages if p["slug"] == "teruel")["marginales"]["2019-11-10"]
        self.assertIsNotNone(m["ultimo"])
        self.assertIsNotNone(m["siguiente"])
        self.assertGreaterEqual(m["margen_votos"], 0)

    def test_teruel_2019_primera_fuera_es_vox(self):
        m = next(p for p in self.pages if p["slug"] == "teruel")["marginales"]["2019-11-10"]
        self.assertEqual(m["siguiente"]["escanos"], 0)
        self.assertIn("VOX", m["siguiente"]["etiqueta"])
        self.assertEqual(m["margen_votos"], 8175)

    def test_orden_y_enlaces(self):
        nombres = [p["nombre"] for p in self.pages]
        self.assertEqual(nombres, sorted(nombres))
        self.assertIsNone(self.pages[0]["prev"])
        self.assertIsNone(self.pages[-1]["next"])
        self.assertEqual(self.pages[0]["next"]["slug"], self.pages[1]["slug"])
        self.assertEqual(self.pages[1]["prev"]["slug"], self.pages[0]["slug"])

    def test_slug(self):
        self.assertEqual(circunscripciones.slugify("Araba/Álava"), "alava")
        self.assertEqual(circunscripciones.slugify("Coruña, A"), "a-coruna")
        self.assertEqual(circunscripciones.slugify("Valencia / València"), "valencia")
        self.assertEqual(circunscripciones.slugify("Madrid"), "madrid")


if __name__ == "__main__":
    unittest.main()
