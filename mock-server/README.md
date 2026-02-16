# TBA3 Mock Server

Mock-API-Server für die TBA3-Spezifikation. Der Server liefert plausible Zufallsdaten zum Testen von API-Consumern wie Frontends.

## Voraussetzungen

Es wird [uv](https://docs.astral.sh/uv/getting-started/installation/) als Paketmanager benötigt. Python 3.14 wird von uv automatisch installiert, falls es nicht vorhanden ist.

## Projekt aufsetzen

Zuerst muss der Projektordner `tba3/mock-server` im Terminal geöffnet werden.

```bash
cd /path/to/tba3/mock-server
```

Das Virtual Environment und alle Abhängigkeiten werden mit zwei Befehlen eingerichtet:

```bash
uv venv
uv sync
```

## Metadaten vorbereiten

Außerdem müssen entsprechende Itemkennwerttabellen des IQB (als modularisierte CSV) im Ordner `metadata` abgelegt werden. Im Ordner `config` sind Äquivalenztabellen für die VERA 8-Durchgänge 2024 in den Fächern Deutsch, Mathematik, Englisch und Französisch angelegt, diese sind direkt mit den Itemkennwerttabellen des IQB kompatibel. Falls Kompetenzstufen für eigene Tabellen erzeugt werden sollen, müssen diese in der Config ergänzt werden.

## Server starten

Der API-Server wird mit folgendem Befehl gestartet:

```bash
uv run uvicorn api.main:app --reload
```

Die API ist danach unter `http://localhost:8000` erreichbar. Die interaktive Dokumentation (SwaggerUI) befindet sich unter `http://localhost:8000/docs`.
