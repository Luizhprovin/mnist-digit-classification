# Guia Técnico Completo do Projeto MNIST: De Cabo a Rabo

Este documento detalha o raciocínio científico, a fundamentação teórica e as decisões de implementação por trás de cada bloco de código do [`projeto.ipynb`](file:///Users/luizhenriqueprovin/Documents/ChatGPT/New%20project/miniprojeto_mod02/projeto.ipynb) e do módulo [`mnist_demo`](file:///Users/luizhenriqueprovin/Documents/ChatGPT/New%20project/miniprojeto_mod02/mnist_demo/).

---

## 1. Configuração do Ambiente e Reprodutibilidade

### O que o código faz:
- Define variáveis de ambiente do TensorFlow (`TF_CPP_MIN_LOG_LEVEL = '2'`) antes de importar a biblioteca para silenciar avisos de compilação de instruções de CPU (AVX2/FMA).
- Fixa sementes de números pseudoaleatórios no NumPy (`np.random.seed(42)`), Python (`random.seed(42)`) e TensorFlow (`tf.keras.utils.set_random_seed(42)`).
- Habilita determinismo nos algoritmos de álgebra linear do Keras (`tf.config.experimental.enable_op_determinism()`).

### Por que isso é feito?
- **Reprodutibilidade científica:** Redes neurais inicializam pesos com distribuições aleatórias e treinam com mini-lotes sorteados via estocástica. Sem sementes fixadas, cada execução geraria acurácias ligeiramente diferentes.
- **Auditoria de avaliadores:** Garante que qualquer cientista de dados ou avaliador que execute o notebook obtenha os mesmos 98,36% de acurácia na CNN.

---

## 2. Fase 1: Carregamento e Análise Exploratória (EDA)

### 2.1. Importação via OpenML e Cache Local
- **Código:** `fetch_openml('mnist_784', version=1, as_frame=False, data_home='data/cache')`.
- **Por que `as_frame=False`?** Imagens são tensores numéricos; representá-las como matrizes densas NumPy (`np.ndarray`) consome até $5\times$ menos memória RAM e executa cálculos vetoriais em C/Fortran muito mais rápidos que `pandas.DataFrame`.
- **Por que `data_home='data/cache'`?** O edital proíbe caminhos absolutos locais (`C:\Usuarios\...`) e exige reprodutibilidade sem forçar downloads de 50MB a cada teste. O cache local resolve isso.

### 2.2. Dimensionalidade e Representação Vetorial
- **O que representa:** Imagens bidimensionais de $28 \times 28$ pixels desdobradas em um vetor unidimensional de **784 características (*features*)**.
- **Escala de Intensidade (0 a 255):** Representa profundidade de cor de 8 bits ($2^8 = 256$ valores). No MNIST original, $0$ representa o fundo (preto absoluto) e $255$ o traço do dígito em brilho máximo (branco puro).
- **Equilíbrio de Classes:** O código calcula a frequência dos dígitos de 0 a 9. Cada classe possui aproximadamente 7.000 amostras ($\approx 10\%$), provando que a base é perfeitamente balanceada e que a acurácia global é uma métrica válida (não há classe majoritária distorcendo o aprendizado).
- **Grade $2 \times 5$ com Matplotlib:** Exibe visualmente um exemplo canônico de cada dígito para inspeção humana.

---

## 3. Fase 2: Pipeline de Pré-processamento e Divisão dos Dados

### 3.1. O Particionamento Quádruplo Estratificado
Enquanto projetos convencionais dividem apenas em treino e teste (ou treino/val/teste), este projeto utiliza uma partição estratégica em **4 conjuntos independentes**:

1. **Treino (60% — 42.000 imagens):** Ajuste dos pesos dos modelos e cálculo de gradientes.
2. **Validação (10% — 7.000 imagens):** Ajuste fino de hiperparâmetros (seleção da melhor arquitetura da MLP, número de vizinhos do KNN, profundidade da Random Forest) e gatilho de *Early Stopping* das redes.
3. **Calibração (10% — 7.000 imagens):** Reservado exclusivamente para ajustar o hiperparâmetro de temperatura ($T$) da CNN pós-treinamento, sem usar dados de teste.
4. **Teste Cego (20% — 14.000 imagens):** Conjunto estritamente intocado, utilizado apenas na medição final de desempenho.

- **Por que `stratify=y`?** Garante que todas as partições mantenham exatamente a proporção idêntica de $10\%$ para cada um dos 10 dígitos, prevenindo viés amostral.

### 3.2. Normalização e Escalonamento dos Pixels
- **Código:** `X = X.astype(np.float32) / 255.0`.
- **Por que dividir por 255?**
  1. **Convergência de Redes Neurais:** Os pesos são inicializados próximos de 0. Entradas brutas entre 0 e 255 gerariam gradientes gigantescos logo na primeira época, causando saturação rápida de funções de ativação e instabilidade numérica (*exploding gradients*).
  2. **Modelos Baseados em Distância (KNN):** O cálculo da distância euclidiana $d(x, z) = \sqrt{\sum (x_i - z_i)^2}$ com valores em $[0, 255]$ geraria magnitudes astronômicas, penalizando qualquer pequena variação de ruído. Na escala $[0.0, 1.0]$, as distâncias tornam-se numericamente estáveis.

### 3.3. Auditoria de Imagens Duplicadas
- O notebook realiza uma busca vetorial hash/exata no dataset para averiguar vazamento de dados (*data leakage*) entre treino e teste. Nenhuma imagem exatamente idêntica foi compartilhada entre as partições.

---

## 4. Fase 3: Modelagem e Ajuste de Hiperparâmetros

O edital exige a comparação de 3 modelos distintos com ao menos 2 hiperparâmetros ajustados cada. O projeto foi além e implementou 4 famílias:

### 4.1. K-Nearest Neighbors (KNN)
- **Hiperparâmetros ajustados:**
  1. `n_neighbors`: $k \in \{3, 5\}$.
  2. `weights`: `'uniform'` (voto simples da maioria) vs `'distance'` (ponderação pelo inverso da distância euclidiana).
- **Por que os pesos por distância venceram?** No reconhecimento de escrita, vizinhos mais próximos no espaço vetorial possuem traços muito mais verossímeis; ponderar pela proximidade impede que vizinhos marginais na borda da hiperesfera distorçam o voto.
- **Resultado:** $k=3$, pesos por distância alcançou $97,03\%$ de acurácia no teste. Custo de inferência: 2,7 segundos (lento para 14k imagens, pois o KNN precisa calcular a distância para todos os 42k pontos de treino a cada predição).

### 4.2. Random Forest
- **Hiperparâmetros ajustados:**
  1. `n_estimators`: 100 vs 200 árvores de decisão.
  2. `max_depth`: limitada a 20 vs sem limite explícito (*None*).
- **Por que árvores profundas venceram?** Cada pixel do MNIST atua como uma feature isolada. Relações espaciais complexas (ex: "se o pixel 350 for claro E o 400 for escuro") exigem árvores com profundidade suficiente para criar regras hierárquicas compostas.
- **Resultado:** 200 árvores, profundidade livre obteve $96,57\%$ de acurácia.

### 4.3. Multi-Layer Perceptron (MLP) em Keras
- **Hiperparâmetros ajustados:**
  1. Arquitetura das camadas ocultas: $(128, 64)$ neurônios vs $(256, 128)$ neurônios.
  2. Regularização L2 (*Ridge Penalty*): $\lambda = 10^{-4}$ vs $\lambda = 10^{-3}$.
- **Decisões arquiteturais:**
  - Ativação `relu` nas camadas ocultas (evita *vanishing gradient*).
  - Regularização de peso L2 para penalizar pesos gigantescos e mitigar memorização/overfitting.
  - *Early Stopping* monitorando `val_loss` com paciência de 5 épocas e `restore_best_weights=True`.
- **Resultado:** Arquitetura $(256, 128)$ com $\lambda = 10^{-4}$ venceu na validação, alcançando $97,66\%$ no teste.

### 4.4. Convolutional Neural Network (CNN) — Modelo Campeão
- **Por que foi adicionada?** Algoritmos tabulares (KNN, RF, MLP) tratam os 784 pixels de forma desacoplada: se você embaralhar a ordem das 784 colunas, o resultado matemático deles é idêntico! Já a CNN enxerga a imagem como uma matriz $28 \times 28 \times 1$, preservando a **correlação espacial local** de traços e curvas contíguas.
- **Arquitetura implementada:**
  1. `Conv2D(32, (3, 3), activation='relu')`: Extrai 32 mapas de características simples (bordas verticais, horizontais e curvas).
  2. `MaxPooling2D((2, 2))`: Reduz a resolução pela metade, conferindo invariância a pequenas translações.
  3. `Conv2D(64, (3, 3), activation='relu')`: Combina as bordas simples em padrões compostos (laços, junções, cruzamentos).
  4. `MaxPooling2D((2, 2))`: Nova compressão espacial.
  5. `Flatten()` + `Dense(64, activation='relu')`: Vetorização dos mapas convolucionais e combinação semântica.
  6. `Dropout(0.3)`: Zera aleatoriamente 30% das conexões durante o treino para forçar neurônios a aprenderem representações redundantes e robustas.
  7. `Dense(10, activation='softmax')`: Produz a distribuição de probabilidades das 10 classes.
- **Resultado:** Campeã absoluta com **98,36% de acurácia no teste**.

---

## 5. Fase 4: Avaliação Comparativa de Desempenho

### 5.1. Métricas Consolidadas no Teste (14.000 imagens)
O notebook calcula a tabela comparativa exigida:
- **Acurácia Global**
- **Precisão Média Ponderada**
- **Revocação (Recall) Média Ponderada**
- **F1-Score Ponderado** (média harmônica entre precisão e revocação, ponderada pelo suporte de cada classe).
- **Tempos de Treinamento e Inferência:**
  - A CNN exigiu maior tempo de treinamento ($\approx 19$s), mas realiza inferência extremamente rápida ($\approx 0,3$s para 14k imagens em lote).
  - O KNN treina instantaneamente ($0,006$s, pois só armazena os dados), mas é inviável em produção para grandes volumes de consulta (demorou $2,7$s).

### 5.2. Análise de Confusões Frequentes (Heatmap $10 \times 10$)
- O par de dígitos com **maior taxa de confusão na CNN foi o par 9 e 4** (com 16 ocorrências onde o 9 foi previsto como 4).
- **Justificativa técnica:** O 9 e o 4 compartilham a mesma haste vertical direita e um laço superior quadrado/arredondado. Se o topo do 4 fechar levemente ou se o laço do 9 for reto, os filtros convolucionais ativam padrões similares.
- O dígito **9** foi a classe mais desafiadora em todos os 4 modelos, apresentando o menor F1-score da base.

### 5.3. Bootstrap Pareado: CNN vs MLP
- Para responder com rigor se a CNN é verdadeiramente superior à MLP ou se foi apenas sorte na partição de teste:
- O código executa **1.000 reamostragens com reposição (*bootstrap*)** dos 14.000 exemplos de teste.
- Calcula a diferença $\Delta \text{F1} = \text{F1}_{\text{CNN}} - \text{F1}_{\text{MLP}}$ em cada iteração.
- **Resultado:** A diferença média foi de $+0,0070$, com intervalo de confiança de 95% estritamente positivo: $[0,0048; 0,0093]$. Como o zero não está contido no intervalo, comprova-se a superioridade estatisticamente significante da CNN com $p < 0,001$.

---

## 6. Fase 5.1 e 5.2: Desafios A e B — OOD e "Falsa Certeza"

### 6.1. O Experimento de Mascaramento (Class Masking)
- Uma Random Forest com 200 árvores foi treinada a partir de uma base onde os dígitos **4 e 7 foram 100% excluídos**.
- O modelo foi ajustado sem nunca ter visto um 4 ou um 7.

### 6.2. Teste Exclusivo OOD (Out-of-Distribution)
- O modelo foi alimentado com 2.824 imagens que continham **apenas dígitos 4 e 7**.
- A acurácia foi **0% por definição**, pois o classificador só tem nós de saída para os 8 dígitos conhecidos.

### 6.3. O Fenômeno da "Falsa Certeza" (*Overconfidence*)
- **O que aconteceu:** Ao invés de hesitar com probabilidades uniformes ($\approx 12,5\%$ para cada classe), o classificador atribuiu a grande maioria dos 4 e 7 ao **dígito 9**.
- **Pior ainda:** Mais de **100 imagens desconhecidas foram classificadas com mais de 90% de certeza**!
- **Conclusão científica fundamental:** Modelos de classificação com *Softmax* ou votação por árvores assumem a premissa de "mundo fechado" (*Closed-World Assumption*): eles são matematicamente forçados a distribuir a soma 1.0 entre as classes conhecidas. Confiança alta **não significa** que o modelo sabe o que está fazendo; significa apenas que a imagem é menos diferente daquela classe do que das outras.
- **Solução técnica discutida:** É indispensável implementar mecanismos explícitos de **Rejeição OOD** (como detecção por entropia da distribuição ou autoencoders que medem o erro de reconstrução).

---

## 7. Fase 5.3: Desafio C — Inferência com Imagens Próprias

### 7.1. O Protocolo das 30 Fotos
Para evitar manipulação estatística:
- Foram coletadas 30 imagens reais manuscritas em folhas de papel.
- **10 fotos para Desenvolvimento:** Usadas para calibrar os parâmetros de binarização e limiar de contraste.
- **20 fotos Reservadas (Teste Cego):** Fotografadas em folhas diferentes e avaliadas uma única vez com o pipeline congelado.

### 7.2. O Pipeline de Visão Computacional (`etapas_digito`)
A função em [`mnist_demo/preprocessamento.py`](file:///Users/luizhenriqueprovin/Documents/ChatGPT/New%20project/miniprojeto_mod02/mnist_demo/preprocessamento.py) segue 5 etapas rigorosas:

1. **Escala de Cinza:** Converte a foto RGB em intensidades de luminosidade divididas por 255.
2. **Estimativa de Fundo por Filtro Gaussiano:** Aplica um borrão gaussiano de raio largo ($\sigma = \text{largura}/15$) para estimar o fundo iluminado irregularmente pela luz ambiente.
3. **Máscara de Contraste Local:** Subtrai o traço do fundo estimado: $\text{contraste} = \frac{\text{fundo} - \text{cinza}}{\text{fundo}}$. Isso elimina sombras e gradientes de iluminação da folha de papel!
4. **Isolamento e Dilatação Morfológica do Traço:** Binariza onde o contraste $> 0,15$, remove ruídos menores que 1% e aplica dilatação binária com kernel morfológico para fortalecer o traço da caneta.
5. **Redimensionamento Proporcional e Centralização por Centro de Massa:** Redimensiona o dígito para $20 \times 20$ pixels sem distorcer o aspecto original, encaixa em um quadro preto de $28 \times 28$ e aplica a função `scipy.ndimage.shift` para alinhar perfeitamente o centro de massa nos pixels $(13.5, 13.5)$, exatamente como Yann LeCun fez no MNIST em 1998.

### 7.3. Resultados nas Fotos Próprias
- Nas 20 fotos reservadas, a CNN calibrada acertou **19 de 20 dígitos (95% de acurácia)**!
- O único erro foi um dígito 9 previsto como 3 com alta confiança, demonstrando na prática como iluminação e estilo caligráfico interferem no mundo real.

---

## 8. Demonstração Web e Desacoplamento da Inferência

- O módulo [`mnist_demo/inferencia.py`](file:///Users/luizhenriqueprovin/Documents/ChatGPT/New%20project/miniprojeto_mod02/mnist_demo/inferencia.py) cria a classe `PreditorCNN`. Ela extrai as camadas convolucionais de `artifacts/cnn.keras` e computa os *logits* escalonados pela temperatura ($T = 1,009$), dispensando carregar o notebook ou o scikit-learn.
- O servidor em [`mnist_demo/servidor.py`](file:///Users/luizhenriqueprovin/Documents/ChatGPT/New%20project/miniprojeto_mod02/mnist_demo/servidor.py) usa `http.server` nativo e serve a interface em [`mnist_demo/web/`](file:///Users/luizhenriqueprovin/Documents/ChatGPT/New%20project/miniprojeto_mod02/mnist_demo/web/), permitindo desenho interativo em canvas, upload de fotografias e exibição das 10 probabilidades e das 5 etapas do pré-processamento.
- Foi implementado o seletor de espessura de pincel (18px, 24px, 30px), resolvendo o problema de *Domain Shift* e garantindo que desenhos com mouse não fiquem excessivamente finos ao serem reduzidos para $28 \times 28$.
