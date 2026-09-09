# Mini-projeto — Módulo 02

Classificação de dígitos manuscritos com MNIST, comparação de modelos e avaliação de imagens próprias.

## Estado atual

Análise exploratória, divisão estratificada (60% treino, 10% validação, 10% calibração e 20% teste), normalização e auditoria de duplicatas concluídas. KNN, Random Forest e MLP foram comparados em quatro configurações por família; a CNN utiliza uma arquitetura fixa. Os diagramas da MLP e da CNN e as curvas de treinamento estão no notebook.

| Modelo selecionado | F1 ponderado na validação | Acurácia na validação |
|---|---:|---:|
| CNN | 0,982846 | 98,2857% |
| MLP | 0,977409 | 97,7429% |
| KNN | 0,969526 | 96,9571% |
| Random Forest | 0,967215 | 96,7286% |

A CNN foi escolhida pelo F1 de validação para calibração e imagens próprias. A MLP será a referência entre os três modelos principais. A temperatura da CNN foi ajustada nas 7.000 imagens de calibração: T=1,009045, com alteração mínima da log loss nesse conjunto e preservação das classes previstas. Avaliação no teste e desafios serão implementados nas próximas etapas.

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

Abra `projeto.ipynb` no VS Code e selecione o ambiente `.venv` como kernel. Reinicie o kernel e execute as células na ordem para aplicar a configuração inicial dos logs nativos do TensorFlow.

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

TensorFlow 2.21.0 e Keras 3.15.1 estão incluídos nas dependências. VisualKeras 0.2.0 gera os diagramas. MLP e CNN são salvas localmente em `artifacts/melhor_mlp.keras` e `artifacts/cnn.keras`; os modelos podem ser reproduzidos executando o notebook.
