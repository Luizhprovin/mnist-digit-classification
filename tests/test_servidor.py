"""Testes unitários das funções auxiliares do servidor de demonstração."""

import base64
from io import BytesIO
import unittest
from PIL import Image

from mnist_demo.servidor import decodificar_imagem, obter_exemplo


class TestServidorHelpers(unittest.TestCase):
    def test_decodificar_imagem_valida(self):
        img = Image.new("RGB", (50, 50), color="white")
        buf = BytesIO()
        img.save(buf, format="PNG")
        b64 = "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode("ascii")

        imagem_decodificada, fundo = decodificar_imagem({"imagem": b64, "fundo": "claro"})
        self.assertEqual(imagem_decodificada.size, (50, 50))
        self.assertEqual(fundo, "claro")

    def test_decodificar_imagem_rejeita_payload_invalido(self):
        with self.assertRaises(ValueError):
            decodificar_imagem({"imagem": "invalido", "fundo": "claro"})

        with self.assertRaises(ValueError):
            decodificar_imagem({"imagem": "data:image/png;base64,123", "fundo": "invalido"})

    def test_obter_exemplo_valido(self):
        exemplo = obter_exemplo("dev_0")
        self.assertEqual(exemplo["id"], "dev_0")
        self.assertEqual(exemplo["rotulo"], 0)
        self.assertTrue(exemplo["imagem"].startswith("data:image/png;base64,"))

    def test_obter_exemplo_inexistente(self):
        with self.assertRaises(ValueError):
            obter_exemplo("inexistente_999")


if __name__ == "__main__":
    unittest.main()
