# CompTIA A+ 220-1101 Study App

Uma aplicação de estudo interativa para o exame CompTIA A+ 220-1101, que permite aos utilizadores praticar com perguntas baseadas nos objetivos do exame.

## Funcionalidades

- **Modo de Estudo**: Prática por tópicos específicos.
- **Simulação de Exame**: Simula um exame real com 90 perguntas em 90 minutos.
- **Feedback Imediato**: Acesso a explicações detalhadas para cada resposta.
- **Acompanhamento do Progresso**: Monitorização do seu desempenho com estatísticas em tempo real.
- **Interface Responsiva**: Compatível com computadores, tablets e smartphones.

## Motivação

Estudar através de PDFs ou ler no computador é uma tarefa cansativa e demorada. Frequentemente, ao ler as perguntas, a nossa visão periférica acaba por revelar a resposta sem intenção. Para contornar este problema, desenvolvi uma aplicação interativa que permite aos utilizadores praticar com perguntas baseadas nos objetivos do exame. Desta forma, é possível estudar através do telemóvel, substituindo o tempo passado nas redes sociais por uma atividade produtiva. A capacidade de praticar e estudar em qualquer lugar e a qualquer hora representa uma vantagem significativa.

## Como foi construída a aplicação?

A minha área de formação não é programação. Com a ajuda do João Guerreiro (@jqsguerreiro), que me recomendou o Windsurf, todo o desenvolvimento foi realizado com o auxílio de Inteligência Artificial, necessitando de poucas intervenções manuais. Foram utilizados vários modelos de IA, como o Gemini, SWE (do Windsurf), ChatGPT, DeepSeek, entre outros.
As perguntas foram recolhidas de fontes online, como sites e documentos PDF. Muitos destes PDFs, contendo perguntas e explicações, foram encontrados através de pesquisas no Google com palavras-chave específicas, utilizando o operador `filetype:pdf` para localizar documentação pública.

## Como Executar Localmente

1. **Pré-requisitos**:
   - Python 3.6 ou superior
   - Navegador moderno (Chrome, Firefox, Edge, Safari)

2. **Instalação**:
   ```bash
   # Clone o repositório
   git clone [URL_DO_REPOSITÓRIO]
   cd A-220-1101
   ```

3. **Iniciar o servidor de desenvolvimento**:
   ```bash
   python server.py
   ```
   Isto iniciará um servidor local em `http://localhost:8000` e abrirá automaticamente o navegador.

4. **Aceder à aplicação**:
   - Abra o seu navegador e aceda a `http://localhost:8000`.
   - Selecione o curso "CompTIA A+ 220-1101".
   - Escolha entre o modo de estudo ou a simulação de exame.

## Personalização

### Adicionar Novas Perguntas

1. Para adicionar ou modificar perguntas, edite os ficheiros JSON localizados na pasta `data/1101/`.
2. O formato de cada pergunta deve ser:
   ```json
   {
     "id": 1,
     "type": "single",
     "question": "A sua pergunta aqui",
     "options": ["Opção 1", "Opção 2", "Opção 3", "Opção 4"],
     "correct": [0],
     "explanation": "Explicação detalhada da resposta correta"
   }
   ```
   - `type`: Pode ser "single" (uma resposta) ou "multiple" (múltiplas respostas)
   - `correct`: Índice ou índices da(s) opção(ões) correta(s) no array `options`.

### Personalizar o Tema

Para personalizar as cores, fontes e o layout da aplicação, edite os ficheiros CSS na pasta `css/`.

## Licença

Este projeto está licenciado sob a Licença MIT. Para mais detalhes, consulte o ficheiro [LICENSE](LICENSE).

## Agradecimentos

Um agradecimento especial ao João Guerreiro (@jqsguerreiro) pela sua ajuda em várias fases do projeto.
