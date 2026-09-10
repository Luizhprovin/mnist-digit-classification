# Roteiro Falado para Gravação do Vídeo (Até 10 Minutos)

> **Instruções para Gravação:**
> - Mantenha a webcam ligada com seu rosto bem iluminado e visível em um canto da tela (ex: via OBS Studio, Loom, QuickTime ou gravação de tela com câmera).
> - As marcações entre colchetes como `[pausa]`, `[mostra a tela]` e `[aponta com o mouse]` são orientações cênicas para guiar o seu ritmo.
> - Fale com calma, naturalidade e segurança. Este roteiro foi cronometrado para durar entre **8 minutos e meio e 9 minutos e meio**, deixando uma margem segura antes do limite de 10 minutos.

---

### [0:00 - 1:15] Bloco 1: Abertura e Objetivo do Sistema (Tópico 1)

`[Rosto na câmera, sorriso tranquilo, tom natural]`

"Fala pessoal, tudo bem? Meu nome é Luiz Henrique Provin e este é o meu mini-projeto avaliativo do Módulo 2 de Desenvolvimento de IA para Análise Preditiva.

`[Pausa breve]`

O objetivo principal desse sistema é construir e comparar um pipeline preditivo multiclasse de ponta a ponta para classificar os dígitos manuscritos de 0 a 9 do benchmark MNIST. 

Mas a ideia aqui não foi só treinar modelos em ambiente perfeito de laboratório. A proposta central do projeto é estressar e testar a generalização extrema desses classificadores quando eles são confrontados com cenários fora do padrão: como imagens que nunca foram vistas no treino e fotografias do mundo real, tiradas do papel com a câmera do celular.

No final, além do notebook com todo o rigor experimental, a gente também colocou isso em prática construindo uma demonstração interativa local com visão computacional e inferência desacoplada da nossa melhor rede, que eu vou mostrar rodando daqui a pouquinho."

---

### [1:15 - 2:30] Bloco 2: Como Executar o Sistema e Reprodutibilidade (Tópico 2)

`[Compartilha a tela com o README.md e terminal]`

"Bom, antes de olhar os números, como é que qualquer pessoa ou avaliador roda esse projeto na máquina?

`[Pausa]`

A primeira coisa que eu me preocupei aqui foi com a reprodutibilidade. Como vocês podem ver aqui no `README.md`, o projeto foi desenvolvido em Python 3.12. Para rodar, o processo é super simples:

Basta clonar o repositório público, criar um ambiente virtual com `python3 -m venv .venv`, ativar com `source .venv/bin/activate` e instalar o `requirements.txt`. Todas as versões de bibliotecas, como Scikit-Learn, TensorFlow, Keras, NumPy e Pillow, estão cravadas lá sem conflito de versão.

`[Aponta para o notebook no VS Code]`

Para quem quiser conferir o experimento completo, basta abrir o arquivo `projeto.ipynb` e clicar em 'Executar Tudo'. O download do dataset é feito direto da API do OpenML, mas ele é salvo numa pasta local `data/cache`. Isso significa que não existe nenhum caminho absoluto de arquivo na minha máquina — é tudo caminho relativo —, então o código roda em qualquer computador sem dar erro de arquivo não encontrado.

E se a pessoa quiser apenas testar a aplicação web interativa sem precisar rodar ou treinar o notebook de novo, basta digitar no terminal: `python -m mnist_demo.servidor` e abrir `localhost:8765` no navegador."

---

### [2:30 - 4:00] Bloco 3: Organização do Projeto e Git Flow (Tópicos 3 e 4)

`[Mostra o histórico de branches no terminal ou no GitHub]`

"Agora, sobre como eu planejei e organizei as tarefas antes de escrever a primeira linha de código...

`[Pausa para respirar]`

Eu estruturei o desenvolvimento seguindo o ciclo clássico de Ciência de Dados e as fases do edital: começando pela análise exploratória, passando pela engenharia de features, treinamento e validação dos modelos clássicos e profundos, até chegar na avaliação cega e nos testes de estresse.

