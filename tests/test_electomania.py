import unittest

from ingest.electomania import extract_poll


class ElectomaniaTest(unittest.TestCase):
    def _post(self, text, title="ElectoPanel (18 oct)"):
        return {
            "title": {"rendered": title},
            "content": {"rendered": "<p>" + text + "</p>"},
            "link": "https://electomania.es/electopanel-18-oct/",
            "date": "2026-10-18T20:00:00",
        }

    def test_frente_amplio_maps_to_sumar(self):
        text = (
            "El PP sube al 31,8%, el PSOE baja al 27,1% y Vox queda en el 18,9%. "
            "Frente Amplio, que concurre por primera vez como coalición estatal, "
            "obtiene el 4,9%; Podemos, 2,1%; Se Acabó la Fiesta, 1,7%; ERC, 2,1%; "
            "EH Bildu, 1,4%; Junts, 1,2%; PNV, 1,0%. Tamaño muestral: 3.141"
        )
        poll = extract_poll(self._post(text))
        self.assertIsNotNone(poll)
        self.assertEqual(poll["values"]["SUMAR"], 4.9)
        self.assertAlmostEqual(sum(poll["values"].values()), 92.2, places=1)
        self.assertEqual(poll["sample"], 3141)
        self.assertEqual(poll["pollster"], "ElectoPanel")


if __name__ == "__main__":
    unittest.main()
