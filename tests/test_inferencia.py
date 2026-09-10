"""Testes unitários do preditor desacoplado da CNN."""

import unittest
from PIL import Image, ImageDraw
import numpy as np

from mnist_demo.inferencia import PreditorCNN, RAIZ


class TestInferênciaCNN(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.preditor = PreditorCNN()

    def test_modelo_e_calibracao_disponiveis(self):
        self.assertTrue(
            self.preditor.disponivel,
            "Os artefatos da CNN (cnn.keras, calibracao_cnn.json, preprocessamento.json) devem existir."
        )

    def test_predicao_em_imagem_sintetica(self):
        # Cria dígito 1 (traço vertical centralizado)
        img = Image.new("RGB", (100, 100), color="white")
        draw = ImageDraw.Draw(img)
        draw.line([(50, 15), (50, 85)], fill="black", width=12)

        res = self.preditor.predizer(img, fundo="claro")
        self.assertIn("previsto", res)
        self.assertIn(res["previsto"], range(10))
        self.assertGreaterEqual(res["confianca"], 0.0)
        self.assertLessEqual(res["confianca"], 1.0)
        self.assertEqual(len(res["probabilidades"]), 10)
        self.assertAlmostEqual(sum(res["probabilidades"]), 1.0, places=4)
        self.assertIn("etapas", res)
        for etapa in ["original", "cinza", "contraste", "traco", "entrada"]:
            self.assertIn(etapa, res["etapas"])
            self.assertTrue(res["etapas"][etapa].startswith("data:image/png;base64,"))


if __name__ == "__main__":
    unittest.main()
