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

A CNN foi escolhida pelo F1 de validação para calibração e imagens próprias. A MLP foi a referência entre os três modelos principais no bootstrap pareado. A temperatura da CNN foi ajustada nas 7.000 imagens de calibração: T=1,009045, com alteração mínima da log loss nesse conjunto e preservação das classes previstas. A avaliação no teste, o experimento com classes ocultadas e a avaliação das imagens próprias foram concluídos.

## Resultados no teste

| Modelo | F1 ponderado | Acurácia | Acertos / 14.000 |
|---|---:|---:|---:|
| CNN | 0,983553 | 98,3571% | 13.770 |
| MLP | 0,976551 | 97,6571% | 13.672 |
| KNN | 0,970257 | 97,0286% | 13.584 |
| Random Forest | 0,965695 | 96,5714% | 13.520 |

A diferença de F1 entre CNN e MLP foi 0,007002, com intervalo de 95% [0,004786; 0,009285] pelo bootstrap pareado de 1.000 reamostragens. O intervalo é condicionado aos modelos ajustados e não incorpora a variabilidade de treinamento.

A calibração não trouxe benefício nas medidas observadas no teste: a log loss passou de 0,05217654 para 0,05218850. As classes previstas foram preservadas. Matrizes de confusão, resultados por dígito, confiabilidade e interpretação estão no notebook; tabelas exportadas em `reports/tables/`.

## Classes ausentes do treino

Uma nova Random Forest foi ajustada sem os dígitos 4 e 7, com 33.531 imagens. Nas 2.824 imagens de teste dessas classes, a acurácia foi zero por construção. O modelo atribuiu a maioria dos exemplos à classe 9 e produziu 106 previsões erradas com confiança de pelo menos 90%. Isso demonstra que alta confiança entre classes conhecidas não garante reconhecer uma classe ausente do treino. A matriz e as probabilidades estão documentadas no notebook.

## Imagens próprias

A primeira fotografia fornece dez recortes para desenvolver o processamento: correção de iluminação, extração e expansão do traço, redimensionamento proporcional e centralização em 28 × 28. A CNN acertou 9/10 nesses exemplos; o dígito 1 foi previsto como 3. Esses resultados pertencem ao desenvolvimento do processamento.

As vinte imagens das outras duas fotografias foram avaliadas com os parâmetros fixados, sem novos ajustes nos pesos da CNN ou na temperatura:

| Fotografia reservada | Acertos | Acurácia |
|---|---:|---:|
| IMG_7058.heic | 10/10 | 100% |
| IMG_7059.heic | 9/10 | 90% |
| Total reservado | 19/20 | 95% |

O único erro na avaliação foi um 9 previsto como 3, com confiança de 98,53%. A calibração feita no MNIST não garante probabilidades adequadas às fotografias próprias. O resultado de 95% descreve apenas esses vinte exemplos de uma mesma pessoa e duas fotografias; não representa uma estimativa precisa para outros estilos de escrita ou condições de captura.

As três galerias do notebook apresentam todos os trinta dígitos com suas dez probabilidades. Os resultados numéricos estão em `reports/tables/imagens_proprias_avaliacao.csv` e `reports/tables/probabilidades_imagens_proprias.csv`. As cópias orientadas das fotos, as coordenadas dos recortes, os rótulos e os parâmetros fixados estão em `data/imagens_proprias/`.

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

## Escopo implementado

Análise exploratória, divisão estratificada, normalização, KNN, Random Forest, MLP em Keras, CNN, comparação multiclasse, bootstrap pareado, calibração e diagramas das redes. Os desafios incluem treinamento sem duas classes e inferência sobre 30 dígitos manuscritos próprios.

## Organização

- `projeto.ipynb`: implementação e resultados.
- `requirements.txt`: dependências do ambiente atual.
- `.python-version`: versão de Python adotada.
- `.vscode/`: configuração local do editor.
- `data/cache/`: dados baixados, ignorados pelo Git.
- `reports/figures/`: gráficos gerados pelo notebook.
- `reports/tables/`: resultados exportados em CSV.
- `data/imagens_proprias/`: fotografias de trabalho, manifesto de recortes e parâmetros do processamento.

TensorFlow 2.21.0 e Keras 3.15.1 estão incluídos nas dependências. VisualKeras 0.2.0 gera os diagramas. MLP e CNN são salvas localmente em `artifacts/melhor_mlp.keras` e `artifacts/cnn.keras`; os modelos podem ser reproduzidos executando o notebook.
