"""Confere que os números citados na documentação batem com os resultados gerados.

O notebook regenera `reports/tables/` a cada execução, mas as conclusões em
markdown e o README são escritos à mão. Sem esta verificação, uma reexecução que
mude qualquer resultado deixa os textos descrevendo números que não existem
mais. Como as tabelas são versionadas, o teste roda também na integração
contínua, sem precisar dos artefatos ignorados pelo Git.
"""

import csv
import json
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
TABELAS = RAIZ / "reports" / "tables"


def linhas(nome):
    with (TABELAS / nome).open(encoding="utf-8", newline="") as arquivo:
        return list(csv.DictReader(arquivo))


def por_modelo(nome, chave="Modelo"):
    return {linha[chave]: linha for linha in linhas(nome)}


def decimal(valor, casas):
    """Formate como a documentação escreve: vírgula decimal, sem separador de milhar."""
    return f"{float(valor):.{casas}f}".replace(".", ",")


def markdown_do_notebook():
    conteudo = json.loads((RAIZ / "projeto.ipynb").read_text(encoding="utf-8"))
    return "\n".join(
        "".join(celula["source"])
        for celula in conteudo["cells"]
        if celula["cell_type"] == "markdown"
    )


class TestConsistenciaDocumentacao(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.readme = (RAIZ / "README.md").read_text(encoding="utf-8")
        cls.notebook = markdown_do_notebook()
        cls.docs = "\n".join(
            caminho.read_text(encoding="utf-8") for caminho in sorted((RAIZ / "docs").glob("*.md"))
        )

    def afirmar_presente(self, texto, agulha, onde, descricao):
        # assertIn despejaria o documento inteiro na falha; a mensagem curta basta.
        self.assertTrue(
            agulha in texto,
            f"{onde} não cita {descricao} com o valor de reports/tables/: esperado {agulha!r}. "
            "Atualize o texto ou regenere as tabelas executando o notebook.",
        )

    def test_metricas_do_teste_no_readme(self):
        metricas = por_modelo("metricas_teste.csv")
        for modelo, linha in metricas.items():
            acuracia = f"{float(linha['Acurácia']) * 100:.4f}%"
            self.afirmar_presente(self.readme, acuracia, "README", f"a acurácia da {modelo}")
            self.afirmar_presente(
                self.readme, f"{float(linha['F1 ponderado']):.6f}", "README", f"o F1 da {modelo}"
            )

    def test_acertos_da_cnn(self):
        cnn = por_modelo("metricas_teste.csv")["CNN"]
        mlp = por_modelo("metricas_teste.csv")["MLP"]
        acertos = int(cnn["Acertos"])
        vantagem = acertos - int(mlp["Acertos"])
        formatado = f"{acertos:,}".replace(",", ".")
        self.afirmar_presente(self.readme, formatado, "README", "os acertos da CNN no teste")
        self.afirmar_presente(self.notebook, formatado, "O notebook", "os acertos da CNN no teste")
        self.afirmar_presente(
            self.readme, f"{vantagem} a mais", "README", "a vantagem da CNN sobre a MLP em acertos"
        )

    def test_bootstrap(self):
        linha = linhas("bootstrap_cnn_mlp.csv")[0]
        for campo, descricao in [
            ("Diferença de F1", "a diferença de F1"),
            ("Limite inferior (95%)", "o limite inferior do intervalo"),
            ("Limite superior (95%)", "o limite superior do intervalo"),
        ]:
            valor = decimal(linha[campo], 6)
            self.afirmar_presente(self.readme, valor, "README", descricao)
            self.afirmar_presente(self.notebook, valor, "O notebook", descricao)

    def test_calibracao_no_teste(self):
        versoes = por_modelo("calibracao_teste.csv", chave="CNN")
        temperatura = decimal(versoes["Calibrada"]["Temperatura"], 6)
        self.afirmar_presente(self.readme, temperatura, "README", "a temperatura")
        self.afirmar_presente(self.notebook, temperatura, "O notebook", "a temperatura")
        for versao in ("Original", "Calibrada"):
            for campo, casas, descricao in [
                ("Log loss", 8, "a log loss"),
                ("ECE (10 intervalos)", 8, "o ECE"),
            ]:
                valor = decimal(versoes[versao][campo], casas)
                self.afirmar_presente(self.readme, valor, "README", f"{descricao} ({versao.lower()})")

    def test_imagens_proprias(self):
        resumo = linhas("resumo_imagens_proprias.csv")
        total = sum(int(linha["Imagens"]) for linha in resumo)
        acertos = sum(int(linha["Acertos"]) for linha in resumo)
        self.assertEqual(total, 20, "O conjunto reservado deve ter vinte imagens.")
        self.afirmar_presente(
            self.readme, f"{acertos}/{total}", "README", "os acertos nas imagens reservadas"
        )
        for linha in resumo:
            self.afirmar_presente(
                self.readme, f"{linha['Acertos']}/{linha['Imagens']}", "README",
                f"os acertos da foto {linha['Foto']}",
            )

    def test_pior_digito_por_modelo(self):
        """O texto não pode afirmar um pior dígito comum se os modelos discordam."""
        tabela = linhas("f1_por_digito.csv")
        coluna_digito = list(tabela[0])[0]
        modelos = [c for c in tabela[0] if c in {"KNN", "Random Forest", "MLP", "CNN"}]
        piores = {
            modelo: min(tabela, key=lambda l: float(l[modelo]))[coluna_digito]
            for modelo in modelos
        }
        if len(set(piores.values())) > 1:
            for texto, onde in [(self.readme, "README"), (self.docs, "Os documentos em docs/")]:
                self.assertNotIn(
                    "menor F1 em todos os modelos", texto,
                    f"{onde} afirma um pior dígito comum, mas os modelos discordam: {piores}.",
                )
                self.assertNotIn(
                    "mais desafiadora em todos os 4 modelos", texto,
                    f"{onde} afirma um pior dígito comum, mas os modelos discordam: {piores}.",
                )


if __name__ == "__main__":
    unittest.main()
