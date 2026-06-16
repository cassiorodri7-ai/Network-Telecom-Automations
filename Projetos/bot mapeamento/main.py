import time
import random
import win32gui
import pyautogui

# ==========================================
# CONFIGURAÇÕES DE JANELA E MAPEAMENTO
# ==========================================
WINDOW_TITLE = "Task Bar Hero"

# Coordenadas relativas à área cliente (onde o jogo roda)
COORD_PORTAL_X = 64
COORD_PORTAL_Y = 239

COORD_ATO_X = 142
COORD_ATO_Y = 244

COORD_FASE_X = 188
COORD_FASE_Y = 244

# ==========================================
# FUNÇÕES CORE
# ==========================================

def encontrar_janela():
    """Busca o handle (hwnd) da janela do jogo."""
    hwnd = win32gui.FindWindow(None, WINDOW_TITLE)
    if not hwnd:
        print(f"Janela '{WINDOW_TITLE}' não encontrada!")
    return hwnd

def clicar_fisico(hwnd, rel_x, rel_y):
    """
    Traduz as coordenadas da tela interna (cliente) para a tela do monitor
    e simula um clique físico para burlar anti-cheats.
    """
    try:
        # Converter coordenadas cliente para coordenadas absolutas da tela
        abs_x, abs_y = win32gui.ClientToScreen(hwnd, (rel_x, rel_y))
        
        # Mover o mouse fisicamente
        pyautogui.moveTo(abs_x, abs_y, duration=0.2)
        time.sleep(random.uniform(0.1, 0.3))
        
        # Clique físico (simula pressionamento real de hardware)
        pyautogui.mouseDown()
        time.sleep(random.uniform(0.05, 0.15))
        pyautogui.mouseUp()
        
        print(f"Clique físico em: Absolute({abs_x}, {abs_y}) | Relative({rel_x}, {rel_y})")
        return True
    except Exception as e:
        print(f"Erro ao clicar: {e}")
        return False

def ativar_janela(hwnd):
    """Garante que a janela esteja focada e visível antes de clicar."""
    try:
        win32gui.ShowWindow(hwnd, 5) # 5 = SW_SHOW
        win32gui.SetForegroundWindow(hwnd)
        time.sleep(0.5)
        return True
    except Exception as e:
        print(f"Erro ao focar janela: {e}")
        return False

# ==========================================
# LÓGICA PRINCIPAL - LOOP 1-1
# ==========================================

def loop_basico_1_1():
    hwnd = encontrar_janela()
    if not hwnd:
        return
        
    print("Iniciando rotina de clique no Portal 1-1...")
    
    while True:
        if not ativar_janela(hwnd):
             print("Aguardando janela voltar a ficar disponível...")
             time.sleep(5)
             continue
             
        # Sequência de inicialização 1-1
        print("\n--- Novo Ciclo ---")
        
        # 1. Clicar no Portal
        clicar_fisico(hwnd, COORD_PORTAL_X, COORD_PORTAL_Y)
        time.sleep(random.uniform(1.0, 1.5))
        
        # 2. Clicar no Ato 1
        clicar_fisico(hwnd, COORD_ATO_X, COORD_ATO_Y)
        time.sleep(random.uniform(1.0, 1.5))
        
        # 3. Clicar na Fase 1
        clicar_fisico(hwnd, COORD_FASE_X, COORD_FASE_Y)
        
        # Intervalo de segurança antes do próximo ciclo
        espera = random.uniform(3.0, 5.0)
        print(f"Aguardando {espera:.2f} segundos...")
        time.sleep(espera)

if __name__ == "__main__":
    loop_basico_1_1()