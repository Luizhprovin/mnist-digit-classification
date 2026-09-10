# Conferência da entrega

## Evidências técnicas

| Requisito | Local no notebook | Evidência |
|---|---|---|
| Fase 1 — EDA | Seção 2 | Dimensões, distribuição, grade 2 × 5 e representação dos pixels |
| Fase 2 — preparação | Seção 3 | Divisão estratificada, ausência de sobreposição, normalização e justificativas |
| Fase 3 — três modelos | Seção 4 | KNN, Random Forest e MLP com duas variações de hiperparâmetros e quatro combinações por família |
| Fase 4 — comparação | Seção 6 | Quatro matrizes 10 × 10, acurácia, precisão, recall, F1 e tempos |
| Desafios A e B | Seção 7 | Novo modelo sem 4 e 7, teste exclusivo dessas classes, matriz e análise de confiança |
| Desafio C | Seção 8 | Processamento, centralização, inferência e gráficos das probabilidades de trinta dígitos |
| Conclusão técnica | Seções 6 a 9 | Modelo vencedor, confusões, custo, limites e melhorias |
| Reprodutibilidade | README e requirements.txt | Instalação, execução, versões e dados próprios com caminhos relativos |
| Extras planejados | Seções 4 a 6 | CNN, diagramas, calibração e bootstrap pareado |
| Demonstração interativa | `mnist_demo/` | Interface web em HTML/JS com desenho, upload, exemplos e inferência desacoplada |
| Automação e qualidade | `tests/` e `.github/` | Suíte de testes unitários e pipeline de integração contínua (CI) com GitHub Actions |

## Git e GitHub

As branches de cada etapa são preservadas. As primeiras integrações ocorreram localmente por fast-forward; o fechamento local usa commits de merge. O repositório público mantém as branches de cada etapa. A versão de entrega é integrada de `develop` para `main` por pull request. A versão consolidada deve estar em `main` antes da entrega.

Repositório público: [Luizhprovin/mnist-digit-classification](https://github.com/Luizhprovin/mnist-digit-classification).

## Vídeo e submissão — pendentes

A gravação e edição ficam com o estudante. O enunciado exige vídeo de até dez minutos, com rosto visível, cobrindo:

- Objetivo e demonstração de funcionamento.
- Preparação do ambiente e execução.
- Organização das tarefas e planejamento.
- Branches utilizadas e finalidade de cada uma.
- Justificativa das escolhas técnicas e interpretação dos resultados.
- Limitações e melhorias possíveis.

O vídeo deverá ser disponibilizado no Google Drive como leitor para qualquer pessoa com o link. Antes de submeter, conferir o acesso público ao repositório, o acesso ao vídeo e o código consolidado em `main`.

O prazo indicado no enunciado fornecido é **14/09/2026 às 22h**. A entrega exige os dois links no AVA. O enunciado orienta não alterar o projeto após a submissão até receber a nota. Vídeo e submissão não foram realizados por este repositório.
