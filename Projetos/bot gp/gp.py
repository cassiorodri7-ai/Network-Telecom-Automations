import os
import shutil
from datetime import datetime
import glob

def organizar_gopro(diretorio_origem, diretorio_destino):
    if not os.path.exists(diretorio_destino):
        os.makedirs(diretorio_destino)

    arquivos_mp4 = glob.glob(os.path.join(diretorio_origem, "*.[mM][pP]4"))
    arquivos_lixo = glob.glob(os.path.join(diretorio_origem, "*.[lL][rR][vV]")) + glob.glob(os.path.join(diretorio_origem, "*.[tT][hH][mM]"))

    for lixo in arquivos_lixo:
        try:
            os.remove(lixo)
        except Exception:
            pass

    for mp4 in arquivos_mp4:
        try:
            data_modificacao = os.path.getmtime(mp4)
            data_formatada = datetime.fromtimestamp(data_modificacao).strftime('%Y-%m-%d')
            
            pasta_destino = os.path.join(diretorio_destino, data_formatada)
            if not os.path.exists(pasta_destino):
                os.makedirs(pasta_destino)
            
            nome_arquivo = os.path.basename(mp4)
            caminho_destino = os.path.join(pasta_destino, nome_arquivo)
            
            shutil.move(mp4, caminho_destino)
        except Exception:
            pass

if __name__ == "__main__":
    diretorio_sd = r"C:\Users\cassio.correa\Desktop\SD_Teste"
    diretorio_pc = r"C:\Users\cassio.correa\Desktop\GoPro_Organizado"
    
    organizar_gopro(diretorio_sd, diretorio_pc)