"""Testes de integridade do manifesto e fotos de imagens próprias."""

import csv
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
PASTA_IMAGENS = RAIZ / "data" / "imagens_proprias"


class TestManifestoImagensProprias(unittest.TestCase):
    def setUp(self):
        self.caminho_manifesto = PASTA_IMAGENS / "manifesto.csv"
        self.assertTrue(self.caminho_manifesto.is_file(), "manifesto.csv não encontrado")

    def test_integridade_e_quantidade_de_registros(self):
        with open(self.caminho_manifesto, encoding="utf-8", newline="") as f:
            leitor = list(csv.DictReader(f))

        self.assertEqual(len(leitor), 30, "O manifesto deve conter exatamente 30 registros")

        ids = [r["id"] for r in leitor]
        self.assertEqual(len(ids), len(set(ids)), "Os IDs do manifesto devem ser únicos")

        dev_count = sum(1 for r in leitor if r["finalidade"] == "desenvolvimento")
        aval_count = sum(1 for r in leitor if r["finalidade"] == "avaliacao")
        self.assertEqual(dev_count, 10, "Devem existir 10 imagens de desenvolvimento")
        self.assertEqual(aval_count, 20, "Devem existir 20 imagens de avaliação reservada")

        for linha in leitor:
            rotulo = int(linha["rotulo"])
            self.assertIn(rotulo, range(10), "O rótulo deve ser um dígito entre 0 e 9")

            x0, y0, x1, y1 = int(linha["x0"]), int(linha["y0"]), int(linha["x1"]), int(linha["y1"])
            self.assertGreater(x1, x0, "Coordenada x1 deve ser maior que x0")
            self.assertGreater(y1, y0, "Coordenada y1 deve ser maior que y0")

            caminho_foto = PASTA_IMAGENS / linha["arquivo_foto"]
            self.assertTrue(caminho_foto.is_file(), f"Foto {linha['arquivo_foto']} não encontrada")


if __name__ == "__main__":
    unittest.main()
