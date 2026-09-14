# Classificação de dígitos manuscritos — MNIST

Mini-projeto avaliativo do Módulo 02 de Desenvolvimento de IA para Análise Preditiva. O projeto compara algoritmos clássicos e redes neurais para reconhecer dígitos de 0 a 9, examina erros e confiança das previsões e aplica o modelo selecionado a fotografias de dígitos próprios.

A implementação, as saídas executadas e as interpretações estão em [projeto.ipynb](projeto.ipynb). A CNN atingiu **98,9929% de acurácia nas 14.000 imagens de teste** e acertou **as 20 imagens próprias reservadas**. O resultado nas fotos é exploratório e não estima o desempenho para outras pessoas ou condições de captura.

![Arquitetura da CNN utilizada](reports/figures/arquitetura_cnn.png)

## Métodos e tecnologias

- Python 3.12, NumPy e pandas para preparação e análise dos dados.
- scikit-learn para MNIST via OpenML, divisão estratificada, KNN, Random Forest e métricas.
- TensorFlow 2.21.0 / Keras 3.15.1 para MLP e CNN.
- SciPy e Pillow para calibração e processamento das imagens próprias.
- Matplotlib e VisualKeras 0.2.0 para gráficos e diagramas das redes.
- Jupyter para organizar código, resultados e interpretação; Git e GitHub para versionamento.

As versões do ambiente estão registradas em [requirements.txt](requirements.txt).

## Protocolo do experimento

Usamos `mnist_784`, versão 1, com 70.000 imagens de 28 × 28 pixels e dez classes. A auditoria não encontrou imagens exatamente duplicadas; imagens apenas semelhantes não foram auditadas.

| Partição | Imagens | Função |
|---|---:|---|
| Treino — 60% | 42.000 | Ajustar os modelos |
| Validação — 10% | 7.000 | Selecionar configurações e acompanhar a parada das redes |
| Calibração — 10% | 7.000 | Ajustar a temperatura da CNN já selecionada |
| Teste — 20% | 14.000 | Avaliar os modelos e as probabilidades sem novos ajustes |

A divisão é estratificada, com semente 42, e própria deste projeto; não corresponde à divisão oficial do MNIST em 60.000/10.000. As partições são comuns aos modelos. Os pixels são convertidos para `float32` e divididos por 255. KNN, Random Forest e MLP recebem 784 atributos; a CNN recebe as mesmas imagens reorganizadas em 28 × 28 × 1.

### Configurações comparadas

| Família | Variações avaliadas | Configuração selecionada |
|---|---|---|
| KNN | 3 ou 5 vizinhos; pesos uniformes ou por distância | 3 vizinhos, pesos por distância |
| Random Forest | 100 ou 200 árvores; profundidade 20 ou sem limite | 200 árvores, sem limite explícito |
| MLP | Camadas (128, 64) ou (256, 128); L2 de 0,0001 ou 0,001 | (256, 128), L2 de 0,0001 |
| CNN | Uma arquitetura fixa, adicional às três famílias principais | Conv32 → Pool → Conv64 → Pool → Dense64 → saída de 10 classes |

São quatro combinações por família principal, doze no total. A CNN é uma comparação adicional sem busca equivalente de hiperparâmetros. As redes usam Adam, taxa de aprendizado 0,001, lotes de 64 e até 30 épocas, com parada antecipada pela acurácia de validação, paciência de cinco épocas e restauração dos melhores pesos. A regra é a mesma nas duas redes, para padronizar o limite de épocas e a regra de parada, embora épocas efetivas e custo continuem diferentes; acompanhamos a acurácia porque a perda de validação oscila neste problema e interrompia o ajuste antes da convergência.

O critério de seleção é o F1 ponderado na validação; os critérios de desempate estão documentados no notebook. Em cada execução, a escolha da CNN para calibração e imagens próprias utiliza a validação. A MLP foi a referência entre as três famílias principais no bootstrap pareado.

**Histórico da avaliação:** a regra de parada das redes foi revisada após uma primeira execução, e os resultados foram recalculados nas mesmas partições e fotografias. Treinamento e calibração não recebem o teste, mas seus resultados anteriores já eram conhecidos. Não apresentamos esse histórico como uma única avaliação cega; futuras decisões de ajuste exigem uma nova amostra reservada.

## Resultados no teste

