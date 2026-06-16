# 🌐 NOC Automator: Gerenciamento Inteligente de ONUs

Um robô de automação desenvolvido em Python para otimizar as operações do Network Operations Center (NOC). O bot realiza a interação com sistemas de OLT e CRMs, automatizando processos de rede e fechamento de chamados com inteligência geográfica.

## 🚀 Funcionalidades

- **Gestão de ONUs:** Remoção automatizada de equipamentos utilizando integração com OLT Cloud e Xshell.
- **Roteamento Dinâmico:** Tomada de decisão baseada no mapeamento de bairros e HUBs locais para direcionamento de rotinas.
- **Busca de Contingência:** Varredura avançada via Serial Number (SN) caso a localização pelo número do contrato falhe.
- **Integração com CRM:** Automação web web para atualização e finalização de chamados de forma automática.
- **Relatórios em Tempo Real:** Disparo de relatórios de execução para canais do Discord.
- **Segurança:** Código estruturado para compilação em executável protegido.

## 🛠️ Tecnologias Utilizadas

- **Python 3.x**
- **Selenium:** Para automação de interações web no CRM e painéis na nuvem.
- **Xshell:** Para automação de comandos de infraestrutura via terminal.
- **Integração Discord:** Para mensageria e logs operacionais.
- **PyInstaller** (ou similar): Para compilação e segurança do código-fonte.

## ⚙️ Como executar na sua máquina

1. Clone o repositório:
   ```bash
   git clone [https://github.com/cassiorodri7-ai/Network-Telecom-Automations](https://github.com/cassiorodri7-ai/Network-Telecom-Automations)