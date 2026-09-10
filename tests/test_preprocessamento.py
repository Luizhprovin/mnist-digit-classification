"""Testes unitários do pipeline de pré-processamento de imagens."""

import unittest
import numpy as np
from PIL import Image, ImageDraw

from mnist_demo.preprocessamento import etapas_digito, preparar_digito


class TestPreprocessamento(unittest.TestCase):
    def test_rejeita_imagem_muito_pequena(self):
        img = Image.new("RGB", (1, 1), color="white")
        with self.assertRaises(ValueError):
            etapas_digito(img)

    def test_rejeita_imagem_sem_traco(self):
        # Imagem totalmente branca
        img = Image.new("RGB", (100, 100), color="white")
        with self.assertRaises(ValueError):
            etapas_digito(img)

    def test_processa_digito_sintetico_com_sucesso(self):
        # Cria um quadrado escuro sobre fundo branco
        img = Image.new("RGB", (100, 100), color="white")
        draw = ImageDraw.Draw(img)
        draw.line([(30, 20), (30, 80), (70, 80)], fill="black", width=10)

        etapas = etapas_digito(img)
        chaves_esperadas = {"cinza", "fundo", "contraste", "traco", "entrada"}
        self.assertTrue(chaves_esperadas.issubset(etapas.keys()))

        entrada = etapas["entrada"]
        self.assertEqual(entrada.shape, (28, 28))
        self.assertEqual(entrada.dtype, np.float32)
        self.assertGreaterEqual(float(entrada.min()), 0.0)
        self.assertLessEqual(float(entrada.max()), 1.0)
        self.assertTrue(np.isfinite(entrada).all())

    def test_preparar_digito_retorna_array_28x28(self):
        img = Image.new("RGB", (80, 80), color="white")
        draw = ImageDraw.Draw(img)
        draw.ellipse([(25, 25), (55, 55)], outline="black", width=8)

        saida = preparar_digito(img)
        self.assertEqual(saida.shape, (28, 28))
        self.assertEqual(saida.dtype, np.float32)


if __name__ == "__main__":
    unittest.main()
