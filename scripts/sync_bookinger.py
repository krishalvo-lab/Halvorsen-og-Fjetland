"""Henter bookingkalenderen (iCal) og skriver opptatte dager per maskin til bookinger.json.

Kalenderadressen leses fra miljøvariabelen GCAL_ICS_URL (GitHub-secret).
Bare maskin-id og datoer skrives ut – aldri kundenavn eller andre detaljer.

Maskin gjenkjennes fra tittelen på hendelsen, f.eks. «Minigraver 1,8 t – Ola».
Hendelser uten gjenkjent maskin hoppes over og logges.
"""
import json
import os
import re
import sys
import urllib.request
from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo

OSLO = ZoneInfo("Europe/Oslo")

# Rekkefølgen betyr noe: mest spesifikke treff først.
MASKINER = [
    ("vtw12s", ["vtw-12", "vtw12", "1,2 t", "1.2 t", "1,2t", "1.2t", "1,2 tonn"]),
    ("vtw18", ["vtw-18", "vtw18", "1,8 t", "1.8 t", "1,8t", "1.8t", "1,8 tonn"]),
    ("vtw25", ["vtw-25", "vtw25", "2,5 t", "2.5 t", "2,5t", "2.5t", "2,5 tonn"]),
    ("vth480z", ["vth-480", "vth480", "minilaster", "skid steer", "laster"]),
    ("vtys50a", ["ys50", "dumper", "trillebår", "trillebor"]),
    ("vtgc500", ["gc500", "beitepusser", "klipper"]),
]


def hent_ics(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "hf-booking-sync"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", errors="replace")


def unfold(text: str) -> list[str]:
    lines: list[str] = []
    for raw in text.splitlines():
        if raw[:1] in (" ", "\t") and lines:
            lines[-1] += raw[1:]
        else:
            lines.append(raw)
    return lines


def parse_dt(key: str, value: str):
    """Returnerer (date|datetime, er_heldag)."""
    params = dict(p.split("=", 1) for p in key.split(";")[1:] if "=" in p)
    if params.get("VALUE") == "DATE" or re.fullmatch(r"\d{8}", value):
        return datetime.strptime(value, "%Y%m%d").date(), True
    if value.endswith("Z"):
        dt = datetime.strptime(value, "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc)
    else:
        tz = ZoneInfo(params["TZID"]) if "TZID" in params else OSLO
        dt = datetime.strptime(value, "%Y%m%dT%H%M%S").replace(tzinfo=tz)
    return dt.astimezone(OSLO), False


def hendelser(lines: list[str]):
    ev = None
    for line in lines:
        if line == "BEGIN:VEVENT":
            ev = {}
        elif line == "END:VEVENT":
            if ev is not None:
                yield ev
            ev = None
        elif ev is not None and ":" in line:
            key, value = line.split(":", 1)
            name = key.split(";", 1)[0]
            if name in ("DTSTART", "DTEND"):
                ev[name] = parse_dt(key, value)
            elif name in ("SUMMARY", "STATUS"):
                ev[name] = value.replace("\\,", ",").replace("\\;", ";").strip()


def maskin_for(tittel: str) -> str | None:
    t = tittel.lower()
    for mid, ord_ in MASKINER:
        if any(o in t for o in ord_):
            return mid
    return None


def dager(start, slutt, heldag: bool) -> list[date]:
    if heldag:
        d0, d1 = start, slutt  # DTEND er eksklusiv for heldagshendelser
    else:
        d0 = start.date()
        # en hendelse som slutter nøyaktig ved midnatt opptar ikke neste dag
        d1 = (slutt - timedelta(seconds=1)).date() + timedelta(days=1)
    out, d = [], d0
    while d < d1:
        out.append(d)
        d += timedelta(days=1)
    return out


def main() -> int:
    url = os.environ.get("GCAL_ICS_URL", "").strip()
    if not url:
        print("GCAL_ICS_URL mangler – ingenting å gjøre.")
        return 0
    lines = unfold(hent_ics(url))
    idag = datetime.now(OSLO).date()
    resultat: dict[str, set] = {mid: set() for mid, _ in MASKINER}
    for ev in hendelser(lines):
        if ev.get("STATUS", "").upper() == "CANCELLED" or "DTSTART" not in ev:
            continue
        tittel = ev.get("SUMMARY", "")
        mid = maskin_for(tittel)
        if not mid:
            print(f"Hopper over (ukjent maskin): {tittel[:40]!r}")
            continue
        start, heldag = ev["DTSTART"]
        slutt = ev.get("DTEND", (start + timedelta(days=1) if heldag else start, heldag))[0]
        for d in dager(start, slutt, heldag):
            if d >= idag:
                resultat[mid].add(d.isoformat())
    data = {mid: sorted(v) for mid, v in resultat.items()}
    with open("bookinger.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print("Opptatte dager:", {k: len(v) for k, v in data.items()})
    return 0


if __name__ == "__main__":
    sys.exit(main())
