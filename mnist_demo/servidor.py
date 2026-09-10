"""Demonstração local: python -m mnist_demo.servidor."""

from __future__ import annotations

import argparse
import base64
import binascii
import csv
from functools import partial
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from io import BytesIO
import json
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

from PIL import Image, UnidentifiedImageError

from .inferencia import PreditorCNN, RAIZ, png_base64

STATIC = Path(__file__).resolve().parent / "web"
LIMITE_BYTES = 8 * 1024 * 1024
LIMITE_PIXELS = 12_000_000


def decodificar_imagem(conteudo: dict) -> tuple[Image.Image, str]:
    if not isinstance(conteudo, dict):
        raise ValueError("Envie uma imagem válida.")
    fundo = conteudo.get("fundo", "claro")
    if fundo not in {"claro", "escuro"}:
        raise ValueError("Escolha fundo claro ou escuro.")
    dado = conteudo.get("imagem", "")
    if not isinstance(dado, str) or "," not in dado:
        raise ValueError("Envie uma imagem PNG, JPEG ou WebP.")
    cabecalho, payload = dado.split(",", 1)
    if cabecalho not in {"data:image/png;base64", "data:image/jpeg;base64", "data:image/webp;base64"}:
        raise ValueError("Envie uma imagem PNG, JPEG ou WebP.")
    try:
        dados = base64.b64decode(payload, validate=True)
        with Image.open(BytesIO(dados)) as imagem:
            if imagem.format not in {"PNG", "JPEG", "WEBP"}:
                raise ValueError("Formato de imagem não aceito.")
            if imagem.width * imagem.height > LIMITE_PIXELS:
                raise ValueError("Recorte ou reduza a imagem antes de enviá-la.")
            imagem.load()
            return imagem.copy(), fundo
    except (binascii.Error, UnidentifiedImageError, OSError, Image.DecompressionBombError) as exc:
        raise ValueError("Não foi possível ler a imagem. Escolha outro arquivo.") from exc


def obter_exemplo(identificador: str) -> dict:
    if identificador not in {"dev_0", "dev_1", "aval_7059_9"}:
        raise ValueError("Exemplo não encontrado.")
    pasta = RAIZ / "data/imagens_proprias"
    with (pasta / "manifesto.csv").open(encoding="utf-8", newline="") as arquivo:
        linha = next(r for r in csv.DictReader(arquivo) if r["id"] == identificador)
    with Image.open(pasta / linha["arquivo_foto"]) as foto:
        recorte = foto.convert("RGB").crop(tuple(int(linha[c]) for c in ["x0", "y0", "x1", "y1"]))
    # Sem thumbnail: os exemplos devem manter os pixels originais do experimento.
    buffer = BytesIO()
    recorte.save(buffer, format="PNG")
    imagem = "data:image/png;base64," + base64.b64encode(buffer.getvalue()).decode("ascii")
    return {"imagem": imagem, "rotulo": int(linha["rotulo"]), "id": identificador}


class Requisicao(BaseHTTPRequestHandler):
    def __init__(self, *args, preditor: PreditorCNN, **kwargs):
        self.preditor = preditor
        super().__init__(*args, **kwargs)

    def _responder(self, status: int, corpo: bytes, tipo: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", tipo)
        self.send_header("Content-Length", str(len(corpo)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header(
            "Content-Security-Policy",
            "default-src 'self'; img-src 'self' data: blob:; style-src 'self' 'unsafe-inline'; "
            "script-src 'self'; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'",
        )
        self.end_headers()
        try:
            self.wfile.write(corpo)
        except (BrokenPipeError, ConnectionResetError):
            pass  # O usuário pode limpar a imagem enquanto a inferência termina.

    def _json(self, status: int, dados: dict) -> None:
        self._responder(status, json.dumps(dados, ensure_ascii=False, allow_nan=False).encode(), "application/json; charset=utf-8")

    def do_GET(self) -> None:
        url = urlsplit(self.path)
        arquivos = {"/": ("index.html", "text/html; charset=utf-8"),
                    "/app.js": ("app.js", "text/javascript; charset=utf-8"),
                    "/style.css": ("style.css", "text/css; charset=utf-8")}
        if url.path in arquivos:
            nome, tipo = arquivos[url.path]
            self._responder(200, (STATIC / nome).read_bytes(), tipo)
        elif url.path == "/api/estado":
            self._json(200, {"modelo_disponivel": self.preditor.disponivel, "modelo": "CNN MNIST"})
        elif url.path == "/api/exemplo":
            try:
                self._json(200, obter_exemplo(parse_qs(url.query).get("id", [""])[0]))
            except (ValueError, StopIteration):
                self._json(404, {"erro": "Exemplo não encontrado."})
        else:
            self._json(404, {"erro": "Página não encontrada."})

    def do_POST(self) -> None:
        if self.path != "/api/predizer":
            self._json(404, {"erro": "Página não encontrada."})
            return
        origem = self.headers.get("Origin")
        porta = self.server.server_port
        if origem and origem not in {f"http://127.0.0.1:{porta}", f"http://localhost:{porta}"}:
            self._json(403, {"erro": "Abra a demonstração pelo endereço local informado."})
            return
        if self.headers.get("Content-Type", "").split(";")[0] != "application/json":
            self._json(415, {"erro": "Envie a imagem no formato esperado pela demonstração."})
            return
        try:
            tamanho = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            tamanho = 0
        if not 0 < tamanho <= LIMITE_BYTES:
            self._json(413, {"erro": "A imagem está vazia ou é muito grande. Use um recorte menor."})
            return
        try:
            conteudo = json.loads(self.rfile.read(tamanho))
            imagem, fundo = decodificar_imagem(conteudo)
            self._json(200, self.preditor.predizer(imagem, fundo))
        except FileNotFoundError as exc:
            self._json(503, {"erro": str(exc)})
        except (ValueError, TypeError, UnicodeDecodeError) as exc:
            self._json(400, {"erro": str(exc)})
        except Exception:
            self._json(500, {"erro": "Não foi possível executar a CNN. Confira o modelo e o ambiente Python."})


def main() -> None:
    parser = argparse.ArgumentParser(description="Demonstração local da CNN MNIST.")
    parser.add_argument("--porta", type=int, default=8765)
    parser.add_argument("--modelo-dir", type=Path, help="Pasta com a CNN e a calibração.")
    args = parser.parse_args()
    preditor = PreditorCNN(args.modelo_dir)
    servidor = ThreadingHTTPServer(("127.0.0.1", args.porta), partial(Requisicao, preditor=preditor))
    print(f"Demonstração disponível em http://127.0.0.1:{servidor.server_port}", flush=True)
    print("Encerre com Ctrl+C. As imagens enviadas não são salvas.", flush=True)
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        servidor.server_close()


if __name__ == "__main__":
    main()
