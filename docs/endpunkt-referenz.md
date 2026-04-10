# TBA3-Auswertungsschnittstelle: Endpunkt-Referenz

Diese Referenz richtet sich an Frontend- und Backend-Entwickler:innen. Sie beschreibt alle Endpunkte, die die Spec definiert,
sowie die Konventionen, die auf diesen Endpunkten sinnvoll sind.

Grundbegriffe (Value-Group, 3-Schichten-Architektur) sind in [Konzepte und Architektur](konzepte.md) erklärt.

---

## Was die Spec definiert

Die Spec definiert **9 Endpunkte**: 3 Ebenen × 3 Datentypen. Jeder Endpunkt gibt ein **Array von Value-Groups** zurück.
Was eine einzelne Value-Group repräsentiert (eine Lerngruppe, ein:e SuS, eine Schule, ein Vergleichswert …),
hängt von der Implementierung des Backends bzw. dem Query-Parameter `type` ab.

---

### Kompetenzstufenverteilung (`/competence-levels`)

Jede Value-Group enthält ein `competenceLevels[]`-Array. Jeder Eintrag beschreibt eine Kompetenzstufe (z.B. „Regelstandard") mit zugehöriger deskriptiver Statistik (Häufigkeit, Mittelwert, Gesamtzahl).

| Ebene | Pfad | Value-Group enthält | Swagger-UI |
|---|---|---|---|
| Lerngruppe | `/groups/{id}/competence-levels` | `competenceLevels[]` mit Stufen + deskriptiver Statistik | [Link](https://apps.indibit.eu/tba3-api/docs#/groups/getGroupCompetenceLevels) |
| Schule | `/schools/{id}/competence-levels` | `competenceLevels[]` mit Stufen + deskriptiver Statistik | [Link](https://apps.indibit.eu/tba3-api/docs#/schools/getSchoolCompetenceLevels) |
| Land | `/states/{id}/competence-levels` | `competenceLevels[]` mit Stufen + deskriptiver Statistik | [Link](https://apps.indibit.eu/tba3-api/docs#/states/getStateCompetenceLevels) |

---

### Lösungshäufigkeiten (`/items`)

Jede Value-Group enthält ein `items[]`-Array. Jeder Eintrag beschreibt ein einzelnes Item (Testaufgabe) mit Lösungshäufigkeit und optionalen Item-Parametern.

| Ebene | Pfad | Value-Group enthält | Swagger-UI |
|---|---|---|---|
| Lerngruppe | `/groups/{id}/items` | `items[]` mit Lösungshäufigkeiten je Item | [Link](https://apps.indibit.eu/tba3-api/docs#/groups/getGroupItems) |
| Schule | `/schools/{id}/items` | `items[]` mit Lösungshäufigkeiten je Item | [Link](https://apps.indibit.eu/tba3-api/docs#/schools/getSchoolItems) |
| Land | `/states/{id}/items` | `items[]` mit Lösungshäufigkeiten je Item | [Link](https://apps.indibit.eu/tba3-api/docs#/states/getStateItems) |

---

### Aggregationen (`/aggregations`)

Jede Value-Group enthält ein `aggregations[]`-Array. Jeder Eintrag beschreibt eine Aggregation nach einem bestimmten Typ (z.B. nach Kompetenz oder Geschlecht) mit deskriptiver Statistik. Welche Aggregationsarten verfügbar sind, steuert der `aggregation`-Parameter (→ Query-Parameter).

| Ebene | Pfad | Value-Group enthält | Swagger-UI |
|---|---|---|---|
| Lerngruppe | `/groups/{id}/aggregations` | `aggregations[]` mit Typ + deskriptiver Statistik | [Link](https://apps.indibit.eu/tba3-api/docs#/groups/getGroupAggregations) |
| Schule | `/schools/{id}/aggregations` | `aggregations[]` mit Typ + deskriptiver Statistik | [Link](https://apps.indibit.eu/tba3-api/docs#/schools/getSchoolAggregations) |
| Land | `/states/{id}/aggregations` | `aggregations[]` mit Typ + deskriptiver Statistik | [Link](https://apps.indibit.eu/tba3-api/docs#/states/getStateAggregations) |

---

## Response-Inhalte einer Value-Group

Zur Orientierung die Grundstruktur einer Value-Group:

```
Value-Group
├── id           (optional) — Eindeutige Kennung
├── name         (Pflicht)  — Bezeichnung, z.B. "Klasse 8a"
├── domain       (optional)
│   ├── id       (optional)
│   └── name     (Pflicht) — z.B. "Leseverstehen"
├── subject      (optional)
│   ├── id       (optional)
│   └── name     (Pflicht) — z.B. "Deutsch"
├── covariates   (optional) — Kovariaten der Value-Group (Geschlecht, Sprache, ...)
├── properties   (optional) — Freie Key-Value-Metadaten
└── ... Ergebnisdaten (je nach Endpunkt)
```

Neben den endpunktspezifischen Ergebnisdaten (`competenceLevels`, `items`, `aggregations`) trägt jede Value-Group optionale Kontextfelder.
Konzeptionell sind alle diese Felder Metadaten über die Value-Group.
`subject` und `domain` sind bewusst als eigene Felder modelliert (nicht als Properties), weil Berichte sehr häufig nach Fach und Domäne gruppieren — sie sind strukturelle Metadaten.
`covariates` sind typisierte Merkmale der Personen in der Gruppe.
`properties` sind komplett freie Key-Value-Paare für alles andere.

---

### `type`: Typ einer Value-Group

Die Value-Group trägt ein optionales `type`-Feld, das die Granularität beschreibt. So kann ein Berichtselement erkennen, was eine Value-Group repräsentiert — auch ohne den ursprünglichen Request zu kennen.

| Wert | Bedeutung |
|---|---|
| `student` | Einzelne:r SuS |
| `group` | Lerngruppe |
| `school` | Schule |
| `district` | Stadt/Gemeinde |
| `authority` | Schulamt |
| `state` | Bundesland |

---

### `subject` und `domain`: Fach und Domäne

`subject` und `domain` sind eigene Response-Felder (nicht Properties), weil in Berichten fast immer nach Fach und Domäne gruppiert wird.

`subject` ist ein Objekt mit `id` (optional) und `name` (Pflicht), z.B. `{ name: "Deutsch" }`.
`domain` ist ebenfalls ein Objekt mit `id` (optional) und `name` (Pflicht). Der `name` enthält die lange Beschreibung der Domäne, z.B. `{ name: "Leseverstehen" }`.

Für den **Query-Parameter** `domain` werden Kürzel für Teilbereiche eines Fachs verwendet. Die Kürzel entsprechen den Domänen-Bezeichnungen aus den Itemkennwerttabellen des IQB ([Kompetenzstufenmodelle](https://www.iqb.hu-berlin.de/de/bista/entwicklung/kompetenzstufenmodelle/)).

| Fach | Fachkürzel | Mögliche Domänen-Kürzel (Query-Parameter) |
|---|---|---|
| Deutsch | `de` | `rs` (Rechtschreibung/Orthografie), `le` (Lesen), `ho` (Zuhören/Sprechen und Zuhören), `sp` (Sprache und Sprachgebrauch/Sprachgebrauch) |
| Mathematik | `ma` | V8 keine, V3  `zo` (Zahlen und Operationen), `rf` (Raum und Form), `gm` (Größen und Messen), `dh` (Daten, Häufigkeiten und Wahrscheinlichkeiten), `ms` (Muster und Strukturen) |
| Englisch | `en` | `ho` (Hörverstehen), `le` (Leseverstehen) |
| Französisch | `fr` | `ho` (Hörverstehen), `le` (Leseverstehen) |

**Wichtig: Query-Kürzel vs. Response-Objekt.** Die Kürzel in der Tabelle oben sind Werte für den `domain`-**Query-Parameter** (z.B. `?domain=rs`). Das `domain`-Feld in der **Response** ist dagegen ein Objekt mit der langen Beschreibung, z.B. `{ name: "Rechtschreibung" }`. Das Backend setzt die lange Beschreibung kontextabhängig — sie kann je nach Jahrgangsstufe variieren (z.B. `rs` = "Rechtschreibung" in der Grundschule, "Orthografie" in der Sek I).

---

### `covariates`: Merkmale Personen(gruppen)

Array von typisierten Merkmalen auf einer Value-Group. Jede Covariate hat `type`, `label`, `value`.

Vordefinierte Typen:

| `type` | Beschreibung | Beispiel-`value`s |
|---|---|---|
| `gender` | Geschlecht | `male`, `female`, `diverse` |
| `languageAtHome` | Sprache zu Hause | `german`, `other`, `english`, `french` |
| `other` | Frei erweiterbar — `label` beschreibt das Merkmal | z.B. Schulform, SES, Migrationshintergrund |

Für nicht-vordefinierte Merkmale steht der `other`-Typ zur Verfügung. Ob weitere freie `type`-Werte (z.B. `SES`, `schoolType`) verwendet werden können, ist noch nicht abschließend festgelegt. Aktuell beschreibt das `label` das Merkmal näher.

---

### `properties`: Freie Key-Value-Metadaten

Komplett offene Key-Value-Paare (`key`, `value`) für systemspezifische Metadaten über die Value-Group selbst.

Bekannte Beispiele:

| `key`               | Beschreibung          | Beispiel               |
|---------------------|-----------------------|------------------------|
| `firstName`         | Vorname               | `Maria`                |
| `lastName`          | Nachname              | `Muster`               |
| `startTime`         | Testbeginn            | `2024-03-15T08:00:00Z` |
| `endTime`           | Testende              | `2024-03-15T09:30:00Z` |
| `testDuration`      | Testdauer in Sekunden | `2541`                 |
| `schoolType`        | Schulform             | `Gymnasium`            |
| `testPeriod`        | Durchführungszeitraum | `2024-03`              |
| `booklet`           | Testheft-Kennung      | `V8-2024-DE-TH01`      |
| `participationRate` | Teilnahmequote        | `0.93`                 |

---

### Abgrenzung: Covariates vs. Properties

|                  | Covariates                               | Properties                                |
|------------------|------------------------------------------|-------------------------------------------|
| **Beschreiben**  | Merkmale der **Personen**(gruppe)        | Metadaten über die **Value-Group** selbst |
| **Beispiel**     | Geschlechterverteilung, Sprachverteilung | Testdauer, Schulform, Testheft            |
| **Struktur**     | Typisiert (`type`, `label`, `value`)     | Offene Key-Value-Paare (`key`, `value`)   |
| **Vordefiniert** | `gender`, `languageAtHome` + `other`     | Komplett frei                             |

**Faustregel:** Zusammensetzung der Personengruppe → Covariates. Kontext der Erhebung → Properties.

---

### Beispiel-Response: Kompetenzstufenverteilung mit Vergleichsgruppe

`GET /groups/3a-deutsch/competence-levels?comparison=3b-deutsch`

```json
[
  {
    "name": "Klasse 3a",
    "domain": { "name": "Leseverstehen" },
    "subject": { "name": "Deutsch" },
    "competenceLevels": [
      {
        "nameShort": "II",
        "name": "Mindeststandard",
        "descriptiveStatistics": { "frequency": 5, "total": 20, "mean": 0.25 }
      },
      {
        "nameShort": "III",
        "name": "Regelstandard",
        "descriptiveStatistics": { "frequency": 10, "total": 20, "mean": 0.50 }
      },
      {
        "nameShort": "IV",
        "name": "Optimalstandard",
        "descriptiveStatistics": { "frequency": 5, "total": 20, "mean": 0.25 }
      }
    ]
  },
  {
    "name": "Klasse 3b",
    "domain": { "name": "Leseverstehen" },
    "subject": { "name": "Deutsch" },
    "competenceLevels": [
      {
        "nameShort": "II",
        "name": "Mindeststandard",
        "descriptiveStatistics": { "frequency": 8, "total": 22, "mean": 0.36 }
      },
      {
        "nameShort": "III",
        "name": "Regelstandard",
        "descriptiveStatistics": { "frequency": 9, "total": 22, "mean": 0.41 }
      },
      {
        "nameShort": "IV",
        "name": "Optimalstandard",
        "descriptiveStatistics": { "frequency": 5, "total": 22, "mean": 0.23 }
      }
    ]
  }
]
```

Die erste Value-Group enthält die Ergebnisse der angefragten Lerngruppe (3a), die zweite die Vergleichsgruppe (3b). Beide tragen `domain` und `subject` als Objekte mit `name`-Feld.

---

## Query-Parameter: Vorgeschlagene Konventionen

Die Spec definiert alle Query-Parameter als **freie Strings**. Die folgenden Konventionen sind ein **Vorschlag**.
Jedes Backend kann eigene Werte einführen. Ein Backend muss keine dieser Konventionen übernehmen,
sofern es Bericht und Frontend entsprechend dokumentiert.

Die Query-Parameter nutzen häufig dieselben Werte wie die Response-Felder, erweitern sie aber um **Kombinierbarkeit** (kommasepariert).

---

### `type`: Granularität steuern

Der `type`-Parameter bestimmt, welche Art von Value-Groups in der Antwort enthalten sind. Die einzelnen Werte sind unter [Response-Inhalte → type](#type-typ-einer-value-group) beschrieben.

Mehrere Werte können kommasepariert übergeben werden.
Dann liefert der Endpunkt Value-Groups für jede der kombinierten Granularitätsstufen in einer einzigen Antwort.

| Pfad | `type` | Ergebnis | Mock-Server |
|---|---|---|---|
| `/groups/3a-deutsch/competence-levels` | `group,students` | VGs für die Lerngruppe + je SuS | [Link](https://apps.indibit.eu/tba3-api/groups/3a-deutsch/competence-levels?type=group,students) |
| `/states/beispielland/items` | `state,district` | VGs für das Land + je Bezirk | [Link](https://apps.indibit.eu/tba3-api/states/beispielland/items?type=state,district) |

Ohne `type`-Parameter entscheidet das Backend, welche Granularität es standardmäßig liefert.

---

### `comparison`: Vergleichswerte

> **Spec = freier String.** Die Werte und ihre Bedeutung definiert das Backend, nicht die Spec.

Der `comparison`-Parameter steuert, welche Vergleichs-Value-Groups zusätzlich zu den primären Ergebnissen zurückgeliefert werden. Mehrere Werte sind kommasepariert kombinierbar.

**Vorgeschlagene Syntax:** Präfix `typ-id` oder nur `wert`, kommasepariert — z.B. `comparison=group-3b,group-3c,state-average`.
Die Syntax ist im Backend leicht zu parsen und lässt beliebige Kombinationen zu.

#### Vorgeschlagene Comparison-Typen

Die Comparison-Typen leiten sich aus den [`type`-Werten](#type-typ-einer-value-group) ab: Was als `type` in der Response existiert, ergibt in der Regel auch als Vergleichsgruppe Sinn.

| Comparison       | Bedeutung                                                        | Beispiel                |
|------------------|------------------------------------------------------------------|-------------------------|
| `student-<id>`   | Bestimmte:r SuS                                                  | `student-12345`         |
| `group-<id>`     | Bestimmte Lerngruppe                                             | `group-3b`              |
| `group-parallel` | Alle Parallelklassen                                             | `group-parallel`        |
| `school-<id>`    | Bestimmte Schule                                                 | `school-gs-musterstadt` |
| `school-average` | Schulschnitt (Convenience für die Schule der angefragten Gruppe) | `school-average`        |
| `district-<id>`  | Bestimmte Stadt/Gemeinde                                         | `district-nord`         |
| `authority-<id>` | Bestimmtes Schulamt                                              | `authority-12345`       |
| `state-average`  | Landesmittelwert                                                 | `state-average`         |
| `year-<jahr>`    | Vergleich mit einem bestimmten Jahr                              | `year-2024`             |
| `faircomparison` | Fairer Vergleichswert (merkmalsbereinigt)                        | `faircomparison`        |

Jeder Bericht kann darüber hinaus eigene Werte einführen, z.B. Shortcuts, die mehrere Vergleichsgruppen bündeln:

| Shortcut-Beispiel | Bedeutung                                |
|-------------------|------------------------------------------|
| `group-all`       | Alle Lerngruppen (z.B. einer Schule)     |
| `year-last4`      | Die letzten vier Durchgänge              |

#### Beispiele nach Ebene

**Lerngruppen-Ebene (`/groups/{id}/…`):**

| Szenario | Request-Beispiel |
|---|---|
| Parallelklasse(n) | `?comparison=group-3b` oder `?comparison=group-parallel` |
| Schulschnitt | `?comparison=school-average` |
| Landesmittelwert | `?comparison=state-average` |
| Vorjahreswerte | `?comparison=year-2024,year-2023` |
| Kombiniert | `?comparison=state-average,year-2024` |

**Schul-Ebene (`/schools/{id}/…`):**

| Szenario | Request-Beispiel |
|---|---|
| Klassen als Vergleich | `?comparison=group-3a,group-3b` |
| Andere Schule | `?comparison=school-gs-musterstadt` |
| Schuljahresvergleich | `?comparison=year-2024,year-2023` |

**Landes-Ebene (`/states/{id}/…`):**

| Szenario | Request-Beispiel |
|---|---|
| Bezirke als Vergleich | `?comparison=district-nord,district-sued` |
| Schulämter als Vergleich | `?comparison=authority-12345` |

**Hinweis zum Mock-Server:** Der Mock-Server akzeptiert einfache kommaseparierte IDs ohne Typ-Präfix (z.B. `comparison=3b-deutsch`).

---

### `aggregation`: Aggregationsarten

> **Spec = freier String.** Welche Aggregationsarten ein Backend unterstützt, ist nicht durch die Spec vorgegeben.

Der `aggregation`-Parameter ist nur für den `/aggregations`-Endpunkt relevant. Er bestimmt, nach welchen Dimensionen die Ergebnisse aufgeschlüsselt werden.

| Wert | Bedeutung | Mock-Server |
|---|---|---|
| `competence` | Nach Kompetenzen | Implementiert |
| `gender` | Nach Geschlecht der SuS | Implementiert |
| `exercise` | Nach Aufgabe | Nicht implementiert |

Mehrere Werte können kommasepariert kombiniert werden: `aggregation=competence,gender`

Mock-Server-Beispiele:
- [/groups/3a-deutsch/aggregations?aggregation=competence](https://apps.indibit.eu/tba3-api/groups/3a-deutsch/aggregations?aggregation=competence)
- [/groups/3a-deutsch/aggregations?aggregation=gender](https://apps.indibit.eu/tba3-api/groups/3a-deutsch/aggregations?aggregation=gender)

---

### `domain`: Domäne filtern

> **Spec = freier String.** Der Parameter ist in `api/components/parameters.yml` definiert, aber noch nicht an Endpunkte gebunden.

Der `domain`-Parameter filtert die Ergebnisse nach Domäne. Ohne diesen Parameter liefert das Backend Ergebnisse über alle Domänen.
Die Werte und Kürzel sind unter [Response-Inhalte → subject und domain](#subject-und-domain-fach-und-domäne) beschrieben.

Das Fachkürzel ist ein sinnvoller Shortcut: `domain=rs,le` ist inhaltlich gleich zu `domain=de`, wenn in einem Jahr z.B. die Domänen _Orthografie_ und _Leseverstehen_ getestet werden.

**Hinweis zum Mock-Server:** Der Mock-Server liefert `domain`-Felder auf Value-Groups zurück, hat aber keinen serverseitigen Filter implementiert — der Parameter wird ignoriert.

---

## Fehlerverhalten

| HTTP-Status | Bedeutung | Beispiel |
|---|---|---|
| `200` mit leerem Array | Parameter wird verstanden, aber es gibt keine Daten dafür | `?domain=sp` liefert `[]`, weil keine Sprachgebrauch-Daten vorliegen |
| `400 Bad Request` | Syntaktisch ungültige Anfrage (in Spec definiert) | Fehlender Pfad-Parameter |
| `404 Not Found` | Pfad-ID (group, school, state) ist unbekannt | `/groups/unbekannt/competence-levels` |
| `501 Not Implemented` | Backend erkennt einen Query-Parameter-Wert nicht oder unterstützt ihn nicht | `?comparison=pilotierung` → `{ "message": "comparison 'pilotierung' not supported" }` |

`501 Not Implemented` ist die vereinbarte Konvention, wenn ein Backend einen Parameter-Wert prinzipiell nicht unterstützt. Der Response-Body enthält eine erklärende Nachricht. Damit kann ein Frontend zwischen "keine Daten vorhanden" (200 + leeres Array) und "nicht unterstützt" (501) unterscheiden.
