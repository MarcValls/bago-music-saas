#!/usr/bin/env python3
"""
cli.py — BAGO Music SaaS CLI

Gestiona el servidor FastAPI, el bot de Telegram, las herramientas web
y el estado del deploy desde la terminal.

Subcomandos:
    status          Ping al API + estado del webhook Telegram
    dev             Arranca el servidor FastAPI en local
    webhook <url>   Configura el webhook de Telegram
    test            Envía mensaje de prueba via bot
    open [tool]     Abre herramienta en el navegador
                    tools: transposer | teacher | editor | pwa
    build           Estado del último build en GitHub Actions
    config          Muestra la configuración activa

Uso:
    python3 cli.py                  → dashboard de estado
    python3 cli.py dev              → servidor local :7430
    python3 cli.py webhook <url>    → configura webhook Telegram
    python3 cli.py test             → test del bot
    python3 cli.py open transposer  → abre transpositor web
    python3 cli.py build            → estado GitHub Actions
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import urllib.request
import webbrowser
from pathlib import Path

# ── Config ────────────────────────────────────────────────────────────────────
ROOT   = Path(__file__).parent
STATE  = ROOT / ".cli_config.json"

DEFAULTS = {
    "token":       os.environ.get("BAGO_TELEGRAM_TOKEN", ""),
    "api_url":     os.environ.get("BAGO_MUSIC_URL", ""),
    "local_port":  "7430",
    "gh_repo":     "MarcValls/bago-music-saas",
    "pwa_url":     "https://marcvalls.github.io/bago-music-saas/",
}

WEB_TOOLS = {
    "transposer": "static/bago_score_transposer.html",
    "teacher":    "static/bago_score_teacher.html",
    "editor":     "static/bago_matrix_music_editor.html",
}

PLANS = [
    ("🆓 Free",   "€0/mes",   ["3 transposiciones/mes", "Export MusicXML"]),
    ("⭐ Pro",    "€4.99/mes", ["Transposiciones ilimitadas", "Export PDF/SVG/PNG", "Validación avanzada"]),
    ("🎛️ Studio", "€14.99/mes",["Todo Pro", "Ableton integration", "MIDI export + API"]),
]

# ANSI helpers
def _c(code: str, text: str) -> str:
    return f"\033[{code}m{text}\033[0m"

cyan   = lambda t: _c("96", t)
green  = lambda t: _c("92", t)
yellow = lambda t: _c("93", t)
red    = lambda t: _c("91", t)
bold   = lambda t: _c("1",  t)
dim    = lambda t: _c("2",  t)
reset  = "\033[0m"

# ── Config I/O ────────────────────────────────────────────────────────────────

def load_config() -> dict:
    if STATE.exists():
        try:
            saved = json.loads(STATE.read_text())
            return {**DEFAULTS, **saved}
        except Exception:
            pass
    return dict(DEFAULTS)


def save_config(cfg: dict) -> None:
    STATE.write_text(json.dumps(cfg, indent=2))


# ── HTTP helpers ──────────────────────────────────────────────────────────────

def _get(url: str, headers: dict | None = None, timeout: int = 8) -> dict | None:
    try:
        req = urllib.request.Request(url, headers=headers or {})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read())
    except Exception as e:
        return {"_error": str(e)}


def _post(url: str, data: dict, headers: dict | None = None, timeout: int = 10) -> dict | None:
    try:
        payload = json.dumps(data).encode()
        req = urllib.request.Request(
            url, data=payload,
            headers={"Content-Type": "application/json", **(headers or {})},
        )
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read())
    except Exception as e:
        return {"_error": str(e)}


# ── Commands ──────────────────────────────────────────────────────────────────

def cmd_status(cfg: dict) -> None:
    print(bold(cyan("\n  🎵 BAGO Music SaaS — Estado\n")))

    # Local API
    port = cfg["local_port"]
    local = _get(f"http://localhost:{port}/")
    if "_error" not in local:
        print(f"  {green('✅')} Servidor local     {dim(f'localhost:{port}')}  v{local.get('version','?')}")
    else:
        print(f"  {dim('○')} Servidor local     {dim('no activo')}")

    # Remote API
    api_url = cfg.get("api_url", "").rstrip("/")
    if api_url:
        remote = _get(f"{api_url}/")
        if "_error" not in remote:
            print(f"  {green('✅')} API remota         {dim(api_url)}")
        else:
            print(f"  {red('❌')} API remota         {dim(api_url)}  {dim(remote.get('_error',''))}")
    else:
        print(f"  {yellow('⚠')}  API remota         {dim('no configurada — bago music config')}")

    # Telegram webhook
    token = cfg.get("token", "")
    if token:
        info = _get(f"https://api.telegram.org/bot{token}/getWebhookInfo")
        if info and info.get("ok"):
            wh = info["result"]
            wh_url = wh.get("url", "")
            pending = wh.get("pending_update_count", 0)
            if wh_url:
                print(f"  {green('✅')} Telegram webhook   {dim(wh_url[:60])}")
                if pending:
                    print(f"     {yellow(f'⚠  {pending} updates pendientes')}")
            else:
                print(f"  {yellow('⚠')}  Telegram webhook   {dim('no configurado — usa: python cli.py webhook <URL>')}")
        else:
            print(f"  {red('❌')} Telegram token     {dim('inválido')}")
    else:
        print(f"  {dim('○')} Telegram           {dim('token no configurado')}")

    # PWA
    print(f"\n  {cyan('🌐')} PWA:   {cfg['pwa_url']}")
    print(f"  {cyan('📦')} Build: https://github.com/{cfg['gh_repo']}/actions\n")


def cmd_dev(cfg: dict) -> None:
    port = cfg["local_port"]
    print(bold(f"\n  🚀 Arrancando BAGO Music SaaS en localhost:{port}\n"))
    print(f"  {dim('Ctrl+C para parar')}\n")
    try:
        subprocess.run(
            [sys.executable, "-m", "uvicorn", "app.main:app",
             "--host", "127.0.0.1", "--port", port, "--reload"],
            cwd=str(ROOT),
        )
    except KeyboardInterrupt:
        print(f"\n  {dim('Servidor parado.')}")


def cmd_webhook(cfg: dict, url: str) -> None:
    token = cfg.get("token")
    if not token:
        print(red("\n  ❌ Token Telegram no configurado.\n"))
        print(f"  Exporta: {dim('export BAGO_TELEGRAM_TOKEN=<token>')}\n")
        return

    webhook_url = f"{url.rstrip('/')}/webhook"
    print(f"\n  Configurando webhook → {dim(webhook_url)}")

    result = _post(
        f"https://api.telegram.org/bot{token}/setWebhook",
        {"url": webhook_url},
    )
    if result and result.get("ok"):
        print(f"  {green('✅')} Webhook configurado correctamente")
        # Guardar la URL en config
        cfg["api_url"] = url.rstrip("/")
        save_config(cfg)
        print(f"  {dim(f'API URL guardada: {url}')}")
    else:
        print(f"  {red('❌')} Error: {result}")
    print()


def cmd_test(cfg: dict) -> None:
    token   = cfg.get("token")
    api_url = cfg.get("api_url", "").rstrip("/")

    print(bold(f"\n  🧪 Test del bot Telegram\n"))

    if not token:
        print(f"  {red('❌')} Token no configurado\n")
        return

    # getMe
    me = _get(f"https://api.telegram.org/bot{token}/getMe")
    if me and me.get("ok"):
        bot = me["result"]
        print(f"  {green('✅')} Bot activo: @{bot.get('username')}  ({bot.get('first_name')})")
    else:
        print(f"  {red('❌')} Token inválido: {me}")
        return

    # Webhook info
    wh = _get(f"https://api.telegram.org/bot{token}/getWebhookInfo")
    if wh and wh.get("ok"):
        url = wh["result"].get("url", "")
        pending = wh["result"].get("pending_update_count", 0)
        last_err = wh["result"].get("last_error_message", "")
        print(f"  {green('✅') if url else yellow('⚠')}  Webhook: {url or dim('no configurado')}")
        if pending:
            print(f"     {yellow(f'{pending} updates pendientes')}")
        if last_err:
            print(f"     {red(f'Último error: {last_err}')}")

    # Ping API remota
    if api_url:
        r = _get(f"{api_url}/api/state")
        if r and "_error" not in r:
            print(f"  {green('✅')} API remota responde: v{r.get('version','?')}")
        else:
            print(f"  {red('❌')} API remota no responde: {api_url}")
    print()


def cmd_open(cfg: dict, tool: str = "pwa") -> None:
    if tool == "pwa":
        url = cfg["pwa_url"]
    elif tool in WEB_TOOLS:
        html = ROOT / WEB_TOOLS[tool]
        if html.exists():
            url = html.as_uri()
        else:
            url = f"{cfg['pwa_url']}{WEB_TOOLS[tool]}"
    else:
        print(red(f"\n  ❌ Herramienta desconocida: '{tool}'"))
        print(f"  Opciones: {', '.join(['pwa', *WEB_TOOLS])}\n")
        return

    print(f"\n  🌐 Abriendo {bold(tool)}: {dim(url)}\n")
    webbrowser.open(url)


def cmd_build(cfg: dict) -> None:
    repo = cfg["gh_repo"]
    print(f"\n  🔨 GitHub Actions — {repo}\n")
    try:
        result = subprocess.run(
            ["gh", "run", "list", "--repo", repo, "--limit", "5",
             "--json", "status,conclusion,name,createdAt,databaseId"],
            capture_output=True, text=True, timeout=15,
        )
        if result.returncode == 0:
            runs = json.loads(result.stdout)
            for run in runs:
                status     = run.get("status", "")
                conclusion = run.get("conclusion", "")
                name       = run.get("name", "")
                created    = run.get("createdAt", "")[:16].replace("T", " ")
                rid        = run.get("databaseId", "")

                if conclusion == "success":
                    icon = green("✅")
                elif conclusion == "failure":
                    icon = red("❌")
                elif status == "in_progress":
                    icon = yellow("⏳")
                else:
                    icon = dim("○")

                print(f"  {icon}  {name:<35} {dim(created)}  {dim(str(rid))}")
        else:
            print(f"  {red('❌')} gh CLI error: {result.stderr.strip()}")
    except FileNotFoundError:
        url = f"https://github.com/{repo}/actions"
        print(f"  {dim('gh no instalado. Abre:')} {url}")
        webbrowser.open(url)
    print()


def cmd_config(cfg: dict) -> None:
    print(bold(cyan("\n  ⚙  BAGO Music SaaS — Configuración\n")))
    for k, v in cfg.items():
        val = ("*" * 12 + v[-4:]) if k in ("token",) and v else (v or dim("no configurado"))
        print(f"  {k:<20} {val}")
    print(f"\n  {dim('Config en: ' + str(STATE))}")
    print(f"  {dim('Env: BAGO_TELEGRAM_TOKEN, BAGO_MUSIC_URL')}\n")


def cmd_plans() -> None:
    print(bold(cyan("\n  💰 BAGO Music — Planes de suscripción\n")))
    for name, price, features in PLANS:
        print(f"  {bold(name)}   {cyan(price)}")
        for f in features:
            print(f"    {dim('•')} {f}")
        print()


def cmd_dashboard(cfg: dict) -> None:
    """Dashboard completo — vista por defecto."""
    print(f"\n  {bold(cyan('🎵 BAGO Music SaaS'))}  {dim('v1.0.0')}\n")
    print(f"  {'─' * 50}")

    cmd_status(cfg)

    print(f"  {'─' * 50}")
    print(bold("\n  Comandos disponibles:\n"))
    cmds = [
        ("python cli.py dev",                "Servidor local FastAPI"),
        ("python cli.py webhook <url>",      "Configurar bot Telegram"),
        ("python cli.py test",               "Test conexión bot"),
        ("python cli.py open transposer",    "Abrir transpositor"),
        ("python cli.py open teacher",       "Abrir score teacher"),
        ("python cli.py open editor",        "Abrir editor matricial"),
        ("python cli.py build",              "Estado GitHub Actions"),
        ("python cli.py config",             "Configuración activa"),
    ]
    for cmd, desc in cmds:
        print(f"  {cyan(cmd):<45}  {dim(desc)}")
    print()


# ── Entry point ───────────────────────────────────────────────────────────────

def main() -> None:
    args = sys.argv[1:]
    cfg  = load_config()

    if not args:
        cmd_dashboard(cfg)
        return

    sub = args[0]

    if sub == "status":
        cmd_status(cfg)
    elif sub == "dev":
        cmd_dev(cfg)
    elif sub == "webhook":
        if len(args) < 2:
            print(red("\n  ❌ Uso: python cli.py webhook <URL>\n"))
            sys.exit(1)
        cmd_webhook(cfg, args[1])
    elif sub == "test":
        cmd_test(cfg)
    elif sub == "open":
        cmd_open(cfg, args[1] if len(args) > 1 else "pwa")
    elif sub == "build":
        cmd_build(cfg)
    elif sub == "config":
        cmd_config(cfg)
    elif sub == "plans":
        cmd_plans()
    else:
        print(red(f"\n  ❌ Subcomando desconocido: '{sub}'"))
        print(f"  Usa: {dim('python cli.py')} para ver todos los comandos\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
