# Halvorsen og Fjetland – nettside

Statisk nettside for maskinutleie, publisert med GitHub Pages.

## Endre innhold

- **Telefon, e-post og maskiner:** øverst i `<script>` nederst i `index.html` (`KONTAKT` og `MASKINER`).
- **Priser:** søk etter `[PRIS]` i `index.html`.
- **Opptatte dager** hentes automatisk fra Google-kalenderen «H&F booking» hvert 30. minutt
  (se under). `bookinger.json` skal ikke redigeres for hånd.

## Booking i kalenderen

Legg bookingen inn i «H&F booking» med maskinen i tittelen, f.eks.:

| Maskin | Skriv i tittelen (ett av) |
|---|---|
| Minigraver 1,8 t | `1,8 t` eller `VTW-18` |
| Minigraver 2,5 t | `2,5 t` eller `VTW-25` |
| Minilaster 4WD | `Minilaster` |
| Beltedumper | `Dumper` |
| RC beitepusser | `Beitepusser` |

Eksempel: «Minigraver 1,8 t – Ola, Karmøy». Alle dager hendelsen dekker vises som opptatt.
Bare maskin og dato publiseres – aldri navn eller detaljer.

Oppsett (én gang): Settings → Secrets and variables → Actions → New repository secret,
navn `GCAL_ICS_URL`, verdi = «Hemmelig adresse i iCal-format» fra kalenderens innstillinger.
Kjør manuelt under Actions → «Synk bookinger fra kalender» → Run workflow.

## Før lansering

- Fyll inn alle `[...]`-plassholdere (`[PRIS]`, `[LAGRINGSTID]` i personvernerklæringen) og legg inn bilder.
- Fjern `<meta name="robots" content="noindex">` i `index.html` så Google finner siden.
