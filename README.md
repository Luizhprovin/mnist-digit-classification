# Mini-projeto — Módulo 02

Classificação de dígitos manuscritos com MNIST, comparação de modelos e avaliação de imagens próprias.

## Estado atual

Ambiente inicial e notebook de verificação preparados. As etapas de dados, treinamento e avaliação serão implementadas progressivamente.

## Ambiente

- Python 3.12
- Dependências com versões registradas em `requirements.txt`
- VS Code com as extensões Python e Jupyter

## Instalação

Execute na raiz do projeto, em macOS ou Linux:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

## Execução

Abra `projeto.ipynb` no VS Code e selecione o ambiente `.venv` como kernel. Execute as células na ordem.

Para executar e atualizar as saídas pelo terminal:

```bash
python -m jupyter nbconvert --execute --to notebook --inplace projeto.ipynb
```

## Escopo previsto

Análise exploratória, divisão estratificada, normalização, KNN, Random Forest, MLP em Keras, CNN, comparação multiclasse, bootstrap pareado, calibração e diagramas das redes. Os desafios incluem treinamento sem duas classes e inferência sobre 30 dígitos manuscritos próprios.

## Organização

- `projeto.ipynb`: implementação e resultados.
- `requirements.txt`: dependências do ambiente atual.
- `.python-version`: versão de Python adotada.
- `.vscode/`: configuração local do editor.

As dependências das redes neurais e dos diagramas serão acrescentadas nas respectivas etapas.