| Modelo | Acurácia | Precisão ponderada | Recall ponderado | F1 ponderado | Ajuste (s) | Inferência (s) |
|---|---:|---:|---:|---:|---:|---:|
| CNN | 98.9929% | 0.989949 | 0.989929 | 0.989933 | 50.003 | 0.295 |
| MLP | 97.6571% | 0.976573 | 0.976571 | 0.976551 | 7.465 | 0.090 |
| KNN | 97.0286% | 0.970562 | 0.970286 | 0.970257 | 0.005 | 2.216 |
| Random Forest | 96.5714% | 0.965740 | 0.965714 | 0.965695 | 3.735 | 0.087 |

A CNN acertou 13.859 imagens, 187 a mais que a MLP. A maior confusão da CNN foi **4 → 9**, com 11 exemplos. O dígito 9 apresentou o menor F1 no KNN, na Random Forest e na MLP; na CNN o menor F1 ficou com o dígito 4 (0,9861), seguido de perto pelo 9 (0,9864).

O tempo de ajuste corresponde somente à configuração selecionada, e o de inferência ao lote de 14.000 imagens. São medidas de uma execução local, sem benchmark repetido; equipamento, paralelismo e custos das chamadas afetam os valores. A CNN apresentou maior tempo de ajuste. A Random Forest teve a menor duração de inferência nesta execução (0,0874 s), muito próxima da MLP (0,0897 s); a diferença isolada não estabelece vantagem consistente.

A diferença de F1 CNN − MLP foi **0,013382**, com intervalo percentil de 95% **[0,011304; 0,015602]**, obtido por 1.000 reamostragens pareadas. O intervalo é condicionado aos modelos ajustados e à hipótese de exemplos independentes; não inclui a variabilidade de novos treinamentos ou seleções.

![Matrizes de confusão dos quatro modelos](reports/figures/matrizes_confusao_teste.png)

### Calibração das probabilidades

A temperatura foi ajustada nas 7.000 imagens de calibração: **T = 1,512363**. A transformação preservou as classes previstas. No teste, a log loss passou de 0,03756771 para 0,03271348, e o ECE de dez intervalos passou de 0,00489486 para 0,00099256. Ambas as medidas melhoraram: a log loss caiu cerca de 12,9% e o ECE ficou aproximadamente cinco vezes menor. Uma temperatura acima de 1 aproxima as probabilidades entre si, o que indica que a CNN atribuía às classes escolhidas probabilidades mais altas do que a frequência de acerto justificaria. A melhora obtida no conjunto usado para ajustar a temperatura se reproduziu no teste, em dados que não participaram desse ajuste.

### Classes ausentes do treino — desafios A e B

Uma nova Random Forest com 200 árvores e profundidade máxima 20 foi ajustada sem os dígitos 4 e 7, usando 33.531 imagens. Nas 2.824 imagens de teste dessas classes, a acurácia foi zero por construção: o classificador só emite as oito classes aprendidas.

A maioria dos exemplos foi atribuída à classe 9. A confiança média ficou abaixo de 60%, mas houve **106 previsões incorretas com confiança de pelo menos 90%** — 3,75% das 2.824 imagens, a cauda de **falsa certeza** (*overconfidence*) discutida na seção 7 do notebook. Alta confiança entre classes conhecidas não garante reconhecer uma classe ausente. O notebook explica essa limitação e a diferença entre classificação e um mecanismo de rejeição, que não foi implementado neste experimento.

### Imagens próprias — desafio C

Três fotografias fornecem trinta dígitos rotulados. As cópias PNG orientadas, as coordenadas de recorte e os parâmetros do processamento estão em [data/imagens_proprias](data/imagens_proprias). As cópias incluídas são suficientes para executar o notebook; os arquivos HEIC originais não são necessários.

O processamento converte para cinza, estima o fundo, destaca o traço escuro como intensidade clara sobre fundo preto, remove componentes pequenos, expande o traço, redimensiona proporcionalmente e centraliza pelo centro de massa em 28 × 28. A saída já está normalizada em [0, 1].

| Fotografia de origem | Finalidade | Acertos |
|---|---|---:|
| IMG_7057.heic | Desenvolvimento do processamento | 9/10 |
| IMG_7058.heic | Avaliação reservada | 10/10 |
| IMG_7059.heic | Avaliação reservada | 10/10 |

As vinte imagens reservadas foram avaliadas com o processamento fixado, sem novos ajustes nos pesos ou na temperatura: **20/20 acertos (100%)**. O acerto integral não deve ser lido como ausência de erro: são vinte exemplos de uma pessoa e duas fotografias, e a confiança variou bastante entre eles — o dígito 9 da segunda foto foi reconhecido com **69,43%** e o dígito 2 com 74,27%. Os dez exemplos de desenvolvimento são apresentados separadamente, com 9/10 acertos; o erro remanescente é um **1 previsto como 2, com confiança de 75,36%**.

