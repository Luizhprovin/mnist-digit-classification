# Mini-projeto — Módulo 02

Classificação de dígitos manuscritos com MNIST, comparação de modelos e avaliação de imagens próprias.

## Estado atual

Ambiente inicial e Fase 1 implementados: carregamento do MNIST, diagnóstico das matrizes, distribuição das classes, grade dos dez dígitos e comparação entre imagem e vetor de pixels. Divisão estratificada (60% treino, 10% validação, 10% calibração e 20% teste) e normalização para [0, 1] implementadas. KNN avaliado em quatro configurações na validação: selecionado k=3 com pesos por distância (F1 ponderado 0,969526). Random Forest também avaliada em quatro configurações: selecionadas 200 árvores sem limite explícito de profundidade (F1 ponderado 0,967215). MLP em Keras avaliada em quatro configurações: selecionadas camadas (256, 128) com L2=0,0001 (F1 ponderado 0,977409). Auditoria adicional confirmou ausência de imagens exatamente duplicadas. CNN e avaliação no teste serão implementadas nas próximas etapas.

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

TensorFlow 2.21.0 e Keras 3.15.1 estão incluídos nas dependências. A MLP selecionada é salva localmente em `artifacts/melhor_mlp.keras`; os modelos podem ser reproduzidos executando o notebook. As dependências dos diagramas serão acrescentadas na respectiva etapa.
