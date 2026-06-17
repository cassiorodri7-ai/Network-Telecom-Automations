import discord
from discord.ext import commands
import subprocess
import time
import pygetwindow as gw
import os
from datetime import datetime
import asyncio
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

def organize_windows(window_titles, cols, width, height):
    for index, title in enumerate(window_titles):
        try:
            windows = gw.getWindowsWithTitle(title)
            if windows:
                win = windows[0]
                row = index // cols
                col = index % cols
                win.resizeTo(width, height)
                win.moveTo(col * width, row * height)
        except Exception:
            pass

def close_windows(window_titles):
    for title in window_titles:
        os.system(f'taskkill /FI "WINDOWTITLE eq {title}*" /T /F >nul 2>&1')

async def get_ping_stats(ip):
    process = await asyncio.create_subprocess_shell(
        f"ping {ip} -n 30 -w 1000",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, _ = await process.communicate()
    output = stdout.decode('cp850', errors='replace')
    
    lines = output.split('\n')
    summary_lines = []
    capture = False
    
    for line in lines:
        clean_line = line.rstrip("\r")
        
        if "Pacotes:" in clean_line or "Packets:" in clean_line:
            capture = True
            
        if capture:
            if clean_line.strip(): 
                summary_lines.append(clean_line.strip())

    if not summary_lines:
        summary_text = "    Pacotes: Enviados = 30, Recebidos = 0, Perdidos = 30 (100% de perda)"
    else:
        summary_text = "\n".join(summary_lines)
        
    return f"--- Estatísticas do Ping para {ip} ---\n{summary_text}\n\n"

@bot.command()
async def pings(ctx, *, ips_str: str):
    ip_list = ips_str.split()
    if not ip_list:
        return

    prompt_msg = await ctx.send("Digite o nome do relatório:")

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    try:
        msg = await bot.wait_for('message', check=check, timeout=60.0)
        report_name = msg.content.strip()
        await prompt_msg.delete()
        await msg.delete()
    except asyncio.TimeoutError:
        await prompt_msg.delete()
        await ctx.send("Tempo esgotado.")
        return

    await ctx.send(f"Iniciando {len(ip_list)} janelas por 30 segundos. O relatório '{report_name}' será gerado ao final.")

    opened_titles = []
    for ip in ip_list:
        title = f"Ping {ip}"
        subprocess.Popen(f'start "{title}" cmd /c ping {ip} -n 30 -w 1000', shell=True)
        opened_titles.append(title)
        time.sleep(0.5)

    cols = 4 if len(ip_list) > 4 else len(ip_list)
    time.sleep(1)
    organize_windows(opened_titles, cols, 400, 300)

    tasks = [get_ping_stats(ip) for ip in ip_list]
    results = await asyncio.gather(*tasks)

    close_windows(opened_titles)

    base_dir = os.path.dirname(os.path.abspath(__file__))
    report_dir = os.path.join(base_dir, "Relatorios")
    os.makedirs(report_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    invalid_chars = '<>:"/\\|?*'
    safe_report_name = ''.join(c for c in report_name if c not in invalid_chars)
    
    report_path = os.path.join(report_dir, f"{safe_report_name}.txt")

    with open(report_path, "w", encoding="utf-8") as f:
        for result in results:
            f.write(result)

    await ctx.send(f"Relatório gerado com sucesso em: `{report_path}`")

    ask_msg = await ctx.send("Deseja gerar outro relatório? (S ou N)")

    try:
        resp_msg = await bot.wait_for('message', check=check, timeout=60.0)
        choice = resp_msg.content.strip().lower()
        await ask_msg.delete()
        await resp_msg.delete()
        
        if choice == 's':
            await ctx.send("comece com !pings")
        elif choice == 'n':
            await ctx.send("Bot será finalizado agora.")
            await bot.close()
    except asyncio.TimeoutError:
        await ask_msg.delete()

if __name__ == "__main__":
    if not TOKEN:
        pass
    else:
        bot.run(TOKEN)