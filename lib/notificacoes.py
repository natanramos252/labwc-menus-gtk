"""Histórico de notificações do mako para a barra e o painel do calendário.

Guarda o que já foi visto e o que foi limpo em ~/.local/state. Como o mako
renumera as notificações quando a sessão reinicia, as marcas são zeradas
sempre que o processo do mako muda.
"""
import json
import os
import subprocess

ESTADO = os.path.join(os.path.expanduser("~/.local/state"), "labwc-notificacoes.json")


def _rodar(*cmd):
    """Executa um comando e devolve a saída (vazia se falhar)."""
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=3).stdout
    except (OSError, subprocess.TimeoutExpired):
        return ""


def _pid_mako():
    """PID atual do mako; muda quando a sessão reinicia."""
    return _rodar("pgrep", "-x", "mako").split("\n")[0].strip()


def ler_estado():
    """Lê o que já foi visto/limpo. Se o mako reiniciou, zera tudo (os números recomeçam)."""
    try:
        e = json.load(open(ESTADO))
    except (OSError, ValueError):
        e = {}
    pid = _pid_mako()
    if e.get("pid") != pid:  # mako reiniciou: os números recomeçam
        e = {"pid": pid, "limpo_ate": 0, "visto_ate": 0, "ocultos": []}
    return e


def gravar_estado(e):
    """Grava o estado em ~/.local/state/labwc-notificacoes.json."""
    os.makedirs(os.path.dirname(ESTADO), exist_ok=True)
    json.dump(e, open(ESTADO, "w"))


def _converter(item):
    """Converte uma notificação do formato do makoctl para um dicionário simples."""
    def v(chave, padrao=""):
        """Pega o valor de um campo no formato {'type': ..., 'data': ...} do makoctl."""
        return item.get(chave, {}).get("data", padrao)
    return {"id": int(v("id", 0)), "app": v("app-name"), "titulo": v("summary"), "texto": v("body"),
            "icone": v("app-icon"), "desktop": v("desktop-entry"), "urgencia": int(v("urgency", 1))}


def lista():
    """Notificações visíveis e do histórico, da mais nova para a mais antiga."""
    vistas = {}
    for comando in ("list", "history"):
        try:
            dados = json.loads(_rodar("makoctl", comando) or "{}").get("data", [[]])[0]
        except ValueError:
            dados = []
        for item in dados:
            n = _converter(item)
            vistas.setdefault(n["id"], n)
    e = ler_estado()
    return [n for n in sorted(vistas.values(), key=lambda n: -n["id"])
            if n["id"] > e["limpo_ate"] and n["id"] not in e["ocultos"]]


def novas():
    """Quantas notificações ainda não foram vistas (para o ponto azul do relógio)."""
    e = ler_estado()
    return sum(1 for n in lista() if n["id"] > e["visto_ate"])


def marcar_vistas():
    """Marca todas as notificações atuais como vistas."""
    e = ler_estado()
    ids = [n["id"] for n in lista()]
    if ids:
        e["visto_ate"] = max(e["visto_ate"], max(ids))
    gravar_estado(e)


def limpar():
    """Esconde todas as notificações atuais e fecha as que estiverem na tela."""
    e = ler_estado()
    ids = [n["id"] for n in lista()]
    if ids:
        e["limpo_ate"] = max(ids)
        e["visto_ate"] = max(e["visto_ate"], e["limpo_ate"])
    e["ocultos"] = []
    gravar_estado(e)
    _rodar("makoctl", "dismiss", "-a")


def ocultar(id_):
    """Esconde uma notificação específica (botão × no painel)."""
    e = ler_estado()
    e["ocultos"] = sorted(set(e["ocultos"]) | {id_})[-200:]
    gravar_estado(e)


def nao_perturbe():
    """Diz se o modo 'não perturbe' do mako está ligado."""
    return "do-not-disturb" in _rodar("makoctl", "mode")
