import json
import os
import unittest

from agg.dhondt import reparto

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CON = os.path.join(ROOT, "data", "congreso-oficial.json")


class CongresoOficialTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d = json.load(open(CON, encoding="utf-8"))
        cls.e19 = cls.d["elecciones"]["2019-11-10"]
        cls.e23 = cls.d["elecciones"]["2023-07-23"]

    def test_elecciones(self):
        self.assertEqual(set(self.d["elecciones"]), {"2019-11-10", "2023-07-23"})
        for e in (self.e19, self.e23):
            self.assertEqual(len(e["provincias"]), 52)
            self.assertEqual(sum(c["escanos"] for p in e["provincias"] for c in p["candidaturas"]), 350)

    def test_meta(self):
        self.assertEqual(len(self.d["meta"]["sha256"]), 64)
        self.assertIn("CERA", self.d["meta"]["nota"])

    def test_validos_y_cera(self):
        for e in (self.e19, self.e23):
            for p in e["provincias"]:
                self.assertEqual(sum(c["votos"] for c in p["candidaturas"]) + p["blancos"], p["validos"], p["nombre"])
                self.assertEqual(sum(c["cera"] for c in p["candidaturas"]), p["cera_total"], p["nombre"])
                self.assertTrue(all(c["cera"] <= c["votos"] for c in p["candidaturas"]), p["nombre"])

    def test_etiquetas_historicas(self):
        labels19 = {c["etiqueta"] for p in self.e19["provincias"] for c in p["candidaturas"]}
        labels23 = {c["etiqueta"] for p in self.e23["provincias"] for c in p["candidaturas"]}
        self.assertFalse(any("SUMAR" in x.upper() for x in labels19), "SUMAR no existía en 2019")
        self.assertTrue(any("SUMAR" in x.upper() for x in labels23))

    def test_nacionales_2023(self):
        esc = {}
        for p in self.e23["provincias"]:
            for c in p["candidaturas"]:
                esc[c["acronimo"]] = esc.get(c["acronimo"], 0) + c["escanos"]
        self.assertEqual(esc.get("PP"), 137)
        psoe = sum(v for k, v in esc.items() if k in {"PSOE", "PSC", "PSE-EE (PSOE)", "PSIB-PSOE", "PSdeG-PSOE", "PSN-PSOE"})
        sumar = sum(v for k, v in esc.items() if k.startswith("SUMAR") or k in {"COMPROMÍS", "ECP", "MÉS PER MALLORCA-MÉS PER MENORCA-SUMAR"})
        self.assertEqual(psoe, 121)
        self.assertEqual(esc.get("VOX"), 33)
        self.assertEqual(sumar, 31)

    def test_provincias_clave(self):
        for e, nombre, n in ((self.e23, "Madrid", 37), (self.e23, "Barcelona", 32), (self.e23, "Teruel", 3)):
            p = next(p for p in e["provincias"] if p["nombre"] == nombre)
            self.assertEqual(sum(c["escanos"] for c in p["candidaturas"]), n)

    def test_dhondt_reproduce_oficial(self):
        for fecha, e in (("2019-11-10", self.e19), ("2023-07-23", self.e23)):
            for p in e["provincias"]:
                esperado = {c["etiqueta"]: c["escanos"] for c in p["candidaturas"]}
                n = sum(esperado.values())
                self.assertEqual(reparto(p["candidaturas"], n, p["validos"]), esperado, f"{fecha} {p['nombre']}")


if __name__ == "__main__":
    unittest.main()
