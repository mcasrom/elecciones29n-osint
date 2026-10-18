#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import getpass
import html
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(os.environ.get("ELECCIONES29N_REPO", Path(__file__).resolve().parent.parent))
STATE = Path(os.environ.get("ELECCIONES29N_STATE_DIR", Path.home() / ".config/elecciones29n"))
LOGS = Path(os.environ.get("ELECCIONES29N_LOG_DIR", Path.home() / ".local/state/elecciones29n"))
NEEDS = STATE / "needs.json"
PANEL = STATE / "needs.html"
LAST_DIGEST = STATE / "last_digest"
PENDING = STATE / "needs_pending"

SEED = [
    {
        "id": "gsc-index",
        "title": "GSC: comprobar indexación",
        "detail": "Revisa en Search Console que las 6 URLs nuevas estén indexadas; si no, solicita de nuevo.",
        "due": "2026-10-21",
        "status": "open",
        "source": "manual",
        "created": "2026-10-18",
    },
    {
        "id": "irdp-review",
        "title": "Revisión del índice IRDP",
        "detail": "2-4 h, solo revisión: ficha técnica, dispersión y error histórico; no publicar hasta contrastar.",
        "due": None,
        "status": "open",
        "source": "manual",
        "created": "2026-10-18",
    },
    {
        "id": "social-card",
        "title": "Tarjeta social del 29N",
        "detail": "El lanzador publish_e29n_card.py --dry funciona; falta decidir y publicar.",
        "due": None,
        "status": "open",
        "source": "manual",
        "created": "2026-10-18",
    },
]


def _now() -> dt.datetime:
    return dt.datetime.now().astimezone()


def _parse_dt(value: str | None) -> dt.datetime | None:
    if not value:
        return None
    try:
        return dt.datetime.fromisoformat(value)
    except ValueError:
        return None


def _parse_date(value: str | None) -> dt.date | None:
    if not value:
        return None
    try:
        return dt.date.fromisoformat(value)
    except ValueError:
        return None


def _ensure_dirs() -> None:
    STATE.mkdir(parents=True, exist_ok=True)
    LOGS.mkdir(parents=True, exist_ok=True)


def _save(data: dict) -> None:
    _ensure_dirs()
    data["updated_at"] = _now().isoformat(timespec="seconds")
    tmp = NEEDS.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(NEEDS)


