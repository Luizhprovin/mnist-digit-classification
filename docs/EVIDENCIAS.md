# Mapa de evidências do experimento

## Evidências técnicas

| Análise | Local no notebook | Evidência |
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

As branches de cada etapa são preservadas. As primeiras integrações ocorreram localmente por fast-forward; o fechamento local usa commits de merge. O repositório público mantém as branches de cada etapa. A versão consolidada é integrada de `develop` para `main` por pull request.

Repositório público: [Luizhprovin/mnist-digit-classification](https://github.com/Luizhprovin/mnist-digit-classification).
