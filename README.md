# Mini-projeto — Módulo 02

Classificação de dígitos manuscritos com MNIST, comparação de modelos e avaliação de imagens próprias.

## Estado atual

Ambiente inicial e Fase 1 implementados: carregamento do MNIST, diagnóstico das matrizes, distribuição das classes, grade dos dez dígitos e comparação entre imagem e vetor de pixels. Divisão estratificada (60% treino, 10% validação, 10% calibração e 20% teste) e normalização para [0, 1] implementadas. KNN avaliado em quatro configurações na validação: selecionado k=3 com pesos por distância (F1 ponderado 0,969526). Os demais modelos e a avaliação no teste serão implementados nas próximas etapas.

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

A primeira execução baixa o [MNIST do OpenML](https://www.openml.org/d/554), `mnist_784`, versão 1, e requer internet. O cache fica em `data/cache/` e é reutilizado nas execuções seguintes. A análise inicial considera as 70.000 imagens, sem treinamento de modelos.

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
- `data/cache/`: dados baixados, ignorados pelo Git.
- `reports/figures/`: gráficos gerados pelo notebook.

As dependências das redes neurais e dos diagramas serão acrescentadas nas respectivas etapas.