def load() -> dict:
    _ensure_dirs()
    if NEEDS.exists():
        try:
            data = json.loads(NEEDS.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise SystemExit(f"needs.json inválido: {exc}") from exc
    else:
        data = {"tasks": []}
    data.setdefault("tasks", [])
    changed = not NEEDS.exists()
    for seed in SEED:
        if not any(t.get("id") == seed["id"] for t in data["tasks"]):
            data["tasks"].append(dict(seed))
            changed = True
    if changed:
        _save(data)
    return data


def _latest() -> dict | None:
    path = ROOT / "web" / "data" / "latest.json"
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def _item(
    task_id: str,
    title: str,
    detail: str,
    severity: str = "warning",
    due: str | None = None,
) -> dict:
    return {
        "id": task_id,
        "title": title,
        "detail": detail,
        "severity": severity,
        "due": due,
        "auto": True,
        "source": "auto",
    }


def auto_tasks() -> list[dict]:
    tasks: list[dict] = []
    now = _now()
    latest = _latest()
    if latest is None:
        tasks.append(_item("auto:data", "Sin datos publicados", "No existe web/data/latest.json; el build no ha generado datos.", "critical"))
    else:
        health = latest.get("health") or {}
        updated = _parse_dt(latest.get("updated_at_iso"))
        if updated is not None:
            if updated.tzinfo is None:
                updated = updated.astimezone()
            age_h = (now - updated).total_seconds() / 3600
            if age_h > 48:
                tasks.append(_item("auto:stale", "Datos muy desactualizados", f"La última actualización fue hace {age_h:.1f} h.", "critical"))
            elif age_h > 30:
                tasks.append(_item("auto:stale", "Datos desactualizados", f"La última actualización fue hace {age_h:.1f} h.", "warning"))

        if health.get("status") and health.get("status") != "ok":
            reasons = health.get("reasons") or []
            detail = "; ".join(str(r) for r in reasons) if reasons else "La salud de la muestra no está en ok."
            tasks.append(_item("auto:health", "Muestra justa", detail, "warning"))

        n_polls = health.get("n_polls")
        if n_polls is None:
            n_polls = latest.get("n_polls")
        if isinstance(n_polls, int) and n_polls < 4:
            tasks.append(_item("auto:few-polls", "Pocos sondeos", f"Solo hay {n_polls} sondeos en la ventana; el objetivo es 4 o más.", "warning"))

        houses = health.get("n_pollsters")
        if houses is None:
            houses = len(health.get("pollsters") or [])
        if isinstance(houses, int) and houses < 2:
            tasks.append(_item("auto:few-houses", "Pocas casas", f"Solo hay {houses} casa(s) independiente(s); el objetivo es 2 o más.", "warning"))

        days = health.get("days_since_last")
        if not latest.get("in_blackout") and isinstance(days, int) and days > 7:
            tasks.append(_item("auto:last-poll", "Último sondeo antiguo", f"El último sondeo tiene {days} días; toca buscar uno nuevo.", "warning"))

    for name, task_id, title in (
        ("entrada_sondeos.csv", "auto:inbox", "Sondeos en el inbox"),
        ("entrada_resultados.csv", "auto:results", "Resultados en el inbox"),
    ):
        path = ROOT / "data" / name
        if not path.exists():
            continue
        lines = [line.strip() for line in path.read_text(encoding="utf-8", errors="ignore").splitlines() if line.strip()]
        rows = [line for line in lines[1:] if not line.upper().startswith("EJEMPLO")]
        if rows:
            tasks.append(_item(task_id, title, f"{len(rows)} fila(s) pendientes en data/{name}.", "warning"))

    last_error = STATE / "last_error"
    if last_error.exists():
        detail = last_error.read_text(encoding="utf-8", errors="ignore").strip()
        tasks.append(_item("auto:error", "Última ejecución con error", detail[:800] or "Revisa last_error.", "critical"))
    elif now.hour >= 9 and not (STATE / f"last_run_{now:%Y%m%d}").exists():
        tasks.append(_item("auto:last-run", "El cron no ha dejado marca hoy", "No existe last_run de hoy y no hay error registrado; revisa el timer o ejecuta run_daily.sh.", "warning"))

    return tasks


def manual_tasks(data: dict) -> list[dict]:
    today = _now().date()
    out: list[dict] = []
    for task in data.get("tasks", []):
        if task.get("status") != "open":
            continue
        snooze = _parse_date(task.get("snooze_until"))
        if snooze is not None and snooze > today:
            continue
        due = _parse_date(task.get("due"))
        severity = "warning" if due is not None and due <= today + dt.timedelta(days=3) else "info"
        out.append({
            "id": task["id"],
            "title": task.get("title", task["id"]),
            "detail": task.get("detail", ""),
            "severity": severity,
            "due": due.isoformat() if due else None,
            "auto": False,
            "source": task.get("source", "manual"),
        })
    return out


def all_tasks(data: dict) -> list[dict]:
    tasks = auto_tasks() + manual_tasks(data)
    tasks.sort(key=lambda t: ({"critical": 0, "warning": 1, "info": 2}.get(t["severity"], 3), t.get("due") or "9999-12-31", t["title"]))
    return tasks


def _status(latest: dict | None) -> dict:
    if not latest:
        return {"updated_at": "sin datos", "last_poll_date": "-", "n_polls": "-", "n_pollsters": "-", "days_since_last": "-", "in_blackout": False}
    health = latest.get("health") or {}
    return {
        "updated_at": latest.get("updated_at") or "-",
        "last_poll_date": latest.get("last_poll_date") or "-",
        "n_polls": health.get("n_polls", latest.get("n_polls", "-")),
        "n_pollsters": health.get("n_pollsters", "-"),
        "days_since_last": health.get("days_since_last", "-"),
        "in_blackout": bool(latest.get("in_blackout")),
    }


def _fmt_date(value: str | None, today: dt.date) -> str:
    due = _parse_date(value)
    if due is None:
        return "sin fecha"
    delta = (due - today).days
    if delta < 0:
        return f"vencida hace {abs(delta)} d"
    if delta == 0:
        return "vence hoy"
    if delta == 1:
        return "vence mañana"
    return f"vence en {delta} d"


def render_panel(tasks: list[dict], latest: dict | None) -> None:
    _ensure_dirs()
    status = _status(latest)
    today = _now().date()
    rows = []
    for task in tasks:
        sev = html.escape(task["severity"])
        title = html.escape(task["title"])
        detail = html.escape(task["detail"] or "")
        due = _fmt_date(task.get("due"), today)
        kind = "auto" if task.get("auto") else "manual"
        command = ""
        if not task.get("auto"):
            command = f'<p class="cmd">Marcar hecho: <code>python3 scripts/needs.py done {html.escape(task["id"])}</code></p>'
        rows.append(
            f'<li class="{sev}"><div class="line"><strong>{title}</strong>'
            f'<span class="tag">{kind}</span><span class="due">{html.escape(due)}</span></div>'
            f'<p>{detail}</p>{command}</li>'
        )
    if not rows:
        rows.append('<li class="ok"><strong>Sin pendientes.</strong> Los datos están al día.</li>')
    body = "".join(rows)
    blackout = "sí" if status["in_blackout"] else "no"
    page = f"""<!doctype html>
<html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>29N - Pendientes</title>
<style>
:root{{--bg:#0f172a;--card:#111c33;--fg:#e8eef8;--muted:#9fb0c9;--line:#2a3b57;--accent:#f59e0b;--bad:#ef4444;--warn:#f59e0b;--ok:#22c55e}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--fg);font:15px/1.5 system-ui,-apple-system,Segoe UI,sans-serif}}
main{{max-width:860px;margin:0 auto;padding:28px 18px 48px}}h1{{font-size:26px;margin:0 0 4px}}.sub{{color:var(--muted);margin:0 0 20px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(130px,1fr));gap:10px;margin:18px 0}}
.card{{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:12px}}.k{{color:var(--muted);font-size:12px;text-transform:uppercase;letter-spacing:.06em}}.v{{font-size:20px;font-weight:700;margin-top:2px}}
ul{{list-style:none;padding:0;margin:0}}li{{background:var(--card);border:1px solid var(--line);border-left:4px solid var(--line);border-radius:10px;padding:12px 14px;margin:10px 0}}
li.critical{{border-left-color:var(--bad)}}li.warning{{border-left-color:var(--warn)}}li.info{{border-left-color:var(--accent)}}li.ok{{border-left-color:var(--ok)}}
.line{{display:flex;gap:10px;align-items:baseline;flex-wrap:wrap}}.tag{{font-size:11px;color:var(--muted);border:1px solid var(--line);border-radius:20px;padding:1px 7px}}.due{{font-size:12px;color:var(--muted);margin-left:auto}}
p{{margin:6px 0 0}}code{{background:#0b1324;border:1px solid var(--line);border-radius:5px;padding:1px 5px;font-size:12px}}
.cmd{{color:var(--muted);font-size:12px}}.foot{{color:var(--muted);font-size:12px;margin-top:24px}}
@media(prefers-color-scheme:light){{:root{{--bg:#f8fafc;--card:#fff;--fg:#0f172a;--muted:#5b6b82;--line:#d7dfeb}}code{{background:#f1f5f9}}}}
</style></head><body><main>
<h1>29N - lo que necesita tu atención</h1>
<p class="sub">Panel local, generado por <code>scripts/needs.py</code>. No se publica.</p>
<div class="grid">
<div class="card"><div class="k">Actualizado</div><div class="v">{html.escape(str(status["updated_at"]))}</div></div>
<div class="card"><div class="k">Sondeos</div><div class="v">{html.escape(str(status["n_polls"]))}</div></div>
<div class="card"><div class="k">Casas</div><div class="v">{html.escape(str(status["n_pollsters"]))}</div></div>
<div class="card"><div class="k">Último sondeo</div><div class="v">{html.escape(str(status["days_since_last"]))} d</div></div>
<div class="card"><div class="k">Reflexión</div><div class="v">{blackout}</div></div>
</div>
<ul>{body}</ul>
<p class="foot">Los avisos automáticos se resuelven solos. Los manuales se marcan con <code>python3 scripts/needs.py done &lt;id&gt;</code>. Para añadir: <code>python3 scripts/needs.py add --id ... --title ...</code>.</p>
</main></body></html>"""
    PANEL.write_text(page, encoding="utf-8")


def _session_active() -> bool:
    user = os.environ.get("USER") or getpass.getuser()
    try:
        result = subprocess.run(
            ["loginctl", "show-user", user, "-p", "Sessions", "--value"],
            capture_output=True, text=True, timeout=3, check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return True
    sessions = result.stdout.split()
    if not sessions:
        return False
    for session in sessions:
        active = subprocess.run(
            ["loginctl", "show-session", session, "-p", "Active", "--value"],
            capture_output=True, text=True, timeout=3, check=False,
        )
        if active.stdout.strip() == "yes":
            return True
    return False


def _display_available() -> bool:
    return bool(
        os.environ.get("DISPLAY")
        and os.environ.get("DBUS_SESSION_BUS_ADDRESS")
        and shutil.which("notify-send")
        and _session_active()
    )


def _notification_body(tasks: list[dict]) -> str:
    lines = [f"· {t['title']}" for t in tasks[:4]]
    if len(tasks) > 4:
        lines.append(f"· +{len(tasks) - 4} más")
    latest = _latest()
    st = _status(latest)
    lines.append(f"Datos: {st['n_polls']} sondeos · {st['n_pollsters']} casas · último hace {st['days_since_last']} d")
    lines.append(f"Panel: {PANEL.as_uri()}")
    return "\n".join(lines)


def send(tasks: list[dict], all_clear: bool = False) -> bool:
    _ensure_dirs()
    if not _display_available():
        PENDING.write_text(_now().isoformat(timespec="seconds"), encoding="utf-8")
        print("aviso pendiente: no hay sesión gráfica; se mostrará al entrar")
        return False
    if all_clear:
        title = "29N · todo al día"
        body = _notification_body([])
    else:
        title = f"29N · {len(tasks)} pendiente" + ("" if len(tasks) == 1 else "s")
        body = _notification_body(tasks)
    urgency = "critical" if any(t["severity"] == "critical" for t in tasks) else "normal"
    result = subprocess.run(
        ["notify-send", "-a", "Elecciones 29N", "-u", urgency, title, body],
        capture_output=True, text=True, timeout=10, check=False,
    )
    if result.returncode == 0:
        LAST_DIGEST.write_text(_now().isoformat(timespec="seconds"), encoding="utf-8")
        PENDING.unlink(missing_ok=True)
        print("aviso enviado")
        return True
    PENDING.write_text(_now().isoformat(timespec="seconds"), encoding="utf-8")
    print("aviso pendiente: notify-send falló")
    return False


def _should_send(args: argparse.Namespace) -> bool:
    if args.force:
        return True
    if args.if_pending:
        return PENDING.exists()
    if args.if_due:
        if PENDING.exists():
            return True
        if not LAST_DIGEST.exists():
            return True
        last = _parse_dt(LAST_DIGEST.read_text(encoding="utf-8").strip())
        if last is None:
            return True
        if last.tzinfo is None:
            last = last.astimezone()
        return last.date() != _now().date()
    return True


def _print_tasks(tasks: list[dict]) -> None:
    if not tasks:
        print("sin pendientes")
        return
    for task in tasks:
        due = f" [{task['due']}]" if task.get("due") else ""
        kind = "auto" if task.get("auto") else "manual"
        print(f"{task['severity']:8} {kind:6} {task['id']}{due} · {task['title']}")


def cmd_seed(args: argparse.Namespace) -> int:
    data = load()
    print(f"seed: {len(data['tasks'])} tareas")
    return 0


def cmd_list(args: argparse.Namespace) -> int:
    data = load()
    tasks = all_tasks(data)
    if args.json:
        print(json.dumps(tasks, ensure_ascii=False, indent=2))
    else:
        _print_tasks(tasks)
    return 0


def cmd_add(args: argparse.Namespace) -> int:
    data = load()
    task_id = args.id or re.sub(r"[^a-z0-9]+", "-", args.title.lower()).strip("-")
    if any(t.get("id") == task_id for t in data["tasks"]):
        raise SystemExit(f"ya existe: {task_id}")
    data["tasks"].append({
        "id": task_id,
        "title": args.title,
        "detail": args.detail or "",
        "due": args.due,
        "status": "open",
        "source": "manual",
        "created": _now().date().isoformat(),
    })
    _save(data)
    print(f"añadida: {task_id}")
    return 0


def cmd_done(args: argparse.Namespace) -> int:
    data = load()
    changed = False
    for task_id in args.id:
        found = next((t for t in data["tasks"] if t.get("id") == task_id), None)
        if found is None:
            print(f"no existe: {task_id}")
            continue
        if found.get("source") == "auto":
            print(f"auto, se resuelve solo: {task_id}")
            continue
        found["status"] = "done"
        found["done_at"] = _now().isoformat(timespec="seconds")
        changed = True
        print(f"hecha: {task_id}")
    if changed:
        _save(data)
    return 0


def cmd_snooze(args: argparse.Namespace) -> int:
    data = load()
    until = (_now().date() + dt.timedelta(days=args.days)).isoformat()
    found = next((t for t in data["tasks"] if t.get("id") == args.id), None)
    if found is None:
        raise SystemExit(f"no existe: {args.id}")
    found["snooze_until"] = until
    _save(data)
    print(f"pospuerta hasta {until}: {args.id}")
    return 0


def cmd_digest(args: argparse.Namespace) -> int:
    data = load()
    tasks = all_tasks(data)
    latest = _latest()
    render_panel(tasks, latest)
    if args.print:
        _print_tasks(tasks)
    if args.no_notify:
        return 0
    if not tasks and not args.all_clear:
        PENDING.unlink(missing_ok=True)
        print("sin pendientes")
        return 0
    if not _should_send(args):
        print("aviso no toca todavía")
        return 0
    send(tasks, all_clear=args.all_clear)
    return 0


def cmd_panel(args: argparse.Namespace) -> int:
    data = load()
    render_panel(all_tasks(data), _latest())
    print(PANEL)
    if args.open and shutil.which("xdg-open"):
        subprocess.run(["xdg-open", str(PANEL)], check=False)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Centro de avisos local de Elecciones 29N")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_seed = sub.add_parser("seed")
    p_seed.set_defaults(func=cmd_seed)

    p_list = sub.add_parser("list")
    p_list.add_argument("--json", action="store_true")
    p_list.set_defaults(func=cmd_list)

    p_add = sub.add_parser("add")
    p_add.add_argument("--id")
    p_add.add_argument("--title", required=True)
    p_add.add_argument("--detail")
    p_add.add_argument("--due")
    p_add.set_defaults(func=cmd_add)

    p_done = sub.add_parser("done")
    p_done.add_argument("id", nargs="+")
    p_done.set_defaults(func=cmd_done)

    p_snooze = sub.add_parser("snooze")
    p_snooze.add_argument("id")
    p_snooze.add_argument("--days", type=int, default=7)
    p_snooze.set_defaults(func=cmd_snooze)

    p_digest = sub.add_parser("digest")
    p_digest.add_argument("--force", action="store_true")
    p_digest.add_argument("--if-due", action="store_true")
    p_digest.add_argument("--if-pending", action="store_true")
    p_digest.add_argument("--no-notify", action="store_true")
    p_digest.add_argument("--all-clear", action="store_true")
    p_digest.add_argument("--print", action="store_true")
    p_digest.set_defaults(func=cmd_digest)

    p_panel = sub.add_parser("panel")
    p_panel.add_argument("--open", action="store_true")
    p_panel.set_defaults(func=cmd_panel)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
