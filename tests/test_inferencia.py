"""Testes unitários do preditor desacoplado da CNN.

A CNN treinada fica em `artifacts/`, que é ignorado pelo Git e recriado pelo
notebook. Por isso os testes se dividem em dois grupos: a recusa explícita
quando os artefatos não existem, verificada em qualquer ambiente, e a predição
completa, executada apenas onde a CNN já foi gerada.
"""

import tempfile
import unittest
from pathlib import Path

from PIL import Image, ImageDraw

from mnist_demo.inferencia import PreditorCNN

ARTEFATOS_PRESENTES = PreditorCNN().disponivel
MOTIVO = "Artefatos da CNN ausentes; execute o notebook para gerar artifacts/."


def digito_sintetico() -> Image.Image:
    """Crie um traço vertical escuro sobre fundo claro."""
    imagem = Image.new("RGB", (100, 100), color="white")
    ImageDraw.Draw(imagem).line([(50, 15), (50, 85)], fill="black", width=12)
    return imagem


class TestPreditorSemArtefatos(unittest.TestCase):
    """Recusa explícita quando a CNN ainda não foi gerada pelo notebook."""

    def test_recusa_com_mensagem_quando_modelo_ausente(self):
        with tempfile.TemporaryDirectory() as vazio:
            preditor = PreditorCNN(Path(vazio))
            self.assertFalse(preditor.disponivel)
            with self.assertRaises(FileNotFoundError):
                preditor.predizer(digito_sintetico())


@unittest.skipUnless(ARTEFATOS_PRESENTES, MOTIVO)
class TestInferênciaCNN(unittest.TestCase):
    """Predição completa; exige a CNN e a calibração em artifacts/."""

    @classmethod
    def setUpClass(cls):
        cls.preditor = PreditorCNN()

    def test_predicao_em_imagem_sintetica(self):
        res = self.preditor.predizer(digito_sintetico(), fundo="claro")
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
