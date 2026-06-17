import os
import re
import requests
from bs4 import BeautifulSoup
import pandas as pd
from flask import Flask, request

app = Flask(__name__)
NOME_PLANILHA = "orcamento_total.xlsx"

def raspar_mercadolivre(url):
    match = re.search(r'(MLB)-?(\d+)', url, re.IGNORECASE)
    if match:
        item_id = f"MLB{match.group(2)}"
        api_url = f"https://api.mercadolibre.com/items/{item_id}"
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "application/json"
            }
            res = requests.get(api_url, headers=headers, timeout=10)
            if res.status_code == 200:
                dados = res.json()
                titulo = dados.get("title", "Produto Desconhecido")
                preco = f"R$ {dados.get('price', 'Sob Consulta')}"
                return titulo, preco
        except Exception:
            pass
    return None, None

def raspar_amazon(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8"
    }
    try:
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, "html.parser")
            titulo_tag = soup.find(id="productTitle")
            titulo = titulo_tag.text.strip() if titulo_tag else "Produto Desconhecido"
            
            preco = "Sob Consulta"
            preco_tag = soup.select_one("span.a-price span.a-offscreen") or soup.find("span", class_="a-offscreen")
            
            if preco_tag:
                raw_preco = preco_tag.text.strip()
                match = re.search(r'(\d+(?:\.\d+)?,\d{2})', raw_preco)
                if match:
                    preco = f"R$ {match.group(1)}"
            return titulo, preco
    except Exception:
        pass
    return None, None

def raspar_produto(url):
    if "mercadolivre.com.br" in url or "mercadolibre" in url:
        titulo, preco = raspar_mercadolivre(url)
        if titulo and titulo != "Produto Desconhecido":
            return titulo, preco

    if "amazon.com" in url:
        titulo, preco = raspar_amazon(url)
        if titulo:
            return titulo, preco

    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8"
        }
        resposta = requests.get(url, headers=headers, timeout=10)
        
        if resposta.status_code == 200:
            soup = BeautifulSoup(resposta.text, "html.parser")
            meta_title = soup.find("meta", property="og:title")
            titulo = meta_title["content"] if meta_title else None
            
            if not titulo:
                h1 = soup.find("h1")
                titulo = h1.text.strip() if h1 else "Produto Desconhecido"
                
            titulo = titulo.replace(" | MercadoLivre", "").strip()
            preco = "Sob Consulta"
            meta_price = soup.find("meta", property="product:price:amount") or soup.find("meta", attrs={"itemprop": "price"})
            
            if meta_price and meta_price.get("content"):
                preco = f"R$ {meta_price['content']}"
            else:
                for classe in ["andes-money-amount__fraction", "price", "preco", "amount", "val", "valores"]:
                    elemento = soup.find(class_=re.compile(classe, re.IGNORECASE))
                    if elemento and elemento.text.strip():
                        raw_preco = elemento.text.strip()
                        match = re.search(r'(\d+(?:\.\d+)?,\d{2})', raw_preco)
                        if match:
                            preco = f"R$ {match.group(1)}"
                        else:
                            preco = f"R$ {raw_preco}"
                        break
            return titulo, preco
    except Exception:
        pass
    return None, None

def atualizar_base_dados(nome, preco, url):
    dados = []
    if os.path.exists(NOME_PLANILHA):
        try:
            df_antigo = pd.read_excel(NOME_PLANILHA)
            dados = df_antigo.to_dict(orient="records")
        except Exception:
            pass
    dados.append({"Produto": nome, "Preço": preco, "Link": url})
    df_novo = pd.DataFrame(dados)
    df_novo.to_excel(NOME_PLANILHA, index=False)

@app.route("/webhook", methods=["POST"])
def webhook_whatsapp():
    dados = request.get_json(silent=True)
    if not dados:
        return {"status": "erro", "motivo": "JSON invalido"}, 400
    print(f"\n📥 Mensagem recebida: '{dados.get('message', '')}'")
    try:
        mensagem = dados.get("message", "")
        urls = re.findall(r"(https?://[^\s\"\'\\]+)", mensagem)
        if urls:
            url_alvo = urls[0]
            print(f"🔍 Link detectado! Raspando dados de: {url_alvo}")
            nome, preco = raspar_produto(url_alvo)
            if nome:
                preco = preco if preco else "Sob Consulta"
                atualizar_base_dados(nome, preco, url_alvo)
                print(f"✅ Salvo na planilha: {nome} | {preco}")
                return {"status": "sucesso", "notificacao": "Planilha atualizada!"}, 200
            else:
                print("⚠️ Não foi possível extrair dados desse site.")
                return {"status": "alerta", "motivo": "Falha na raspagem"}, 200
        else:
            print("ℹ️ Nenhum link de produto encontrado na mensagem.")
            return {"status": "ignorado", "motivo": "Sem link"}, 200
    except Exception as e:
        print(f"❌ Erro interno do Servidor: {e}")
        return {"status": "erro", "motivo": str(e)}, 500

if __name__ == "__main__":
    app.run(port=5000)