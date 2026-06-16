import time
import win32gui
import win32api

WINDOW_TITLE = "Task Bar Hero"

def mapear_tela():
    print(f"Buscando janela: '{WINDOW_TITLE}'...")
    hwnd = win32gui.FindWindow(None, WINDOW_TITLE)

    if not hwnd:
        print("Janela não encontrada! Abra o jogo primeiro e rode este script novamente.")
        return

    print("\n✅ Janela encontrada!")
    print("Mova o mouse sobre os botões do jogo.")
    print("Os valores 'Relativos (CLIENTE)' são os que você deve colocar no script principal.")
    print("Pressione Ctrl+C no terminal para parar o mapeamento.\n")

    try:
        while True:
            # Pega a posição absoluta do mouse no monitor (hardware)
            abs_x, abs_y = win32api.GetCursorPos()

            try:
                # Converte a posição absoluta para a posição relativa dentro do jogo
                rel_x, rel_y = win32gui.ScreenToClient(hwnd, (abs_x, abs_y))

                # Atualiza a linha do terminal em tempo real
                print(f"\rMonitor Absoluto: ({abs_x:4}, {abs_y:4}) | Relativo (CLIENTE): X={rel_x:4}, Y={rel_y:4} ", end="")
            except Exception:
                # Evita erro caso o mouse saia completamente da área rastreável em alguns setups
                pass

            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\n\nMapeamento encerrado pelo usuário.")

if __name__ == "__main__":
    mapear_tela()