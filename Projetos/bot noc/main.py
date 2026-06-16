import os
from dotenv import load_dotenv
import time
import re
import asyncio
import discord
from discord.ext import commands
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pyautogui
import pygetwindow as gw
import pyperclip
from datetime import datetime, timedelta

robo_rodando = False

def executar_fluxo_completo_integrado(viki_email, viki_senha, olt_user, olt_pass):
    global robo_rodando
    robo_rodando = True
    
    options = Options()
    options.binary_location = r"C:\Users\cassio.correa\AppData\Local\BraveSoftware\Brave-Browser\Application\brave.exe"
    options.add_argument(r"--user-data-dir=C:\Users\cassio.correa\AppData\Local\BraveSoftware\Brave-Browser\User Data Robô NOC")
    options.add_argument(r"--profile-directory=PerfilAutomacaoBrave")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument("--disable-blink-features=AutomationControlled")

    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 20)

    abas_abertas = driver.window_handles
    if len(abas_abertas) > 1:
        for aba in abas_abertas[1:]:
            driver.switch_to.window(aba)
            driver.close()
            
    driver.switch_to.window(driver.window_handles[0])
    aba_viki_home = driver.current_window_handle

    contratos_removidos = []
    contratos_nao_encontrados = []
    chamados_processados = set()

    url_acompanhar = "https://viki.gigalink.net.br/chamados/chamados/acompanhar?commit=Filtrar+Chamados&setor_id=38&categoria_id=419&status=&unidade_id=&bairro=+&area_id=&celula_id=&funcionario_id=&setor_origem=&setor_anterior=&agendamento="

    try:
        driver.get(url_acompanhar)
        time.sleep(4)

        if "entrar" in driver.current_url or "login" in driver.current_url:
            campo_email = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@type='email' or @name='email' or @placeholder='E-mail']")))
            campo_email.clear()
            campo_email.send_keys(viki_email)

            campo_senha = driver.find_element(By.XPATH, "//input[@type='password' or @name='password' or @placeholder='Senha']")
            campo_senha.clear()
            campo_senha.send_keys(viki_senha)

            try:
                botao_viki_entrar = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Entrar')] | //input[@value='Entrar']")))
                driver.execute_script("arguments[0].click();", botao_viki_entrar)
            except:
                campo_senha.send_keys(Keys.RETURN)

            WebDriverWait(driver, 25).until(lambda d: "entrar" not in d.current_url and "login" not in d.current_url)
            driver.get(url_acompanhar)
            time.sleep(4)

        driver.execute_script("window.open('https://gigalink.oltcloud.co/onu/device/buscar', '_blank');")
        aba_olt = driver.window_handles[-1]
        driver.switch_to.window(aba_olt)
        time.sleep(4)

        if "login" in driver.current_url or "entrar" in driver.current_url or len(driver.find_elements(By.XPATH, "//button[contains(text(),'Entrar')] | //input[@value='Entrar']")) > 0:
            try:
                campo_user_olt = driver.find_element(By.XPATH, "//input[@type='text' or @name='username' or @placeholder='Usuário']")
                campo_user_olt.clear()
                campo_user_olt.send_keys(olt_user)

                campo_pass_olt = driver.find_element(By.XPATH, "//input[@type='password' or @name='password' or @placeholder='Senha']")
                campo_pass_olt.clear()
                campo_pass_olt.send_keys(olt_pass)

                check_cookies = driver.find_elements(By.XPATH, "//input[@type='checkbox']")
                if check_cookies and not check_cookies[0].is_selected():
                    driver.execute_script("arguments[0].click();", check_cookies[0])

                botao_entrar_olt = driver.find_element(By.XPATH, "//button[contains(text(),'Entrar')] | //input[@value='Entrar']")
                driver.execute_script("arguments[0].click();", botao_entrar_olt)
                time.sleep(5)
                driver.get("https://gigalink.oltcloud.co/onu/device/buscar")
                time.sleep(3)
            except Exception:
                pass

        while robo_rodando:
            driver.switch_to.window(aba_viki_home)
            
            botao_filtrar = wait.until(EC.presence_of_element_located((By.XPATH, "//*[@type='submit' and contains(@value, 'Filtrar')] | //button[contains(text(), 'Filtrar')] | //input[contains(@value, 'Filtrar')]")))
            driver.execute_script("arguments[0].click();", botao_filtrar)
            time.sleep(5)

            link_chamado_alvo = None
            linhas_tabela = driver.find_elements(By.XPATH, "//tbody/tr")

            for linha in linhas_tabela:
                try:
                    if "Designado" in linha.text:
                        botao_visualizar = linha.find_element(By.XPATH, ".//a[contains(translate(., 'VISUALIZAR', 'visualizar'), 'visualizar') or contains(@class, 'btn')]")
                        link_temp = botao_visualizar.get_attribute("href")
                        if link_temp not in chamados_processados:
                            link_chamado_alvo = link_temp
                            chamados_processados.add(link_chamado_alvo)
                            break
                except Exception:
                    continue

            if not link_chamado_alvo:
                break

            driver.execute_script(f"window.open('{link_chamado_alvo}', '_blank');")
            aba_ticket = driver.window_handles[-1]
            driver.switch_to.window(aba_ticket)
            time.sleep(4)

            texto_contrato = wait.until(EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'icone-tipo-produto') or contains(., 'Contrato:')]"))).text
            id_contrato = texto_contrato.split("Contrato:")[1].split("/")[0].strip()

            texto_area = wait.until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Área:')]"))).text
            area_cliente = texto_area.split("Área:")[1].split("Célula:")[0].strip()

            texto_total_chamado = wait.until(EC.presence_of_element_located((By.TAG_NAME, "body"))).text.lower()

            try:
                texto_unidade = driver.find_element(By.XPATH, "//*[contains(text(), 'Unidade:')]").text
                unidade_cliente = texto_unidade.split("Unidade:")[1].split("\n")[0].strip()
            except:
                unidade_cliente = "Nao_Identificada"

            ir_para_olt = False
            areas_olt = ["ACB", "ARBU", "TRL", "CBF", "RASA", "PSA", "RSM", "RMS", "CPA", "OLA"]

            if area_cliente in areas_olt:
                ir_para_olt = True

            if not ir_para_olt:
                if unidade_cliente in ["Nova Friburgo", "Nova Friburgo 2"]:
                    bairros_olt_nof = [
                        "olaria", "cascatinha", "cônego", "conego", "bela vista", "parque são clemente", "parque sao clemente", "vargem grande",
                        "centro", "braunes", "cordoeira", "village", "general osório", "general osorio",
                        "ponte da saudade", "ponte das saudades", "parque dom joão vi", "parque dom joao vi", "parque imperial", "ypu", "catarcione",
                        "conselheiro paulino", "conselheiro", "são jorge", "sao jorge", "santa teresinha", "maria teresa", "sao pedro da serra"
                    ]
                    if any(bairro in texto_total_chamado for bairro in bairros_olt_nof):
                        ir_para_olt = True
                else:
                    cidades_olt_outras = ["cabo frio", "armação de búzios", "armacao de buzios", "araruama", "rasa"]
                    if any(cidade in texto_total_chamado for cidade in cidades_olt_outras):
                        ir_para_olt = True

            sucesso_remocao = False
            texto_comentario = ""
            interface_xshell = ""
            janela_xshell_alvo = None
            alvo_olt = id_contrato

            if ir_para_olt:
                driver.switch_to.window(aba_olt)
                driver.get("https://gigalink.oltcloud.co/onu/device/buscar")
                time.sleep(3)
                
                try:
                    btn_limpar = driver.find_element(By.XPATH, "//button[contains(@class, 'btn-danger') or .//i[contains(@class, 'eraser')]] | //a[contains(@class, 'btn-danger')]")
                    driver.execute_script("arguments[0].click();", btn_limpar)
                    time.sleep(2)
                except:
                    pass

                campo_descricao = wait.until(EC.presence_of_element_located((By.XPATH, "//*[@placeholder='Descrição' or @name='description' or @id='description' or @type='search']")))
                campo_descricao.clear()
                campo_descricao.send_keys(id_contrato)
                campo_descricao.send_keys(Keys.RETURN)
                time.sleep(5)

                try:
                    linha_cliente = driver.find_element(By.XPATH, f"//tbody/tr[td[contains(., '{id_contrato}')]]")
                    colunas = linha_cliente.find_elements(By.TAG_NAME, "td")
                    if len(colunas) >= 9:
                        olt_texto = colunas[5].text.strip()
                        spo_texto = colunas[6].text.strip()
                        sn_texto = colunas[7].text.strip()
                        modelo_texto = colunas[8].text.strip()
                        texto_comentario = f"{id_contrato}\n{olt_texto}\n{spo_texto} {sn_texto} {modelo_texto}"
                        sucesso_remocao = True
                    else:
                        raise Exception("Formato invalido")
                except Exception:
                    driver.switch_to.window(aba_ticket)
                    time.sleep(1)
                    try:
                        link_cliente = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, '/clientes/') or contains(@href, '/crm/')] | //strong[contains(text(), 'Cliente')]/following-sibling::a")))
                        url_cliente = link_cliente.get_attribute("href")
                        driver.execute_script(f"window.open('{url_cliente}', '_blank');")
                        aba_cliente = driver.window_handles[-1]
                        driver.switch_to.window(aba_cliente)
                        time.sleep(4)

                        btn_comodato = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(translate(text(), 'COMODATO', 'comodato'), 'comodato') or contains(translate(text(), 'ESTOQUE', 'estoque'), 'estoque')]")))
                        driver.execute_script("arguments[0].click();", btn_comodato)
                        time.sleep(3)

                        sn_encontrado = ""
                        try:
                            sn_elemento = driver.find_element(By.XPATH, f"//*[contains(text(), '{id_contrato}')]/following::tr[1]/td[3] | //*[contains(text(), '{id_contrato}')]/following::table[1]//tbody/tr[1]/td[3]")
                            sn_encontrado = sn_elemento.text.strip()
                        except:
                            pass

                        driver.close()
                        
                        if sn_encontrado:
                            driver.switch_to.window(aba_olt)
                            time.sleep(1)
                            try:
                                btn_limpar_sn = driver.find_element(By.XPATH, "//button[contains(@class, 'btn-danger') or .//i[contains(@class, 'eraser')]] | //a[contains(@class, 'btn-danger')]")
                                driver.execute_script("arguments[0].click();", btn_limpar_sn)
                                time.sleep(2)
                            except:
                                pass
                                
                            campo_sn = wait.until(EC.presence_of_element_located((By.XPATH, "//input[contains(@placeholder, 'SN') or contains(@name, 'sn') or contains(@name, 'serial')]")))
                            campo_sn.clear()
                            campo_sn.send_keys(sn_encontrado)
                            campo_sn.send_keys(Keys.RETURN)
                            time.sleep(5)
                            
                            try:
                                linha_cliente_sn = driver.find_element(By.XPATH, f"//tbody/tr[td[contains(., '{sn_encontrado}')]]")
                                colunas_sn = linha_cliente_sn.find_elements(By.TAG_NAME, "td")
                                if len(colunas_sn) >= 9:
                                    olt_texto = colunas_sn[5].text.strip()
                                    spo_texto = colunas_sn[6].text.strip()
                                    sn_texto = colunas_sn[7].text.strip()
                                    modelo_texto = colunas_sn[8].text.strip()
                                    texto_comentario = f"{id_contrato}\n{olt_texto}\n{spo_texto} {sn_texto} {modelo_texto}"
                                    sucesso_remocao = True
                                    alvo_olt = sn_encontrado
                                else:
                                    texto_comentario = "ONU/ONT Não encontrada"
                            except:
                                texto_comentario = "ONU/ONT Não encontrada"
                        else:
                            texto_comentario = "ONU/ONT Não encontrada"
                    except:
                        if len(driver.window_handles) > 3:
                            driver.close()
                        texto_comentario = "ONU/ONT Não encontrada"
            
            else:
                pasta_final = ""
                sigla_final = "BUSCA_GERAL"

                mapa_pastas_base = {
                    "Nova Friburgo": "Nova Friburgo", "Nova Friburgo 2": "Nova Friburgo", "Bonsucesso": "Bonsucesso",
                    "Campos": "Campos", "Cantagalo": "Cantagalo", "Carapebus": "Carapebus",
                    "Casimiro de Abreu": "Casimiro de Abreu", "Cordeiro": "Cordeiro", "Macaé": "Macaé",
                    "Niterói": "Niterói", "Praia Seca": "Praia Seca", "Quissamã": "Quissamã",
                    "Rios das Ostras": "Rios das Ostras", "Vargem Grande": "Vargem Grande", "Araruama": "Araruama",
                    "Búzios": "Búzios", "Cabo Frio": "Cabo Frio", "São Pedro da Aldeia": "São Pedro da Aldeia", "Teresópolis": "Teresópolis"
                }

                dicionario_global = {
                    "Campos": {
                        "centro": "CPS", "parque guarus": "CPS", "jardim carioca": "CPS", "parque bandeirantes": "CPS",
                        "parque rosário": "CPS", "parque rosario": "CPS", "parque são caetano": "CPS", "parque sao caetano": "CPS",
                        "parque joão maria": "CPS", "parque joao maria": "CPS", "parque aurora": "CPS", "parque corrientes": "CPS",
                        "parque tarcísio miranda": "CPS", "parque tarcisio miranda": "CPS", "parque turf club": "CPS", "turf club": "CPS",
                        "parque dos rodoviários": "CPS", "parque dos rodoviarios": "CPS", "parque santo amaro": "CPS", "parque são clemente": "CPS",
                        "parque sao clemente": "CPS", "parque tamandaré": "CPS", "parque tamandare": "CPS", "parque pelinca": "CPS", "pelinca": "CPS",
                        "parque leopoldina": "CPS", "caju": "CPS", "parque são domingos": "CPS", "parque sao domingos": "CPS", "ips": "CPS",
                        "farol de são thomé": "FDST", "farol de sao thome": "FDST", "xexé": "FDST", "xexe": "FDST", "vila do sol": "FDST",
                        "lagamar": "FDST", "rádio velho": "FDST", "radio velho": "FDST", "náutico": "FDST", "nautico": "FDST"
                    },
                    "Cantagalo": {
                        "centro": "CTAF", "rocha leão": "CTAF", "rocha leao": "CTAF"
                    },
                    "Carapebus": {
                        "centro": "CRPB", "carapebus": "CRPB"
                    },
                    "Casimiro de Abreu": {
                        "centro": "CBU", "casimiro de abreu": "CBU"
                    },
                    "Cordeiro": {
                        "centro": "CDI", "cordeiro": "CDI"
                    },
                    "Macaé": {
                        "centro": "MAC", "macaé": "MAC", "macae": "MAC", "zen": "MAC"
                    },
                    "Praia Seca": {
                        "caiçara": "PRSE", "caicara": "PRSE", "praia seca": "PRSE", "centro": "PRSE"
                    },
                    "Quissamã": {
                        "quissamã": "QUI", "quissama": "QUI", "centro": "QUI"
                    },
                    "Rios das Ostras": {
                        "nova esperança": "NSP", "nova esperanca": "NSP", "recanto": "RSC"
                    },
                    "Vargem Grande": {
                        "vargem grande": "VGA", "centro": "VGA", "janela das andorinhas": "JAD"
                    },
                    "Nova Friburgo": {
                        "conquista": "COTS", "amparo": "AMP", "são geraldo": "DPE", "sao geraldo": "DPE",
                        "córrego dantas": "DPE", "corrego dantas": "DPE", "chácara do paraíso": "DPE", "chacara do paraiso": "DPE",
                        "loteamento jacina": "DPE", "jacina": "DPE", "rui sanglard": "DPE", "prado": "DPE", "duas pedras": "DPE",
                        "galdinópolis": "GAD", "galdinopolis": "GAD", "jardim ouro preto": "JAD", "lumiar": "LUMA", "macaé de cima": "MDC",
                        "macae de cima": "MDC", "mury": "MRY", "debossan": "MRY", "theodoro": "MRY", "nibra": "NBR", "nova suíça": "NSU",
                        "nova suica": "NSU", "nova suiça": "NSU", "são pedro da serra": "SPS", "sao pedro da serra": "SPS", "varginha": "VAR"
                    }
                }

                if any(exc in texto_total_chamado for exc in ["caiçara", "caicara"]):
                    pasta_final, sigla_final = "Praia Seca", "PRSE"
                elif any(exc in texto_total_chamado for exc in ["farol de são thomé", "farol de sao thome"]):
                    pasta_final, sigla_final = "Campos", "FDST"
                else:
                    pasta_final = mapa_pastas_base.get(unidade_cliente, unidade_cliente)
                    chave_cidade = "Nova Friburgo" if unidade_cliente == "Nova Friburgo 2" else unidade_cliente

                    if chave_cidade in dicionario_global:
                        for bairro, sigla in dicionario_global[chave_cidade].items():
                            if bairro in texto_total_chamado:
                                sigla_final = sigla
                                break

                try:
                    janelas_xshell = gw.getWindowsWithTitle("Xshell")
                    if len(janelas_xshell) > 0:
                        janela_xshell_alvo = janelas_xshell[0]
                        
                        if janela_xshell_alvo.isMinimized:
                            janela_xshell_alvo.restore()
                            time.sleep(0.5)
                        
                        pyautogui.press('alt')
                        time.sleep(0.2)
                        janela_xshell_alvo.activate()
                        time.sleep(1)
                        
                        centro_x = janela_xshell_alvo.left + (janela_xshell_alvo.width // 2)
                        inferior_y = janela_xshell_alvo.top + janela_xshell_alvo.height - 150
                        centro_terminal_y = janela_xshell_alvo.top + (janela_xshell_alvo.height // 2)
                        
                        pyautogui.click(centro_x, inferior_y)
                        time.sleep(1)

                        pyautogui.hotkey('alt', 'o')
                        time.sleep(1.5)
                        
                        janelas_sessoes = gw.getWindowsWithTitle("Sessões")
                        if len(janelas_sessoes) > 0:
                            js_win = janelas_sessoes[0]
                            
                            btn_voltar_x = js_win.left + js_win.width - 45
                            btn_voltar_y = js_win.top + 73
                            
                            search_x = js_win.left + js_win.width - 150
                            search_y = js_win.top + 45
                            
                            primeiro_item_x = js_win.left + 150
                            primeiro_item_y = js_win.top + 135

                            pyautogui.moveTo(btn_voltar_x, btn_voltar_y, duration=0.3)
                            for _ in range(4):
                                pyautogui.click()
                                time.sleep(0.3)

                            pyautogui.moveTo(search_x, search_y, duration=0.2)
                            pyautogui.click()
                            pyautogui.hotkey('ctrl', 'a')
                            pyautogui.press('backspace')
                            pyautogui.write("OLTs Parks", interval=0.05)
                            time.sleep(1)
                            
                            pyautogui.moveTo(primeiro_item_x, primeiro_item_y, duration=0.2)
                            pyautogui.click()
                            time.sleep(0.2)
                            pyautogui.press('enter')
                            time.sleep(1)
                            
                            pyautogui.moveTo(search_x, search_y, duration=0.2)
                            pyautogui.click()
                            pyautogui.hotkey('ctrl', 'a')
                            pyautogui.press('backspace')
                            pyautogui.write(pasta_final, interval=0.05)
                            time.sleep(1)
                            
                            pyautogui.moveTo(primeiro_item_x, primeiro_item_y, duration=0.2)
                            pyautogui.click()
                            time.sleep(0.2)
                            pyautogui.press('down')
                            time.sleep(0.2)
                            pyautogui.press('enter')
                            time.sleep(1)
                            
                            pyautogui.moveTo(search_x, search_y, duration=0.2)
                            pyautogui.click()
                            pyautogui.hotkey('ctrl', 'a')
                            pyautogui.press('backspace')
                            pyautogui.write(sigla_final, interval=0.05)
                            time.sleep(1)
                            
                            pyautogui.moveTo(primeiro_item_x, primeiro_item_y, duration=0.2)
                            pyautogui.click()
                            time.sleep(0.2)
                            pyautogui.press('down')
                            time.sleep(0.2)
                            pyautogui.press('enter')
                            
                            time.sleep(8)

                        comando_final = f'show gpon onu {id_contrato} summary'
                        pyautogui.write(comando_final, interval=0.05)
                        time.sleep(0.5)
                        pyautogui.press('enter')
                        time.sleep(4)

                        pyperclip.copy("") 
                        canto_inf_dir_x = janela_xshell_alvo.left + janela_xshell_alvo.width - 50
                        canto_inf_dir_y = janela_xshell_alvo.top + janela_xshell_alvo.height - 50
                        canto_sup_esq_x = janela_xshell_alvo.left + 50
                        canto_sup_esq_y = janela_xshell_alvo.top + 80 

                        pyautogui.moveTo(canto_inf_dir_x, canto_inf_dir_y)
                        pyautogui.dragTo(canto_sup_esq_x, canto_sup_esq_y, duration=1.5, button='left')
                        time.sleep(0.5)
                        pyautogui.hotkey('ctrl', 'shift', 'c')
                        time.sleep(1)
                        pyautogui.click(centro_x, centro_terminal_y)
                        
                        texto_terminal = pyperclip.paste()
                        olt_prompt = "Nao_identificado#"
                        matches_prompt = re.findall(r'([A-Za-z0-9\-\_]+#)', texto_terminal)
                        if matches_prompt:
                            olt_prompt = matches_prompt[-1]
                            
                        bloco_resultado = texto_terminal
                        if comando_final in texto_terminal:
                            bloco_resultado = texto_terminal.split(comando_final)[-1]

                        linhas_importantes = []
                        palavras_chave = ['index', 'interface', 'serial', 'alias', 'model']
                        
                        for linha in bloco_resultado.split('\n'):
                            linha_lower = linha.lower()
                            if any(palavra in linha_lower for palavra in palavras_chave):
                                linhas_importantes.append(linha.strip())

                        if len(linhas_importantes) > 0:
                            texto_comentario_base = f"{id_contrato}\n{olt_prompt}\n" + "\n".join(linhas_importantes)
                        else:
                            texto_comentario_base = "ONU/ONT Não encontrada"

                        interface_xshell = ""
                        
                        interface_match = re.search(r'gpon\d+/\d+', texto_terminal, re.IGNORECASE)
                        if interface_match:
                            interface_xshell = interface_match.group(0)
                        
                        if not interface_xshell:
                            for linha in bloco_resultado.split('\n'):
                                linha_lower = linha.lower()
                                if "interface" in linha_lower and ":" in linha:
                                    interface_xshell = linha.split(":")[1].strip()

                        if interface_xshell:
                            pyautogui.write("configure terminal", interval=0.05)
                            pyautogui.press('enter')
                            time.sleep(2)

                            sucesso_if = False
                            tentativas = 0
                            while not sucesso_if and tentativas < 3:
                                pyautogui.write(f"interface {interface_xshell}", interval=0.05)
                                pyautogui.press('enter')
                                time.sleep(2)
                                pyperclip.copy("")
                                pyautogui.moveTo(canto_inf_dir_x, canto_inf_dir_y)
                                pyautogui.dragTo(canto_sup_esq_x, canto_sup_esq_y, duration=1.0, button='left')
                                time.sleep(0.5)
                                pyautogui.hotkey('ctrl', 'shift', 'c')
                                time.sleep(1)
                                pyautogui.click(centro_x, centro_terminal_y)
                                texto_verificacao = pyperclip.paste()
                                linhas_ver = [l.strip() for l in texto_verificacao.split('\n') if l.strip()]
                                
                                if len(linhas_ver) > 0:
                                    ultima_linha = linhas_ver[-1]
                                    if "(config-if)#" in ultima_linha:
                                        sucesso_if = True
                                    else:
                                        pyautogui.press('backspace', presses=20, interval=0.01)
                                tentativas += 1

                            if sucesso_if:
                                pyautogui.write("show this", interval=0.05)
                                pyautogui.press('enter')
                                time.sleep(2)
                                
                                pyperclip.copy("")
                                pyautogui.moveTo(canto_inf_dir_x, canto_inf_dir_y)
                                pyautogui.dragTo(canto_sup_esq_x, canto_sup_esq_y, duration=1.0, button='left')
                                time.sleep(0.5)
                                pyautogui.hotkey('ctrl', 'shift', 'c')
                                time.sleep(1)
                                pyautogui.click(centro_x, centro_terminal_y)
                                
                                texto_show_this = pyperclip.paste()
                                
                                if id_contrato in texto_show_this:
                                    comandos_finais = [
                                        f"no onu {id_contrato}",
                                        "end",
                                        "copy r s"
                                    ]
                                    for cmd in comandos_finais:
                                        pyautogui.write(cmd, interval=0.05)
                                        pyautogui.press('enter')
                                        time.sleep(2)
                                    sucesso_remocao = True
                                    texto_comentario = texto_comentario_base
                                else:
                                    pyautogui.write("end", interval=0.05)
                                    pyautogui.press('enter')
                                    texto_comentario = "ONU/ONT Não encontrada na interface especificada."
                            else:
                                texto_comentario = "Falha ao entrar na interface."
                        else:
                            texto_comentario = "ONU/ONT Não encontrada"
                    else:
                        texto_comentario = "ONU/ONT Não encontrada (Xshell fechado)"
                except Exception:
                    texto_comentario = "ONU/ONT Não encontrada"

            driver.switch_to.window(aba_ticket)
            time.sleep(2)

            try:
                campo_observacao = wait.until(EC.presence_of_element_located((By.XPATH, "//textarea[contains(@name, 'descricao') or contains(@id, 'descricao') or contains(@class, 'descricao') or contains(@name, 'observacao') or contains(@id, 'observacao')] | //textarea")))
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", campo_observacao)
                time.sleep(1)
                campo_observacao.click()
                campo_observacao.clear()
                campo_observacao.send_keys(texto_comentario)
                time.sleep(1)
                botao_enviar = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Enviar') or contains(text(), 'Salvar')] | //input[@value='Enviar' or @value='Salvar']")))
                driver.execute_script("arguments[0].click();", botao_enviar)
                time.sleep(5)
            except Exception:
                pass

            if sucesso_remocao:
                if ir_para_olt:
                    driver.switch_to.window(aba_olt)
                    time.sleep(2)
                    try:
                        linha_cliente_atualizada = driver.find_element(By.XPATH, f"//tbody/tr[td[contains(., '{alvo_olt}')]]")
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", linha_cliente_atualizada)
                        time.sleep(1.5)
                        botoes_acao = linha_cliente_atualizada.find_elements(By.XPATH, ".//td[last()]//a | .//td[last()]//button")
                        if botoes_acao:
                            driver.execute_script("arguments[0].click();", botoes_acao[0])
                        else:
                            botao_info_fallback = linha_cliente_atualizada.find_element(By.XPATH, ".//td[last()]//*[contains(@class, 'info')]")
                            driver.execute_script("arguments[0].click();", botao_info_fallback)
                        
                        wait.until(EC.presence_of_element_located((By.XPATH, "//*[contains(translate(text(), 'INFORMAÇÕES', 'informações'), 'informações') or contains(translate(text(), 'EQUIPAMENTO', 'equipamento'), 'equipamento')]")))
                        time.sleep(3)

                        script_desautorizar = """
                        var botoes = document.querySelectorAll('button, a, .btn');
                        for (var i = 0; i < botoes.length; i++) {
                            if (botoes[i].innerText.toUpperCase().includes('DESAUTORIZAR') && botoes[i].offsetParent !== null) {
                                botoes[i].click();
                                return true;
                            }
                        }
                        return false;
                        """
                        tempo_limite = time.time() + 10
                        while time.time() < tempo_limite:
                            if driver.execute_script(script_desautorizar):
                                break
                            time.sleep(1)
                        time.sleep(3)

                        script_sim = """
                        var elements = document.querySelectorAll('.ui.positive.button, .btn, button, div.button');
                        for (var i = 0; i < elements.length; i++) {
                            var text = elements[i].textContent || elements[i].innerText;
                            if (text.trim().toUpperCase() === 'SIM' || text.trim().toUpperCase().includes('SIM')) {
                                if (elements[i].offsetWidth > 0 && elements[i].offsetHeight > 0) {
                                    elements[i].click();
                                    return true;
                                }
                            }
                        }
                        return false;
                        """
                        tempo_limite_sim = time.time() + 10
                        sucesso_sim = False
                        while time.time() < tempo_limite_sim:
                            if driver.execute_script(script_sim):
                                sucesso_sim = True
                                break
                            time.sleep(1)
                        
                        if not sucesso_sim:
                            try:
                                pyautogui.press('enter')
                                time.sleep(1)
                            except:
                                pass
                        time.sleep(4)
                    except Exception:
                        pass
                else:
                    if janela_xshell_alvo and interface_xshell:
                        try:
                            janela_xshell_alvo.activate()
                            time.sleep(1)
                            pyautogui.click(centro_x, centro_terminal_y)
                            time.sleep(1)
                            pyautogui.write("configure terminal", interval=0.05)
                            pyautogui.press('enter')
                            time.sleep(2)

                            sucesso_if = False
                            tentativas = 0
                            while not sucesso_if and tentativas < 3:
                                pyautogui.write(f"interface {interface_xshell}", interval=0.05)
                                pyautogui.press('enter')
                                time.sleep(2)
                                pyperclip.copy("")
                                pyautogui.moveTo(canto_inf_dir_x, canto_inf_dir_y)
                                pyautogui.dragTo(canto_sup_esq_x, canto_sup_esq_y, duration=1.0, button='left')
                                time.sleep(0.5)
                                pyautogui.hotkey('ctrl', 'shift', 'c')
                                time.sleep(1)
                                pyautogui.click(centro_x, centro_terminal_y)
                                texto_verificacao = pyperclip.paste()
                                linhas_ver = [l.strip() for l in texto_verificacao.split('\n') if l.strip()]
                                if len(linhas_ver) > 0:
                                    ultima_linha = linhas_ver[-1]
                                    if "(config-if)#" in ultima_linha:
                                        sucesso_if = True
                                    else:
                                        pyautogui.press('backspace', presses=20, interval=0.01)
                                tentativas += 1

                            if sucesso_if:
                                comandos_finais = [
                                    f"no onu {id_contrato}",
                                    "end",
                                    "copy r s"
                                ]
                                for cmd in comandos_finais:
                                    pyautogui.write(cmd, interval=0.05)
                                    pyautogui.press('enter')
                                    time.sleep(2)
                        except Exception:
                            pass

            driver.switch_to.window(aba_ticket)
            time.sleep(3)

            try:
                aba_resolver = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(translate(., 'RESOLVER', 'resolver'), 'resolver') or contains(@href, '#resolver')]")))
                driver.execute_script("arguments[0].click();", aba_resolver)
                time.sleep(3)

                js_select_opcao = """
                var selectElement = document.evaluate(arguments[0], document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
                if(selectElement) {
                    for(var i=0; i<selectElement.options.length; i++) {
                        if(selectElement.options[i].text.includes(arguments[1])) {
                            selectElement.selectedIndex = i;
                            selectElement.dispatchEvent(new Event('change', { bubbles: true }));
                            return true;
                        }
                    }
                }
                return false;
                """

                xpath_categoria = "//select[contains(@name, 'categoria') or contains(@id, 'categoria')]"
                if not driver.execute_script(js_select_opcao, xpath_categoria, "Remoção de configurações OLT - Cancelado"):
                    try:
                        campo_cat_input = driver.find_element(By.XPATH, "//*[contains(@class, 'categoria')]//input | //input[contains(@name, 'categoria')]")
                        campo_cat_input.send_keys("Remoção de configurações OLT - Cancelado")
                        time.sleep(1)
                        campo_cat_input.send_keys(Keys.RETURN)
                    except:
                        pass
                time.sleep(1)

                motivo_texto = "Realizado com sucesso" if sucesso_remocao else "Não realizado"
                xpath_motivo = "//select[contains(@name, 'motivo') or contains(@id, 'motivo')]"
                
                if not driver.execute_script(js_select_opcao, xpath_motivo, motivo_texto):
                    try:
                        motivo_dropdown = driver.find_element(By.XPATH, "//*[contains(@class, 'motivo')] | //div[contains(@class, 'motivo')]")
                        driver.execute_script("arguments[0].click();", motivo_dropdown)
                        time.sleep(1)
                        opcao_motivo = driver.find_element(By.XPATH, f"//div[contains(@class, 'item') and contains(text(), '{motivo_texto}')] | //option[contains(text(), '{motivo_texto}')]")
                        driver.execute_script("arguments[0].click();", opcao_motivo)
                    except:
                        try:
                            campo_mot_input = driver.find_element(By.XPATH, "//*[contains(@class, 'motivo')]//input | //input[contains(@name, 'motivo')]")
                            campo_mot_input.send_keys(Keys.CONTROL, 'a')
                            campo_mot_input.send_keys(Keys.BACKSPACE)
                            campo_mot_input.send_keys(motivo_texto)
                            time.sleep(1)
                            campo_mot_input.send_keys(Keys.RETURN)
                        except:
                            pass
                time.sleep(1)

                botao_enviar_resolver = driver.find_element(By.XPATH, "//div[contains(@id, 'resolver')]//button[contains(text(), 'Enviar')] | //div[contains(@id, 'resolver')]//input[@value='Enviar'] | //button[contains(translate(., 'ENVIAR', 'enviar'), 'enviar')]")
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", botao_enviar_resolver)
                time.sleep(1)
                driver.execute_script("arguments[0].click();", botao_enviar_resolver)
                time.sleep(5)

                if sucesso_remocao:
                    contratos_removidos.append(id_contrato)
                else:
                    contratos_nao_encontrados.append(id_contrato)

            except Exception:
                contratos_nao_encontrados.append(id_contrato + " (Erro Sistêmico)")

            driver.switch_to.window(aba_ticket)
            driver.close()
            time.sleep(2)

    except Exception:
        pass
        
    finally:
        try:
            driver.quit()
        except:
            pass
            
        return contratos_removidos, contratos_nao_encontrados

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=".", intents=intents)

