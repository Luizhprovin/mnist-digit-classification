"""Inferência da CNN ajustada no notebook, sem treinamento ou acesso ao MNIST."""

from __future__ import annotations

import base64
from io import BytesIO
import json
import os
from pathlib import Path
from threading import Lock

import numpy as np
from PIL import Image, ImageOps
from scipy.special import softmax

from .preprocessamento import etapas_digito

RAIZ = Path(__file__).resolve().parents[1]


def imagem_rgb(imagem: Image.Image, fundo: str = "claro") -> Image.Image:
    """Aplique orientação EXIF e componha transparência sobre o fundo escolhido."""
    if fundo not in {"claro", "escuro"}:
        raise ValueError("Escolha fundo claro ou escuro.")
    imagem = ImageOps.exif_transpose(imagem)
    if "A" in imagem.getbands() or "transparency" in imagem.info:
        rgba = imagem.convert("RGBA")
        base = Image.new("RGBA", rgba.size, "white" if fundo == "claro" else "black")
        imagem = Image.alpha_composite(base, rgba)
    return imagem.convert("RGB")


def png_base64(imagem: Image.Image | np.ndarray) -> str:
    """Crie uma visualização PNG; a inferência usa o array float32 original."""
    if isinstance(imagem, np.ndarray):
        imagem = Image.fromarray(np.rint(np.clip(imagem, 0, 1) * 255).astype(np.uint8))
    copia = imagem.copy()
    if max(copia.size) > 320:
        copia.thumbnail((320, 320), Image.Resampling.LANCZOS)
    buffer = BytesIO()
    copia.save(buffer, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buffer.getvalue()).decode("ascii")


class PreditorCNN:
    """Carregue uma vez a CNN e sua temperatura; reutilize-as nas consultas."""

    def __init__(self, diretorio: Path | str | None = None):
        self.diretorio = Path(diretorio) if diretorio is not None else RAIZ / "artifacts"
        self.caminho_modelo = self.diretorio / "cnn.keras"
        self.caminho_calibracao = self.diretorio / "calibracao_cnn.json"
        self.caminho_processamento = RAIZ / "data/imagens_proprias/preprocessamento.json"
        self._lock = Lock()
        self._extrator = None

    @property
    def disponivel(self) -> bool:
        return all(p.is_file() for p in [
            self.caminho_modelo, self.caminho_calibracao, self.caminho_processamento,
        ])

    def _carregar(self) -> None:
        if self._extrator is not None:
            return
        if not self.disponivel:
            raise FileNotFoundError(
                "Modelo indisponível. Execute o notebook completo para gerar a CNN e a calibração."
            )
        calibracao = json.loads(self.caminho_calibracao.read_text(encoding="utf-8"))
        processamento = json.loads(self.caminho_processamento.read_text(encoding="utf-8"))
        temperatura = float(calibracao["temperatura"])
        if (
            calibracao.get("metodo") != "temperature_scaling"
            or not np.isfinite(temperatura) or temperatura <= 0
            or processamento.get("versao") != "1.0"
        ):
            raise ValueError("A configuração do modelo não corresponde ao experimento.")
        os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")
        import tensorflow as tf

        modelo = tf.keras.models.load_model(self.caminho_modelo, compile=False)
        if tuple(modelo.input_shape[1:]) != (28, 28, 1) or modelo.output_shape[-1] != 10:
            raise ValueError("A CNN deve receber 28 × 28 × 1 e produzir dez classes.")
        pesos, vies = modelo.layers[-1].get_weights()
        self.temperatura = temperatura
        self.parametros = processamento["parametros"]
        self._pesos = pesos.astype(np.float64)
        self._vies = vies.astype(np.float64)
        self._extrator = tf.keras.Model(inputs=modelo.inputs, outputs=modelo.layers[-1].input)

    def probabilidades(self, entradas: np.ndarray) -> np.ndarray:
        """Calcule softmax(logits / T), na ordem fixa dos dígitos de 0 a 9."""
        entradas = np.asarray(entradas, dtype=np.float32)
        if (
            entradas.ndim != 4 or entradas.shape[1:] != (28, 28, 1)
            or len(entradas) == 0 or not np.isfinite(entradas).all()
            or entradas.min() < 0 or entradas.max() > 1
        ):
            raise ValueError("A entrada deve ter formato (n, 28, 28, 1) e valores em [0, 1].")
        with self._lock:
            self._carregar()
            caracteristicas = self._extrator.predict(entradas, batch_size=256, verbose=0)
            logits = caracteristicas.astype(np.float64) @ self._pesos + self._vies
            return softmax(logits / self.temperatura, axis=1)

    def predizer(self, imagem: Image.Image, fundo: str = "claro") -> dict:
        """Retorne uma previsão e as etapas da mesma entrada utilizada pela CNN."""
        original = imagem_rgb(imagem, fundo)
        base = ImageOps.invert(original) if fundo == "escuro" else original
        # Configuração leve: recusas de entrada não precisam carregar o TensorFlow.
        if not self.disponivel:
            raise FileNotFoundError(
                "Modelo indisponível. Execute o notebook completo para gerar a CNN e a calibração."
            )
        parametros = json.loads(self.caminho_processamento.read_text(encoding="utf-8"))["parametros"]
        etapas = etapas_digito(base, **parametros)
        probabilidades = self.probabilidades(etapas["entrada"][None, ..., None])[0]
        if not np.isfinite(probabilidades).all() or not np.isclose(probabilidades.sum(), 1):
            raise RuntimeError("O modelo não produziu probabilidades válidas.")
        previsto = int(probabilidades.argmax())
        return {
            "previsto": previsto,
            "confianca": float(probabilidades[previsto]),
            "probabilidades": [float(p) for p in probabilidades],
            "temperatura": self.temperatura,
            "fundo": fundo,
            "etapas": {
                "original": png_base64(original),
                **{nome: png_base64(etapas[nome]) for nome in ["cinza", "contraste", "traco", "entrada"]},
            },
        }