A calibração feita no MNIST não garante probabilidades adequadas às fotografias próprias. A luminosidade pode alterar contraste e representação dos traços, mas o experimento não isolou esse fator; não é possível atribuir o erro observado à iluminação.

As galerias apresentam cada imagem ao lado das dez probabilidades: [desenvolvimento](reports/figures/probabilidades_IMG_7057.png), [primeira foto de avaliação](reports/figures/probabilidades_IMG_7058.png) e [segunda foto de avaliação](reports/figures/probabilidades_IMG_7059.png).

A [inspeção do processamento em cinco etapas](reports/figures/etapas_processamento.png) mostra o caminho do recorte original até a entrada efetivamente utilizada pela CNN. A função compartilhada está em `mnist_demo/preprocessamento.py`.

## Instalação

Clone o repositório e entre na pasta:

```bash
git clone https://github.com/Luizhprovin/mnist-digit-classification.git
cd mnist-digit-classification
```

Em macOS ou Linux, com Python 3.12 instalado:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Em Windows, use `py -3.12 -m venv .venv` e ative o ambiente com `.venv\Scripts\Activate.ps1` no PowerShell antes de instalar as dependências. O ambiente foi executado e verificado em macOS com Apple Silicon; não houve validação independente em Windows ou Linux.

## Execução

Abra [projeto.ipynb](projeto.ipynb) no VS Code com as extensões Python e Jupyter, selecione `.venv` como kernel e use **Reiniciar Kernel e Executar Tudo**. Execute as células na ordem. A configuração inicial dos logs nativos do TensorFlow deve ser aplicada antes da importação da biblioteca.

Também é possível executar na raiz do projeto pelo terminal:

```bash
python -m jupyter nbconvert --execute --to notebook --inplace projeto.ipynb --ExecutePreprocessor.timeout=600
```