@bot.command()
async def rodar_noc(ctx):
    global robo_rodando
    
    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    try:
        await ctx.message.delete()
    except:
        pass

    prompt1 = await ctx.send("Email de login Viki:")
    msg1 = await bot.wait_for('message', check=check)
    viki_email = msg1.content
    try:
        await prompt1.delete()
        await msg1.delete()
    except:
        pass

    prompt2 = await ctx.send("Senha Viki:")
    msg2 = await bot.wait_for('message', check=check)
    viki_senha = msg2.content
    try:
        await prompt2.delete()
        await msg2.delete()
    except:
        pass

    prompt3 = await ctx.send("Login OLT Cloud:")
    msg3 = await bot.wait_for('message', check=check)
    olt_user = msg3.content
    try:
        await prompt3.delete()
        await msg3.delete()
    except:
        pass

    prompt4 = await ctx.send("Senha OLT Cloud:")
    msg4 = await bot.wait_for('message', check=check)
    olt_pass = msg4.content
    try:
        await prompt4.delete()
        await msg4.delete()
    except:
        pass

    try:
        primeiro_nome = viki_email.split('@')[0].split('.')[0].capitalize()
    except:
        primeiro_nome = "Operador"
    
    status_msg = await ctx.send(f"👤 **Conectado Como:** {primeiro_nome}\n⚙️ **Status:** Trabalhando nas remoções...")

    start_time = datetime.now()
    
    loop = asyncio.get_running_loop()
    removidos, nao_encontrados = await loop.run_in_executor(None, executar_fluxo_completo_integrado, viki_email, viki_senha, olt_user, olt_pass)
    
    robo_rodando = False
    end_time = datetime.now()
    tempo_rodagem = end_time - start_time
    tempo_formatado = str(tempo_rodagem).split('.')[0]
    
    data_remocao = start_time.strftime("%d/%m/%Y")
    proxima_remocao = (start_time + timedelta(days=1)).strftime("%d/%m/%Y")

    if len(removidos) == 0 and len(nao_encontrados) == 0:
        relatorio = (
            f"👤 **Usuário:** {primeiro_nome}\n"
            f"🗑️ **Contratos removidos:** Não há remoções a serem feitas\n"
            f"📅 **Data da remoção:** {data_remocao}\n"
            f"⏭️ **Próxima remoção:** {proxima_remocao}"
        )
    else:
        lista_nao_encontrados = ", ".join(nao_encontrados) if nao_encontrados else "Nenhum"
        relatorio = (
            f"✅ **Removido por:** {primeiro_nome}\n"
            f"🗑️ **Contratos removidos:** {len(removidos)}\n"
            f"⚠️ **Contratos não encontrados:** {lista_nao_encontrados}\n"
            f"⏱️ **Tempo de rodagem do BrocaTratos:** {tempo_formatado}\n"
            f"📅 **Data da remoção:** {data_remocao}\n"
            f"⏭️ **Próxima remoção:** {proxima_remocao}"
        )

    try:
        await status_msg.edit(content=relatorio)
    except:
        await ctx.send(relatorio)

@bot.command()
async def stop(ctx):
    global robo_rodando
    if ctx.channel.name == "contratos-removidos":
        robo_rodando = False
        await ctx.send("Sinal de parada enviado! O robô vai encerrar assim que terminar o chamado atual e fechará o navegador.")
    else:
        await ctx.send("Comando não autorizado neste canal.")

@bot.command()
async def clear(ctx, amount: int = 100):
    if ctx.channel.name == "contratos-removidos":
        await ctx.channel.purge(limit=amount)
        msg = await ctx.send(f"🧹 Histórico limpo ({amount} mensagens).")
        await asyncio.sleep(3)
        await msg.delete()
    else:
        await ctx.send("Comando não autorizado neste canal.")

if __name__ == "__main__":
    load_dotenv()
    bot.run(os.getenv("DISCORD_TOKEN"))