E para garantir qualidade de engenharia de software, eu segui à risca o padrão de Git Flow exigido no edital:

`[Mostra a tabela de versionamento no README ou o git log]`

A branch `main` é a nossa versão estável de entrega. A branch `develop` concentrou todas as integrações de funcionalidades. E para cada fase do edital, eu criei uma *feature branch* separada a partir da `develop`. 

Por exemplo:
- `feature/eda` para a análise exploratória;
- `feature/preprocessamento` para a divisão dos dados;
- `feature/knn`, `feature/random-forest`, `feature/mlp` e `feature/cnn` para cada modelo;
- `feature/calibracao` e `feature/avaliacao` para as métricas;
- `feature/classes-ocultadas` para os testes de robustez;
- `feature/imagens-proprias` e `feature/avaliacao-proprias` para as fotos reais;
- E finalmente `feature/demonstracao`, `feature/ci` e `feature/ajuste-traco` para a interface web, os testes automatizados e o refinamento do traço.

Nenhuma branch foi excluída após os merges, e todos os commits seguiram mensagens concisas no modo imperativo, como 'implementa X' ou 'adiciona Y'."

---

### [4:00 - 6:30] Bloco 4: Raciocínio Técnico do Notebook e Escolha dos Modelos (Tópico 6)

`[Rola pelo notebook projeto.ipynb mostrando os gráficos e tabelas]`

"Entrando agora no código e nas decisões técnicas do experimento...

`[Pausa]`

Na Fase 1 e 2, temos o MNIST com 70 mil imagens. Cada imagem de 28 por 28 pixels foi desdobrada num vetor de 784 features, e os pixels foram normalizados dividindo por 255.0. 
Por que essa divisão é indispensável? Porque colocar os valores na escala de 0 a 1 evita que os gradientes das redes neurais explodam no início do treino e impede que algoritmos baseados em distância euclidiana sejam distorcidos pela magnitude dos pixels.

Outro ponto que eu tive muito cuidado foi no protocolo de dados: eu não dividi apenas em treino e teste. Nós separamos em 4 partes estratificadas: 60% para treino, 10% para validação de hiperparâmetros, 10% exclusivo para calibração de probabilidades e 20% para teste cego independente.

`[Pausa e aponta para a tabela comparativa]`

Na Fase 3 e 4, comparamos os modelos variando ao menos dois hiperparâmetros em cada um:
1. No **KNN**, testamos 3 e 5 vizinhos, com pesos uniformes e ponderados por distância. O KNN com 3 vizinhos e peso por distância venceu com 97,03% de acurácia. O problema dele foi o custo computacional na inferência: demorou 2,7 segundos para avaliar o teste, porque ele precisa calcular a distância para todos os 42 mil pontos de treino a cada previsão.
2. Na **Random Forest**, variamos entre 100 e 200 árvores, com e sem limite de profundidade. A floresta com 200 árvores sem limite foi a melhor, atingindo 96,57%.
3. Na **MLP**, exploramos arquiteturas de duas camadas ocultas e regularização L2. A configuração de 256 e 128 neurônios com L2 de 0.0001 alcançou 97,66%.
4. E por fim, implementamos uma **CNN** convolucional com duas camadas Conv2D, Max Pooling e Dropout de 30%. 

A CNN foi a grande campeã, atingindo **98,36% de acurácia global** e F1 ponderado de 0,9835. E para comprovar se ela era realmente superior à MLP e não apenas sorte da partição, nós rodamos um **bootstrap pareado com 1.000 reamostragens**, que confirmou com 95% de confiança uma vantagem estatisticamente significante da CNN em relação à MLP.

A matriz de confusão mostrou que o par mais difícil para a rede foi o **9 e o 4**, com 16 confusões, justamente por compartilharem a mesma haste reta vertical e o laço superior."

---

### [6:30 - 8:00] Bloco 5: Os Desafios A, B e C e a Demonstração Web (Tópicos 1 e 6)

`[Mostra os gráficos de classes ocultadas no notebook e depois abre o navegador]`

