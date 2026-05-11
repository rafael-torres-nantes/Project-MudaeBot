# Bot de Automação para Mudae no Discord

## 👨‍💻 Projeto desenvolvido por:
[Rafael Torres Nantes](https://github.com/rafael-torres-nantes)

## Índice

* [📚 Contextualização do projeto](#-contextualização-do-projeto)
* [🛠️ Tecnologias/Ferramentas utilizadas](#%EF%B8%8F-tecnologiasferramentas-utilizadas)
* [🖥️ Funcionamento do sistema](#%EF%B8%8F-funcionamento-do-sistema)
   * [🎲 Parte 1 - Roll Automático](#parte-1---roll-automático)
   * [❤️ Parte 2 - Auto-Claim](#parte-2---auto-claim)
* [🔀 Arquitetura da aplicação](#arquitetura-da-aplicação)
* [📁 Estrutura do projeto](#estrutura-do-projeto)
* [📌 Como executar o projeto](#como-executar-o-projeto)
* [🕵️ Dificuldades Encontradas](#%EF%B8%8F-dificuldades-encontradas)

## 📚 Contextualização do projeto

O projeto tem como objetivo automatizar interações com o **Mudae**, um bot de gacha popular no Discord. O sistema executa **rolls automáticos de personagens** a cada hora via comando `$wa`, verifica disponibilidade de casamento com `$mu` antes de cada roll, e realiza **auto-claim inteligente** de personagens desejados reagindo com ❤️ conforme prioridade configurável.

A priorização de claim segue a seguinte hierarquia:
1. Personagens no **TOP 100 kakera** do servidor
2. Personagens na **wishlist pessoal**
3. Personagens com **kakera acima do mínimo configurado**
4. Personagens de **animes na anime_wishlist**

## 🛠️ Tecnologias/Ferramentas utilizadas

[<img src="https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white">](https://www.python.org/)
[<img src="https://img.shields.io/badge/Visual_Studio_Code-007ACC?logo=visual-studio-code&logoColor=white">](https://code.visualstudio.com/)
[<img src="https://img.shields.io/badge/discord.py--self-5865F2?logo=discord&logoColor=white">](https://github.com/dolfies/discord.py-self)
[<img src="https://img.shields.io/badge/python--dotenv-ECD53F?logo=python&logoColor=black">](https://pypi.org/project/python-dotenv/)
[<img src="https://img.shields.io/badge/rapidfuzz-FF6B6B?logo=python&logoColor=white">](https://github.com/maxbachmann/RapidFuzz)
[<img src="https://img.shields.io/badge/GitHub-181717?logo=github&logoColor=white">](https://github.com/)

## 🖥️ Funcionamento do sistema

### 🎲 Parte 1 - Roll Automático

O módulo de roll (`service/roll.py`) gerencia o ciclo horário de interação com o Mudae. Antes de cada roll, o bot envia `$mu` para verificar se há claim disponível. Caso positivo, envia `$wa` para iniciar o gacha. O listener de mensagens aguarda a resposta do Mudae com timeout configurável via variável de ambiente `TIMEOUT_MU`.

* **RollService**: Orquestra o envio de `$mu` e `$wa`, retornando o estado de disponibilidade de claim.
* **Loop horário**: Configurado com `discord.ext.tasks` para disparar a cada hora, mantendo o estado de `can_marry` atualizado.

### ❤️ Parte 2 - Auto-Claim

O módulo de claim (`service/claim.py`) processa cada embed enviado pelo Mudae no canal configurado. Utiliza **fuzzy matching** com `rapidfuzz` para tolerar variações de escrita entre os nomes na wishlist e os exibidos pelo bot.

* **ClaimService**: Avalia cada personagem aparecido conforme a hierarquia de prioridade e reage com ❤️ quando há correspondência.
* **KakeraService**: Busca o TOP 100 kakera do servidor via `$top` na inicialização para alimentar a prioridade mais alta.
* **Parser**: O `utils/parser.py` extrai nome do personagem, série, valor de kakera e status de claim a partir dos embeds do Mudae.

## 🔀 Arquitetura da aplicação

O sistema segue uma arquitetura em camadas onde `bot.py` atua como orquestrador principal, coordenando três serviços independentes. Toda a configuração é centralizada em `config.py`, que carrega variáveis de ambiente via `python-dotenv`, eliminando valores hardcoded no código. Os arquivos de wishlist ficam na pasta `data/` e são carregados na inicialização.

```
Discord API
    │
    ▼
bot.py (orquestrador + event handlers)
    │
    ├── KakeraService  →  $top  →  Mudae Bot
    ├── RollService    →  $mu / $wa  →  Mudae Bot
    └── ClaimService   ←  on_message ←  Mudae Bot
            │
            └── MudaeParser (extração de embed)
```

## 📁 Estrutura do projeto

```
.
├── bot.py                   # Orquestrador principal e event handlers
├── config.py                # Configuração centralizada via variáveis de ambiente
├── requirements.txt         # Dependências do projeto
├── .env                     # Variáveis de ambiente (não commitar)
├── .env.example             # Template de variáveis de ambiente
├── .gitignore
│
├── service/
│   ├── claim.py             # Lógica de reivindicação com fuzzy matching
│   ├── kakera.py            # Busca do TOP 100 kakera via $top
│   └── roll.py              # Execução de $mu e $wa com verificação de claim
│
├── utils/
│   ├── parser.py            # Parsing de embeds do Mudae
│   └── wishlist.py          # Carregamento das wishlists
│
└── data/
    ├── wishlist.txt         # Lista de personagens desejados
    └── anime_wishlist.txt   # Lista de animes desejados
```

## 📌 Como executar o projeto

1. **Clone o repositório:**
   ```bash
   git clone https://github.com/rafael-torres-nantes/mudae-bot.git
   cd mudae-bot
   ```

2. **Instale as dependências:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure as variáveis de ambiente:**
   ```bash
   cp .env.example .env
   ```
   Edite o arquivo `.env` e preencha o `DISCORD_TOKEN` com seu token e ajuste as demais configurações conforme necessário.

4. **Adicione personagens à wishlist:**

   Edite `data/wishlist.txt` com um nome por linha (linhas com `#` são comentários):
   ```
   # Personagens favoritos
   Rem
   Zero Two
   ```

   Edite `data/anime_wishlist.txt` com animes desejados:
   ```
   # Isekai
   Re:Zero
   Sword Art Online
   ```

5. **Execute o bot:**
   ```bash
   python bot.py
   ```

### Variáveis de Ambiente

| Variável | Padrão | Descrição |
|---|---|---|
| `DISCORD_TOKEN` | — | **Obrigatório.** Token de autenticação do Discord |
| `MUDAE_BOT_ID` | `432610292342587392` | ID do bot Mudae |
| `TARGET_GUILD` | `OCOLAST` | Nome do servidor Discord |
| `TARGET_CHANNEL` | `cartinhas` | Canal onde executar os rolls |
| `KAKERA_MIN` | `150` | Valor mínimo de kakera para auto-claim |
| `FUZZY_THRESHOLD` | `85` | Limiar de similaridade para matching (0-100) |
| `TIMEOUT_TOP` | `15` | Timeout em segundos para resposta do `$top` |
| `TIMEOUT_MU` | `10` | Timeout em segundos para resposta do `$mu` |
| `WISHLIST_FILE` | `data/wishlist.txt` | Caminho para o arquivo de wishlist |
| `ANIME_WISHLIST_FILE` | `data/anime_wishlist.txt` | Caminho para o arquivo de anime wishlist |

## 🕵️ Dificuldades Encontradas

Durante o desenvolvimento do projeto, algumas dificuldades foram enfrentadas, como:

- **Race conditions com o Mudae:** O Mudae responde muito rapidamente aos comandos, o que exigiu registrar o `wait_for` *antes* de enviar o comando para evitar perder a resposta. Sem isso, o listener era criado depois que a mensagem já havia chegado.
- **Fuzzy matching de nomes:** Personagens no Mudae possuem nomes com variações de escrita (romaji, katakana, abreviações), tornando a comparação exata inviável. O uso de `rapidfuzz` com threshold de 85% equilibrou precisão e recall.
- **Parsing dinâmico de embeds:** O formato dos embeds do Mudae varia conforme o comando (`$mu`, `$top`, rolls), exigindo um parser robusto capaz de lidar com campos ausentes e estruturas distintas.
