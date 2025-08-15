# Study App for CyberSecurity Certification

[English](./README.md) | [Português (Portugal)](./README.pt.md)

## Português (PT)

Uma aplicação de estudo interativa que simula um exame real com 90 perguntas em 90 minutos, baseadas nos objetivos do exame.
 
É possível usá-la localmente ou online. Para uso local, siga as instruções abaixo. Para a versão online, aceda a https://miguke.github.io/CyberCertPrepExams/

## Funcionalidades

- **Modo de Estudo**: Prática por tópicos específicos.
- **Simulação de Exame**: Simula um exame real com 90 perguntas em 90 minutos.
- **Feedback Imediato**: Acesso a explicações detalhadas para cada resposta.
- **Acompanhamento do Progresso**: Monitorização do seu desempenho com estatísticas em tempo real.
- **Interface Responsiva**: Compatível com computadores, tablets e smartphones.
- **Resultados e Estatísticas**: Ver resultados e estatísticas do seu desempenho no final da simulação de exame.

## Motivação

O estudo de hoje já não é como há 5 ou 10 anos. Acredito que o estudo interativo é a melhor forma de aprender, sobretudo com resultados imediatos e a possibilidade de praticar em qualquer lugar e a qualquer hora. Desenvolvi esta aplicação para me permitir praticar perguntas alinhadas com os objetivos do exame e estudar onde e quando quiser. E, claro, por estar na palma da mão, consigo trocar tempo nas redes sociais por estudo produtivo.

## Como foi construída a aplicação?

A minha área de formação não é programação. Um grande amigo de longa data, João Guerreiro (@jqsguerreiro), recomendou o Windsurf. Todo o desenvolvimento foi realizado com o auxílio de Inteligência Artificial, necessitando de poucas intervenções manuais. 

As perguntas foram recolhidas de fontes online, como sites e documentos PDF. Muitos destes PDFs, contendo perguntas e explicações, foram encontrados através de pesquisas no Google usando o dork "filetype:pdf" com palavras-chave específicas.

Depois de reunir os PDFs, reparei que a IA não os conseguia processar nem extrair corretamente as perguntas e as explicações. Através do Cascade AI, foram criados scripts em Python para processar os PDFs e extrair esse conteúdo. O meu contributo limitou‑se a orientar a IA no processamento.

Perdi algum tempo em "debate" com a IA, a fazer testes, correções e ajustes aos scripts, para que o analisador conseguisse extrair as perguntas e as explicações corretamente. Foi aí que o @jqsguerreiro indicou a utilização de servidores MCP.

Agora que o servidor MCP está a funcionar corretamente, a IA consegue processar os PDFs, sem necessidade de criar scripts, e extrair perguntas e explicações de forma fiável, usando material oficial de estudo e, acima de tudo, corrigindo perguntas e explicações de alguns PDFs.

## Como Executar Localmente

1. **Pré-requisitos**:
   - Python 3.6 ou superior
   - Navegador moderno (Chrome, Firefox, Edge, Safari)

2. **Instalação**:
   ```bash
   # Clone o repositório
   git clone [URL_DO_REPOSITÓRIO]
   cd CyberCertPrepExams
   ```

3. **Iniciar o servidor de desenvolvimento**:
   ```bash
   python server.py
   ```
   Isto iniciará um servidor local em `http://localhost:8080` e abrirá automaticamente o navegador.

4. **Aceder à aplicação**:
   - Abra o seu navegador e aceda a `http://localhost:8080`.
   - Selecione o curso que deseja.
   - Escolha entre o modo de estudo ou a simulação de exame.

### Personalizar o Tema

Para personalizar as cores, fontes e o layout da aplicação, edite os ficheiros CSS na pasta `css/`.

## Licença

Este projeto está licenciado sob a Licença MIT. Para mais detalhes, consulte o ficheiro [LICENSE](LICENSE).

## Agradecimentos

Um agradecimento especial ao João Guerreiro (@jqsguerreiro), que me recomendou o Windsurf e me ajudou a perceber como funcionam o Git e o GitHub.
