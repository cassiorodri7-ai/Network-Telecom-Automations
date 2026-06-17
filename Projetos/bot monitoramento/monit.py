import psutil
import requests
import time
import os
from datetime import datetime
from dotenv import load_dotenv

# Carrega a URL do Webhook escondida no .env
load_dotenv()
WEBHOOK_URL = os.getenv('WEBHOOK_DISCORD')

def enviar_alerta_discord(cpu_percent, ram_percent):
    """Monta a requisição e envia o alerta via Webhook para o Discord."""
    agora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    
    # Estrutura JSON padrão do Discord (Embed)
    mensagem = {
        "username": "Hardware Monitor",
        "embeds": [
            {
                "title": "⚠️ ALERTA DE CARGA CRÍTICA ⚠️",
                "description": "O uso do sistema ultrapassou os limites de segurança configurados.",
                "color": 16711680, # Cor vermelha em código decimal
                "fields": [
                    {"name": "Uso de CPU", "value": f"**{cpu_percent}%**", "inline": True},
                    {"name": "Uso de RAM", "value": f"**{ram_percent}%**", "inline": True},
                    {"name": "Horário", "value": agora, "inline": False}
                ]
            }
        ]
    }
    
    try:
        # Dispara o JSON para a API do Discord
        resposta = requests.post(WEBHOOK_URL, json=mensagem)
        if resposta.status_code == 204:
            print(f"[{agora}] Alerta enviado com sucesso para o Discord!")
        else:
            print(f"Falha ao enviar. Código de erro HTTP: {resposta.status_code}")
    except Exception as e:
        print(f"Erro crítico na conexão: {e}")

def iniciar_monitoramento(limite_cpu=85.0, limite_ram=90.0, intervalo_checagem=5):
    """Loop infinito que monitora o PC em segundo plano."""
    print(f"🛡️ Monitor de Hardware Ativo.")
    print(f"Limites de Alerta -> CPU: {limite_cpu}% | RAM: {limite_ram}%")
    print("Para parar, pressione Ctrl+C no terminal.\n")
    
    try:
        while True:
            # Coleta as métricas do SO
            cpu_atual = psutil.cpu_percent(interval=1)
            ram_atual = psutil.virtual_memory().percent
            
            print(f"Monitorando... CPU: {cpu_atual}% | RAM: {ram_atual}%", end="\r")
            
            # Valida as regras de negócio (limites de segurança)
            if cpu_atual >= limite_cpu or ram_atual >= limite_ram:
                print(f"\n🚨 LIMITE EXCEDIDO! Disparando alerta...")
                enviar_alerta_discord(cpu_atual, ram_atual)
                
                # Pausa o monitoramento por 60 segundos após um alerta para evitar spam de mensagens
                print("Aguardando 60 segundos para retomar a varredura...\n")
                time.sleep(60)
            else:
                # Aguarda o intervalo padrão e repete o loop
                time.sleep(intervalo_checagem)
                
    except KeyboardInterrupt:
        print("\n\n⏹️ Monitoramento encerrado pelo usuário.")

if __name__ == "__main__":
    if not WEBHOOK_URL:
        print("Erro: WEBHOOK_DISCORD não foi encontrado. Verifique seu arquivo .env")
    else:
        # Você pode alterar os limites aqui embaixo para testar mais fácil (Ex: limite_cpu=10.0)
        iniciar_monitoramento(limite_cpu=85.0, limite_ram=90.0)