A primeira execução baixa o [MNIST do OpenML](https://www.openml.org/d/554) e requer internet. O cache fica em `data/cache/` e é reutilizado nas execuções seguintes. O notebook treina os modelos e atualiza as tabelas, figuras e saídas. O tempo total varia com o equipamento. As sementes e versões auxiliam a reprodução, mas pequenas diferenças numéricas podem ocorrer entre plataformas.

### Demonstração interativa local

**Pré-requisito:** a demonstração carrega `artifacts/cnn.keras` e `artifacts/calibracao_cnn.json`, gerados pelo notebook e não versionados (`artifacts/` está no `.gitignore`). Em um clone novo, execute [projeto.ipynb](projeto.ipynb) por completo antes de iniciar o servidor. Sem esses arquivos a interface abre, sinaliza o modelo como indisponível e recusa as predições com a mensagem correspondente.

Para executar a demonstração web com desenho interativo em canvas, envio de fotografias e consulta às probabilidades calibradas da CNN:

```bash
python -m mnist_demo.servidor
```

Abra `http://127.0.0.1:8765` no navegador. A aplicação utiliza apenas a biblioteca padrão do Python (`http.server`) com HTML5/CSS/JavaScript puros no frontend, sem dependências adicionais de frameworks web. Ela desacopla a inferência do treinamento: carrega a CNN ajustada (`artifacts/cnn.keras`) e sua calibração por temperatura sem reexecutar o notebook. A tela de desenho inclui opções de espessura de traço (18px, 24px e 30px), com padrão em 24px. A espessura facilita experimentar desenhos, mas não garante equivalência com a escrita do MNIST.

### Testes automatizados e CI

Para rodar a suíte de testes unitários localmente:

```bash
python -m unittest discover -s tests -v
```

O GitHub Actions verifica a sintaxe Python, valida o formato do notebook e executa os testes em pushes e pull requests. Os testes de consistência comparam afirmações selecionadas do README, notebook e guia com os CSVs; não substituem revisão de todos os textos. O CI não retreina os modelos e pula a inferência completa quando `artifacts/` está ausente. A inferência com a CNN deve ser verificada também no ambiente local com os artefatos gerados.

## Organização

```text
projeto.ipynb                 # Código, saídas e interpretação das fases
README.md                    # Métodos, resultados e instruções
requirements.txt             # Dependências com versões
.python-version              # Python 3.12
.vscode/                     # Seleção do ambiente no editor
.github/workflows/           # Fluxos de automação e CI do GitHub Actions
mnist_demo/                  # Módulos de pré-processamento, inferência desacoplada e servidor
mnist_demo/web/              # Interface web (HTML5 Canvas, CSS e JavaScript puros)
tests/                       # Testes do pipeline, manifesto, servidor e consistência dos números
data/imagens_proprias/       # Fotos PNG, manifesto e parâmetros
reports/figures/              # Matrizes, curvas, diagramas e galerias
reports/tables/               # Resultados em CSV
docs/ENTREGA.md               # Correspondência com os requisitos e pendências externas
```

`data/cache/`, `.venv/` e `artifacts/` são ignorados pelo Git. MLP e CNN são salvas localmente em `artifacts/melhor_mlp.keras` e `artifacts/cnn.keras`; os modelos e demais arquivos desse diretório são recriados pelo notebook.

## Versionamento

As etapas foram registradas em commits próprios, com branches preservadas. As primeiras integrações foram locais por avanço direto de `develop` (fast-forward); o fechamento local usa commits de merge. O repositório público mantém as branches de cada etapa. A versão de entrega é integrada de `develop` para `main` por pull request. O histórico não atribui pull requests às etapas integradas apenas localmente.

| Branch | Objetivo |
|---|---|
| `feature/estrutura` | Ambiente e notebook inicial |
| `feature/eda` | Carregamento e análise exploratória |
| `feature/preprocessamento` | Divisão e normalização |
| `feature/knn` | Ajuste e comparação do KNN |
| `feature/random-forest` | Ajuste e comparação da Random Forest |
| `feature/mlp` | MLP e auditoria de duplicatas |
| `feature/cnn` | CNN e diagramas das redes |
| `feature/calibracao` | Temperatura da CNN e correção de avisos |
| `feature/avaliacao` | Teste, matrizes, confiabilidade e bootstrap |
| `feature/classes-ocultadas` | Desafios A e B |
| `feature/imagens-proprias` | Processamento e dez imagens de desenvolvimento |
| `feature/avaliacao-proprias` | Vinte imagens reservadas e probabilidades dos trinta dígitos |
| `feature/documentacao` | Revisão, conclusão geral e documentação de entrega |
| `feature/publicacao` | Nome público e referências do repositório |
| `feature/etapas-processamento` | Visualização das etapas e processamento compartilhado |
| `feature/demonstracao` | Interface web interativa e inferência desacoplada da CNN |
| `feature/ci` | Testes automatizados e integração contínua no GitHub Actions |
| `feature/ajuste-traco` | Ajuste na espessura do traço e controle interativo de pincel |
| `feature/ajuste-ci` | Testes de inferência condicionados aos artefatos e CI sem TensorFlow |
| `feature/falsa-certeza` | Conceito de falsa certeza nomeado na análise das classes ocultadas |
| `feature/readme-demo` | Pré-requisito da demonstração e alinhamento do termo no README |
| `feature/cnn-convergencia` | Parada antecipada por acurácia de validação e reexecução completa |

## Limitações e melhorias possíveis

Os resultados usam uma divisão e uma semente; a busca de hiperparâmetros é pequena. As fotos próprias representam uma pessoa e poucas condições de captura. A confiança não funciona como garantia de acerto nem como detector de classes desconhecidas.

Desenhos com mouse ou trackpad podem diferir das fotografias e do MNIST em espessura, continuidade e formato dos traços. Foram observadas confusões no uso exploratório do canvas, incluindo desenhos do dígito 8. Não houve experimento controlado nem inspeção das ativações que identificasse sua causa. O seletor de pincel oferece outra forma de desenhar, mas seu ganho de acurácia não foi medido.

Melhorias futuras incluem avaliar outras pessoas, controlar a iluminação ao fotografar os mesmos dígitos, experimentar aumento de dados (*data augmentation* com transformações elásticas e pequenas rotações) para aproximar o treino da caligrafia em telas digitais, adicionar operadores morfológicos de fechamento (*closing*) para conectar laços imperfeitos e avaliar mecanismos explícitos de rejeição para entradas desconhecidas. Novos ajustes exigiriam novos dados de desenvolvimento e uma nova amostra reservada.

## Referências

- [MNIST no OpenML](https://www.openml.org/d/554).
- [TensorFlow — Conv2D](https://www.tensorflow.org/api_docs/python/tf/keras/layers/Conv2D) e [EarlyStopping](https://www.tensorflow.org/api_docs/python/tf/keras/callbacks/EarlyStopping).
- [VisualKeras](https://github.com/paulgavrikov/visualkeras).
- [Guo et al. (2017) — On Calibration of Modern Neural Networks](https://proceedings.mlr.press/v70/guo17a.html).