"Nos desafios de estresse, as coisas ficaram ainda mais interessantes:

`[Pausa]`

Nos Desafios A e B, nós treinamos um modelo ocultando completamente os dígitos 4 e 7. Quando forçamos esse modelo a classificar 2.800 imagens apenas de 4 e 7, a acurácia foi zero por definição, mas o alerta de IA foi evidente: o modelo não hesitou! Ele previu quase tudo como dígito 9 e emitiu **mais de 100 previsões com mais de 90% de confiança**. Isso ilustra o perigo da 'falsa certeza' (*overconfidence*) em redes neurais quando não existe um mecanismo explícito de rejeição OOD.

`[Pausa]`

No Desafio C, eu escrevi dígitos em papel branco e tirei fotos reais com celular. Criamos um pipeline de visão computacional que converte para cinza, calcula o contraste relativo contra o fundo da folha para eliminar sombras, isola o traço e centraliza pelo centro de massa em 28 por 28. Nas 20 fotos reservadas de teste cego, a CNN acertou **19 de 20 imagens, ou seja, 95% de acerto**.

`[Muda a tela para a demonstração web: http://127.0.0.1:8765]`

E para tornar isso totalmente interativo, nós empacotamos essa inferência nessa demonstração web local.

`[Desenha um dígito na tela, por exemplo, o número 3]`

Vejam só: eu desenho aqui no canvas... clico em 'Classificar Dígito'... e instantaneamente a CNN processa a imagem, nos dá a classe prevista, a confiança calibrada por temperatura e as 10 barras de probabilidades. Além disso, o painel aqui embaixo mostra exatamente as 5 etapas da visão computacional: a imagem original, os tons de cinza, o contraste local corrigido, o traço morfológico e a entrada final de 28 por 28 pixels que realmente entra na rede.

Também temos botões aqui para testar com um clique os exemplos fotografados do estudo, como o dígito 0 e o dígito 1, e uma aba para upload de qualquer foto nova."

---

### [8:00 - 9:30] Bloco 6: O que faltou e Melhorias Futuras (Tópico 5 e Fechamento)

`[Rosto na câmera ou dividindo tela com a demo]`

"Para finalizar: respondendo à pergunta crítica do edital... *'O que eu acho que faltou no código e o que poderia ser melhorado?'*

`[Pausa enfática]`

Uma descoberta muito rica durante os testes da interface foi o comportamento do **dígito 8**. Eu percebi que, ao desenhar o 8 com o mouse ou trackpad, a rede às vezes hesitava ou confundia com o 2 ou com o 3. 

E por que isso acontece? Por causa do que chamamos de *Domain Shift*, ou mudança de domínio. O MNIST original foi escrito com caneta em papel há mais de 25 anos, onde o traço tem espessura de 3 a 4 pixels e atrito natural. No mouse, o traçado digital é rápido, tem cantos vivos e, muitas vezes, as alças do 8 não fecham perfeitamente ou ficam muito finas. Como o 8 compartilha as mesmas curvaturas laterais do 3 e a base do 2, se o traço falhar, a convolução ativa o neurônio errado.

Para mitigar isso no código, nós implementamos um seletor de espessura de pincel com padrão em 24 pixels e suavização de pontos. Mas como melhorias futuras para o projeto, eu destaco três pontos essenciais:
1. Treinar os modelos com *Data Augmentation* usando transformações elásticas e pequenas rotações, aproximando o treino de telas digitais;
2. Adicionar uma operação morfológica de fechamento (*closing*) no pré-processamento para fechar automaticamente laços imperfeitos no desenho;
3. E implementar um mecanismo formal de rejeição de entradas baseado na entropia da distribuição ou autoencoders, para que a rede saiba dizer 'não sei' em vez de emitir falsa certeza diante de imagens desconhecidas.

`[Pausa final e conclusão]`

Com isso, fechamos todas as fases do edital, com código limpo, pipeline de testes automatizados no GitHub Actions e reprodutibilidade garantida. 

Muito obrigado pela atenção de todos e fico à disposição para as perguntas!"
