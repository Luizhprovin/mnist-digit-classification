# Roteiro de gravação - até dez minutos

Mantenha o rosto visível. Use as indicações de tela como orientação, sem lê-las. O roteiro é uma estimativa de duração: faça um ensaio com cronômetro, incluindo as transições e a demonstração. Reserve cerca de um minuto de margem. Os resultados abaixo correspondem à execução registrada no repositório.

Antes de gravar, deixe abertos o README, o notebook executado, o histórico Git e a demonstração local. O notebook precisa ter gerado `artifacts/cnn.keras` e `artifacts/calibracao_cnn.json`. Inicie o servidor com o ambiente virtual ativo: `python -m mnist_demo.servidor`. Abra `http://127.0.0.1:8765`.

## 0:00 a 0:45 - objetivo

[Tela: título do projeto e seu rosto.]

Meu nome é Luiz Henrique Provin. Este projeto compara modelos para reconhecer dígitos manuscritos de zero a nove usando o MNIST. Além de medir acertos, investiguei as confusões, a confiança das previsões e o comportamento diante de classes ausentes do treinamento e de fotografias próprias.

O produto principal é um notebook com código, resultados e interpretações. Também construí uma demonstração local que permite desenhar um dígito, enviar um recorte e observar o processamento até a previsão.

## 0:45 a 1:35 - como executar

[Tela: instalação e execução no README.]

O projeto usa Python 3.12. Depois de clonar o repositório, crio o ambiente com `python3.12 -m venv .venv`, ativo esse ambiente e instalo as dependências do `requirements.txt`.

No VS Code, seleciono o kernel desse ambiente e executo o notebook desde o início. O MNIST é baixado do OpenML na primeira execução e fica em cache. As fotos necessárias estão no repositório, com caminhos relativos.

Um clone novo precisa executar o notebook para gerar a CNN e a calibração. Depois disso, posso iniciar a demonstração sem treinar novamente. O ambiente foi validado em macOS; não garanto resultados idênticos em qualquer computador.

## 1:35 a 2:25 - planejamento e Git

[Tela: tabela de branches e histórico.]

Organizei as tarefas pelas fases do enunciado: análise dos dados, preparação, modelos, avaliação e desafios. A branch develop concentra as integrações, e main recebe a versão de entrega.

As branches de funcionalidades registram etapas como eda, preprocessamento, knn, random-forest, mlp, cnn, calibracao e imagens-proprias. Depois vieram a demonstração, os testes e a revisão final. As branches são preservadas para mostrar a evolução do trabalho.

As primeiras integrações ocorreram localmente; o fechamento utiliza pull requests. A mudança de treinamento está identificada na branch cnn-convergencia, permitindo comparar os resultados anteriores e atuais.

## 2:25 a 4:35 - dados e decisões de modelagem

[Tela: distribuição, divisão e arquiteturas.]

O MNIST contém 70 mil imagens de 28 por 28 pixels, equivalentes a 784 valores. A escala original vai de zero, preto, a 255, branco. As dez classes têm frequências próximas, mas não idênticas.

Dividi os dados em 60% para treino, 10% para validação, 10% para calibração e 20% para teste, mantendo aproximadamente as proporções das classes. Os índices não se sobrepõem e a auditoria não encontrou imagens exatamente duplicadas.

Dividir os pixels por 255 coloca as entradas entre zero e um e facilita o treinamento das redes. No KNN, aplicar o mesmo fator a todos os pixels preserva a ordem das distâncias. A normalização não demonstra, por si só, ganho de acurácia.

Comparei três famílias com dois hiperparâmetros e quatro combinações cada: no KNN, vizinhos e pesos; na Random Forest, árvores e profundidade; na MLP, tamanho das camadas e regularização L2. A seleção usa F1 ponderado na validação.

Acrescentei uma CNN de arquitetura fixa. Ela tem duas convoluções, duas operações de pooling e camadas densas. Usa L2 na camada densa oculta, sem Dropout. As convoluções exploram padrões locais e compartilham pesos pela imagem.

Revisei a parada antecipada das redes: agora acompanho acurácia de validação, com paciência de cinco épocas. A CNN executou quinze épocas e restaurou os pesos da décima. O teste já havia sido observado na versão anterior; esta reavaliação usa as mesmas partições e não representa um novo teste cego.

## 4:35 a 5:50 - resultados e probabilidades

[Tela: tabela, matriz da CNN e calibração.]

A CNN obteve 98,9929% de acurácia: 13.859 acertos em 14 mil imagens. Foram 89 acertos adicionais em relação à versão anterior. A MLP permaneceu com 97,66%, o KNN com 97,03% e a Random Forest com 96,57%.

Na CNN, a confusão mais frequente foi 4 → 9, com 11 imagens. O menor F1 foi do dígito quatro. A CNN levou aproximadamente cinquenta segundos para ajustar a configuração escolhida. Os tempos são de uma execução local, sem benchmark repetido.

O bootstrap pareado com mil reamostragens sustenta uma vantagem de F1 da CNN sobre a MLP neste teste. O intervalo considera os modelos já treinados e não mede a variação de novos treinamentos.

A temperatura foi ajustada somente nas sete mil imagens de calibração. Ela preserva a classe prevista e modifica as probabilidades. No teste, a log loss caiu cerca de 12,9% e o ECE também melhorou. Isso não garante probabilidades adequadas às fotos próprias.

## 5:50 a 7:45 - desafios e demonstração

[Tela: matriz das classes ocultadas e galeria das fotos.]

Nos desafios A e B, treinei uma nova Random Forest sem os dígitos quatro e sete. Ao avaliar somente essas classes, o acerto foi zero por construção: elas não estavam entre as saídas possíveis.

Houve 106 erros com confiança de pelo menos 90%, entre 2.824 exemplos. Isso mostra falsa certeza. A confiança média ficou abaixo de 60%, portanto a confiança elevada aparece em uma parte dos casos, não em todos.

Nas fotos próprias, usei dez recortes de uma foto para desenvolver o processamento e vinte recortes de outras duas para avaliação. A CNN acertou vinte de vinte reservados. O desenvolvimento teve nove acertos; o dígito um foi previsto como dois.

São dados de uma pessoa e poucas fotografias. Não posso concluir que o modelo terá cem por cento de acerto em outras condições. Também não posso atribuir um erro à luz sem controlar esse fator.

[Tela: demonstração. Mostre um exemplo, limpe, desenhe um dígito e classifique. Reserve tempo para a resposta.]

Aqui vemos a previsão, as dez probabilidades e as etapas: original, cinza, contraste, traço e entrada de 28 por 28. A demonstração reutiliza o processamento do notebook. Ao limpar ou trocar a entrada, o resultado anterior desaparece.

## 7:45 a 8:35 - limites e melhorias

[Tela: conclusão ou seu rosto.]

Como melhorias, eu avaliaria outras pessoas e fotografaria os mesmos dígitos sob luz controlada. Também estudaria aumento de dados no treino e um mecanismo de rejeição para entradas desconhecidas, medindo seus erros e recusas indevidas.

Os testes verificam processamento, manifesto, inferência e afirmações selecionadas da documentação. O CI não retreina a CNN; a previsão completa também foi verificada localmente.

O principal aprendizado foi separar acerto de confiança e distinguir uma melhora observada de uma garantia de generalização. Cada resultado está acompanhado de seu código, sua amostra e suas limitações. Obrigado.
