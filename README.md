# Halvorsen og Fjetland – nettside

Statisk nettside for maskinutleie, publisert med GitHub Pages.

## Endre innhold

- **Telefon, e-post og maskiner:** øverst i `<script>` nederst i `index.html` (`KONTAKT` og `MASKINER`).
- **Priser, adresse:** søk etter `[PRIS]` og `[ADRESSE]` i `index.html`.
- **Opptatte dager:** legg datoer inn i `bookinger.json`, per maskin, format `ÅÅÅÅ-MM-DD`:

```json
{ "vtw18": ["2026-12-05", "2026-12-06"] }
```

Rediger rett på github.com (blyant-ikonet), så er siden oppdatert etter et minutt.

## Før lansering

- Fyll inn alle `[...]`-plassholdere og legg inn bilder.
- Fjern `<meta name="robots" content="noindex">` i `index.html` så Google finner siden.
