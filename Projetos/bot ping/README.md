# 🤖 Discord Ping Automator & Report Generator

Um bot de Discord desenvolvido em Python focado em automação de redes. Ele permite disparar testes de latência (ping) simultâneos para múltiplos endereços IP, organizando as janelas de terminal visualmente no monitor do host e gerando um relatório final consolidado em formato `.txt`.

## 🚀 Funcionalidades

- Disparo assíncrono de comandos de rede via `subprocess` e `asyncio`.
- Organização visual automática das instâncias do Prompt de Comando em formato de grade (`pygetwindow`).
- Geração de relatórios de perda de pacotes e latência em arquivos `.txt`.
- Tratamento de caracteres especiais para nomeação segura de arquivos.
- Fluxo de loop interativo diretamente pelo chat do Discord.

## 🛠️ Tecnologias Utilizadas

- **Python 3.x**
- **[discord.py](https://discordpy.readthedocs.io/)**: Integração com a API do Discord.
- **asyncio**: Processamento assíncrono e ganho de performance.
- **pygetwindow**: Manipulação de janelas no ambiente Windows.
- **python-dotenv**: Gerenciamento seguro de variáveis de ambiente.

## ⚙️ Como executar na sua máquina

1. Clone o repositório:
   ```bash
   git clone [https://github.com/cassiorodri7-ai/Automacoes.git](https://github.com/cassiorodri7-ai/Automacoes.git)
   