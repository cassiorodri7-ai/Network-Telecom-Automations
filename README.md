# 🌐 Network & Productivity Automation Suite

Bem-vindo ao meu portfólio de automações! Este repositório centraliza ferramentas desenvolvidas em Python para otimização de redes, produtividade operacional, gerenciamento de infraestrutura, análise de dados e Web Scraping.

## 🤖 Projetos Disponíveis

### 1. [🌐 NOC Automator](Projetos/bot_noc/)
Bot focado em operações de Network Operations Center (NOC).
- **Funcionalidades:** Gerenciamento inteligente de ONUs, integração com CRM para fechamento de chamados, busca de contingência por Serial Number e relatórios automatizados no Discord.
- **Tecnologias:** Selenium, Xshell, Python, Discord API.

### 2. [📡 Discord Ping Automator](Projetos/bot_ping/)
Ferramenta de diagnóstico de latência de rede.
- **Funcionalidades:** Disparo de testes de ping simultâneos para múltiplos IPs, organização visual automática de janelas de terminal na tela do monitor e exportação de logs de performance para arquivos `.txt`.
- **Tecnologias:** Subprocess, Asyncio, PyGetWindow.

### 3. [🖱️ TaskBarHero AutoClick](Projetos/autoclick_taskbarhero/)
Automação focada em produtividade e interface.
- **Funcionalidades:** Clique automatizado otimizado para o TaskBarHero, permitindo controle de fluxo de trabalho em ambientes de alta demanda e interação precisa com elementos de interface gráfica.
- **Tecnologias:** PyAutoGUI, OpenCV.

### 4. [🎥 GoPro Media Organizer](Projetos/organizador_gopro/)
Script de organização e limpeza de arquivos de mídia.
- **Funcionalidades:** Varredura de cartão SD, limpeza automática de arquivos temporários/lixo (`.lrv`, `.thm`) e organização inteligente de vídeos `.mp4` em pastas datadas.
- **Tecnologias:** Os, Shutil, Glob, Datetime.

### 5. [🖥️ Hardware Stress Monitor](Projetos/bot_monitoramento/)
Monitor de recursos de sistema em tempo real com alertas na nuvem.
- **Funcionalidades:** Leitura contínua de carga de CPU e uso de memória RAM, aplicando regras de negócio para disparar alertas críticos de estresse via Webhook para canais do Discord.
- **Tecnologias:** Psutil, Requests, Python-dotenv.

### 6. [📊 ECU Telemetry Analyzer](Projetos/analisador_telemetria/)
Analisador de dados e gerador de gráficos para telemetria automotiva.
- **Funcionalidades:** Processamento de planilhas pesadas (`.CSV`) extraídas de injeções programáveis, correlacionando RPM, Pressão de Turbo e Sonda Lambda na mesma linha do tempo para gerar painéis visuais de alta resolução.
- **Tecnologias:** Pandas, Matplotlib.

### 7. [🛒 Smart Budget Assistant API](Projetos/bot_whatsapp_orcamento/)
Servidor de Web Scraping para orçamentos e peças.
- **Funcionalidades:** API Flask projetada para receber requisições de Webhooks de mensagens (ex: WhatsApp), detectar URLs, contornar bloqueios anti-robô, extrair títulos e preços dinâmicos (Mercado Livre e Amazon) e salvar em uma planilha de controle unificada.
- **Tecnologias:** Flask, BeautifulSoup, Requests, Pandas, Expressões Regulares (RegEx).

---

## 🛠️ Tecnologias Utilizadas no Repositório
* **Linguagem:** Python 3.x
* **Versionamento:** Git & GitHub
* **Automação Web/Desktop:** Selenium, PyAutoGUI, PyGetWindow
* **Ciência de Dados & Gráficos:** Pandas, Matplotlib
* **Web Scraping & APIs:** Flask, BeautifulSoup4, Requests
* **Comunicação:** Integração via Webhooks e API do Discord

## 👨‍💻 Autor
**Cássio Corrêa**
- [GitHub](https://github.com/cassiorodri7-ai)
- [LinkedIn](https://www.linkedin.com/in/c%C3%A1ssio-rodrigues-708234214/)

---
*Este repositório é um portfólio em constante evolução. Sinta-se à vontade para explorar os diretórios e os manuais específicos de cada projeto.*