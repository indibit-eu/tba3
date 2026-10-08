# TBA3-Auswertungsschnittstelle: Endpunkt-Referenz

Diese Referenz richtet sich an Frontend- und Backend-Entwickler:innen. Sie beschreibt alle Endpunkte, die die Spec definiert,
sowie die Konventionen, die auf diesen Endpunkten sinnvoll sind.

Grundbegriffe (Value-Group, 3-Schichten-Architektur) sind in [Konzepte und Architektur](konzepte.md) erklärt.

---

## Sprachkonvention

Die Schnittstelle ist in **Englisch** definiert: Feldnamen, Endpunkte und Schlüssel sind englisch (z.B. `competenceLevels`, `descriptiveStatistics`, `frequency`).

**Werte** werden üblicherweise in **Deutsch** übergeben, da sie aus deutschsprachigen Systemen stammen (z.B. `"name": "Regelstandard"`, `"name": "Leseverstehen"`).
Werte, deren Ausprägungen gemeinsam als Konvention definiert sind, können auch Englisch sein (z.B. `"value": "male"` bei Covariates).

---

## Was die Spec definiert

Die Spec definiert **9 Endpunkte**: 3 Ebenen × 3 Datentypen. Jeder Endpunkt gibt ein **Array von Value-Groups** zurück.
Was eine einzelne Value-Group repräsentiert (eine Lerngruppe, ein:e SuS, eine Schule, ein Vergleichswert …),
hängt von der Implementierung des Backends bzw. dem Query-Parameter `type` ab.

Ebenen zwischen Schule und Land (z.B. Schulamt oder Bezirk) sind je Bundesland unterschiedlich und haben daher keine eigenen Endpunkte.
Sie können über `/states/{id}/…` in Kombination mit den Query-Parametern `type` und `filter` abgefragt (→ [`filter`](#filter-ergebnisse-einschränken)) werden.
Damit sind beliebige Zwischenebenen möglich, je nachdem, welche Ebenen es in einem Land gibt.

---

### Kompetenzstufenverteilung (`/competence-levels`)

Jede Value-Group enthält ein `competenceLevels[]`-Array. Jeder Eintrag beschreibt eine Kompetenzstufe (z.B. „Regelstandard") mit zugehöriger deskriptiver Statistik (Häufigkeit, Mittelwert, Gesamtzahl).

| Ebene      | Pfad                              | Value-Group enthält                                      | Swagger-UI                                                                       |
|------------|-----------------------------------|----------------------------------------------------------|----------------------------------------------------------------------------------|
| Lerngruppe | `/groups/{id}/competence-levels`  | `competenceLevels[]` mit Stufen + deskriptiver Statistik | [Link](https://apps.indibit.eu/tba3-api/docs#/groups/getGroupCompetenceLevels)   |
| Schule     | `/schools/{id}/competence-levels` | `competenceLevels[]` mit Stufen + deskriptiver Statistik | [Link](https://apps.indibit.eu/tba3-api/docs#/schools/getSchoolCompetenceLevels) |
| Land       | `/states/{id}/competence-levels`  | `competenceLevels[]` mit Stufen + deskriptiver Statistik | [Link](https://apps.indibit.eu/tba3-api/docs#/states/getStateCompetenceLevels)   |

**Verhalten bei `type=student`:** Auf Schülerebene wird pro SuS nur die **erreichte** Kompetenzstufe zurückgegeben (nicht alle Stufen mit `frequency=0`).
Das `competenceLevels[]`-Array enthält dann in der Regel genau einen Eintrag.

---

### Lösungshäufigkeiten (`/items`)

Jede Value-Group enthält ein `items[]`-Array. Jeder Eintrag beschreibt ein einzelnes Item (Testaufgabe) mit Lösungshäufigkeit und optionalen Item-Parametern.

| Ebene      | Pfad                  | Value-Group enthält                       | Swagger-UI                                                            |
|------------|-----------------------|-------------------------------------------|-----------------------------------------------------------------------|
| Lerngruppe | `/groups/{id}/items`  | `items[]` mit Lösungshäufigkeiten je Item | [Link](https://apps.indibit.eu/tba3-api/docs#/groups/getGroupItems)   |
| Schule     | `/schools/{id}/items` | `items[]` mit Lösungshäufigkeiten je Item | [Link](https://apps.indibit.eu/tba3-api/docs#/schools/getSchoolItems) |
| Land       | `/states/{id}/items`  | `items[]` mit Lösungshäufigkeiten je Item | [Link](https://apps.indibit.eu/tba3-api/docs#/states/getStateItems)   |

---

### Aggregationen (`/aggregations`)

Jede Value-Group enthält ein `aggregations[]`-Array. Jeder Eintrag beschreibt eine Aggregation nach einem bestimmten Typ (z.B. nach Kompetenz oder Geschlecht) mit deskriptiver Statistik. Welche Aggregationsarten verfügbar sind, steuert der `aggregation`-Parameter (→ Query-Parameter).

| Ebene      | Pfad                         | Value-Group enthält                               | Swagger-UI                                                                   |
|------------|------------------------------|---------------------------------------------------|------------------------------------------------------------------------------|
| Lerngruppe | `/groups/{id}/aggregations`  | `aggregations[]` mit Typ + deskriptiver Statistik | [Link](https://apps.indibit.eu/tba3-api/docs#/groups/getGroupAggregations)   |
| Schule     | `/schools/{id}/aggregations` | `aggregations[]` mit Typ + deskriptiver Statistik | [Link](https://apps.indibit.eu/tba3-api/docs#/schools/getSchoolAggregations) |
| Land       | `/states/{id}/aggregations`  | `aggregations[]` mit Typ + deskriptiver Statistik | [Link](https://apps.indibit.eu/tba3-api/docs#/states/getStateAggregations)   |

---

## Response-Inhalte einer Value-Group

Zur Orientierung die Grundstruktur einer Value-Group:

```
Value-Group
├── id           (optional) — Eindeutige Kennung
├── name         (Pflicht)  — Bezeichnung, z.B. "Klasse 8a"
├── type         (Pflicht)  — Typ einer Value Group
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

Die Value-Group hat ein `type`-Feld, das die Granularität beschreibt. So kann ein Berichtselement erkennen,
was eine Value-Group repräsentiert — auch ohne den ursprünglichen Request zu kennen.

| Wert        | Bedeutung      |
|-------------|----------------|
| `student`   | Einzelne:r SuS |
| `group`     | Lerngruppe     |
| `school`    | Schule         |
| `district`  | Stadt/Gemeinde |
| `authority` | Schulamt       |
| `state`     | Bundesland     |

---

### `subject` und `domain`: Fach und Domäne

`subject` und `domain` sind eigene Response-Felder (nicht Properties), weil in Berichten fast immer nach Fach und Domäne gruppiert wird.

`subject` ist ein Objekt mit `id` (optional) und `name` (Pflicht), z.B. `{ name: "Deutsch" }`.
`domain` ist ebenfalls ein Objekt mit `id` (optional) und `name` (Pflicht). Der `name` enthält die lange Beschreibung der Domäne, z.B. `{ name: "Leseverstehen" }`.

Für die **Filter** `subject-<kürzel>` und `domain-<kürzel>` werden Kürzel für Fächer bzw. Teilbereiche eines Fachs verwendet. Die Domänen-Kürzel entsprechen den Domänen-Bezeichnungen aus den Itemkennwerttabellen des IQB ([Kompetenzstufenmodelle](https://www.iqb.hu-berlin.de/de/bista/entwicklung/kompetenzstufenmodelle/)).

| Fach        | Fachkürzel (Filter) | Mögliche Domänen-Kürzel (Filter)                                                                                                                                               |
|-------------|---------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Deutsch     | `de`                | `rs` (Rechtschreibung/Orthografie), `le` (Lesen), `ho` (Zuhören/Sprechen und Zuhören), `sp` (Sprache und Sprachgebrauch/Sprachgebrauch)                                        |
| Mathematik  | `ma`                | V8 keine, V3  `zo` (Zahlen und Operationen), `rf` (Raum und Form), `gm` (Größen und Messen), `dh` (Daten, Häufigkeiten und Wahrscheinlichkeiten), `ms` (Muster und Strukturen) |
| Englisch    | `en`                | `ho` (Hörverstehen), `le` (Leseverstehen)                                                                                                                                      |
| Französisch | `fr`                | `ho` (Hörverstehen), `le` (Leseverstehen)                                                                                                                                      |

**Wichtig: Filter-Kürzel vs. Response-Objekt.** Die Kürzel in der Tabelle oben sind Werte für die **Filter** `subject-<kürzel>` und `domain-<kürzel>` (z.B. `?filter=subject-de,domain-rs`).
Das `domain`-Feld in der **Response** ist dagegen ein Objekt mit der langen Beschreibung, z.B. `{ name: "Rechtschreibung" }`.
Das Backend setzt die lange Beschreibung kontextabhängig — sie kann je nach Jahrgangsstufe variieren (z.B. `rs` = "Rechtschreibung" in der Grundschule, "Orthografie" in der Sek I).

**Gruppierung nach Domäne:** Ob die Response nach Domäne gruppiert wird (eine Value-Group je Domäne) oder flach zurückkommt,
hängt vom Endpunkt und Anwendungsfall ab. Details und Empfehlungen im [Rezept: Gruppierung nach Domäne](rezepte.md#gruppierung-nach-domäne-wann-sinnvoll).

Details und Beispiele zum Sonderfall Mathe in [Rezept: Leitideen in Mathematik](rezepte.md#leitideen-in-mathematik-domäne-vs-competences) beschrieben.

---

### `covariates`: Merkmale Personen(gruppen)

Array von typisierten Merkmalen auf einer Value-Group. Jede Covariate hat `type`, `label`, `value`.

Vordefinierte Typen:

| `type`           | Beschreibung                                      | Beispiel-`value`s                          |
|------------------|---------------------------------------------------|--------------------------------------------|
| `gender`         | Geschlecht                                        | `male`, `female`, `diverse`                |
| `languageAtHome` | Sprache zu Hause                                  | `german`, `other`, `english`, `french`     |
| Beliebig         | Frei erweiterbar — `label` beschreibt das Merkmal | z.B. Schulform, SES, Migrationshintergrund |

Weitere, eigene Kovariaten können im selben Schema ergänzt werden.
Ein Rezept, wie man mit Kovariaten auf anderen Ebenen umgehen kann findet sich in
[Umgang mit Kovariaten auf Schüler- und Gruppenebene](./rezepte.md#umgang-mit-kovariaten-auf-schüler--und-gruppenebene).

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
    "type": "group",
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
    "type": "group",
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

| Pfad                                   | `type`           | Ergebnis                        | Mock-Server                                                                                      |
|----------------------------------------|------------------|---------------------------------|--------------------------------------------------------------------------------------------------|
| `/groups/3a-deutsch/competence-levels` | `group,student`  | VGs für die Lerngruppe + je SuS | [Link](https://apps.indibit.eu/tba3-api/groups/3a-deutsch/competence-levels?type=group,students) |
| `/states/beispielland/items`           | `state,district` | VGs für das Land + je Bezirk    | [Link](https://apps.indibit.eu/tba3-api/states/beispielland/items?type=state,district)           |

Ohne `type`-Parameter entscheidet das Backend, welche Granularität es standardmäßig liefert.

---

### `filter`: Ergebnisse einschränken

> **Spec = freier String.** Welche Filter ein Backend unterstützt, ist nicht durch die Spec vorgegeben.

Der `filter`-Parameter schränkt die Ergebnisse ein. `type` bestimmt, *welche Art* von Value-Groups geliefert wird, `filter` bestimmt, *welche davon*.

**Vorgeschlagene Syntax:** Präfix `typ-id`, kommasepariert — analog zu [`comparison`](#comparison-vergleichswerte), z.B. `filter=testproject-v8-2024,authority-schulamt-nord`.

Typisch sind zwei Arten von Filtern:

- **Teilgruppen-Filter** schränken auf eine Organisationsebene unterhalb des angefragten Endpunkts ein (z.B. `student-<id>`, `authority-<id>`).
- **Kontext-Filter** schränken auf einen fachlichen oder organisatorischen Kontext ein, unabhängig von der Ebene (z.B. `testproject-<id>`, `domain-<kürzel>`).

#### Teilgruppen-Filter

**Faustregel:** Sinnvoll sind Filter auf die Ebenen **unterhalb** des angefragten Endpunkts. Die Präfixe leiten sich aus den [`type`-Werten](#type-typ-einer-value-group) ab.

| Endpunkt     | Sinnvolle `type`s                    | Sinnvolle Teilgruppen-Filter                                                                  |
|--------------|--------------------------------------|-----------------------------------------------------------------------------------------------|
| `/groups/…`  | `student`                            | `student-<id>`                                                                                |
| `/schools/…` | `student`, `group`                   | `student-<id>`, `group-<id>` und weitere Orga-Ebenen der Schule (z.B. Schulzweig, Fachschaft) |
| `/states/…`  | `authority`, `district`, `school`, … | `authority-<id>`, `district-<id>`, `school-<id>`, …                                           |

Beispiele:

| Request                                                                             | Ergebnis                                                    |
|-------------------------------------------------------------------------------------|-------------------------------------------------------------|
| `/groups/3a-deutsch/competence-levels?type=student&filter=student-1234`             | Kompetenzstufe für genau eine:n SuS der Lerngruppe          |
| `/schools/gs-musterstadt/items?type=group&filter=group-3a-deutsch`                  | Lösungshäufigkeiten für genau eine Lerngruppe der Schule    |
| `/states/beispielland/competence-levels?type=authority&filter=district-bezirk-nord` | Kompetenzstufenverteilungen aller Schulämter im Bezirk Nord |
| `/states/beispielland/competence-levels?type=school&filter=authority-schulamt-nord` | Kompetenzstufenverteilungen aller Schulen im Schulamt Nord  |

Welche Zwischenebenen es gibt, ist von Land zu Land unterschiedlich.
Ein Backend unterstützt deshalb nur die Filter für die Ebenen, die es auch kennt (→ [Fehlerverhalten](#fehlerverhalten)).

Filter und `type` auf derselben Ebene sind ebenfalls möglich: `type=authority&filter=authority-schulamt-nord` liefert genau ein Schulamt.

#### Kontext-Filter

| Filter             | Bedeutung                                     | Beispiel                   |
|--------------------|-----------------------------------------------|----------------------------|
| `testproject-<id>` | Bestimmtes Testprojekt / bestimmter Durchgang | `testproject-v8-2024`      |
| `subject-<kürzel>` | Bestimmtes Fach                               | `subject-de`, `subject-ma` |
| `domain-<kürzel>`  | Bestimmte Domäne                              | `domain-le`, `domain-ho`   |

Die Kürzel für `subject` und `domain` sind unter [Response-Inhalte → subject und domain](#subject-und-domain-fach-und-domäne) beschrieben.
Ohne `subject`- oder `domain`-Filter liefert das Backend Ergebnisse über alle Fächer bzw. Domänen.

#### Kombination mehrerer Filter

Wie mehrere Filter kombiniert werden, entscheidet am Ende das Backend. Vorgeschlagen wird:

- **Gleiches Präfix → ODER:** `filter=group-3a-deutsch,group-3b-deutsch` liefert beide Lerngruppen.
- **Verschiedene Präfixe → UND:** `filter=testproject-v8-2024,student-1234` liefert die Ergebnisse von SuS 1234 im Testprojekt V8 2024.

so können auch mehrdeutige Domänen-Kürzel eindeutig angefragt werden: `le` gibt es in Deutsch, Englisch und Französisch.
`filter=subject-en,domain-le` liefert nur Leseverstehen in Englisch.

#### Wirkung auf Vergleichswerte

Auch das entscheidet im Konkreten das Backend. **Faustregel:**

- **Kontext-Filter** gelten für die gesamte Antwort, also auch für die Vergleichswerte.
- **Teilgruppen-Filter** gelten nur für die primären Value-Groups. `?type=student&filter=student-1234&comparison=group-3b` liefert SuS 1234 und die vollständige Vergleichsgruppe 3b.

**Hinweis zum Mock-Server:** Der Mock-Server hat den `filter`-Parameter noch nicht implementiert.

---

**Abgrenzung:** `filter` schränkt die angefragten Value-Groups ein. `comparison` liefert **zusätzliche** Value-Groups für andere Gruppen.

---

### `comparison`: Vergleichswerte

> **Spec = freier String.** Die Werte und ihre Bedeutung definiert das Backend, nicht die Spec.

Der `comparison`-Parameter steuert, welche Vergleichs-Value-Groups zusätzlich zu den primären Ergebnissen zurückgeliefert werden.
Mehrere Werte sind kommasepariert kombinierbar.

**Vorgeschlagene Syntax:** Präfix `typ-id` oder nur `wert`, kommasepariert — z.B. `comparison=group-3b,group-3c,state-average`.
Die Syntax ist im Backend leicht zu parsen und lässt beliebige Kombinationen zu.

**Faustregel**: Wenn nur der `type` angegeben wird, entscheidet in der Regel das Backend, welche Vergleichsgruppen geliefert werden.
Wenn konkrete Vergleichsgruppen erwünscht sind, werden diese mit `type-<id>` referenziert.

#### Vorgeschlagene Comparison-Typen

Die Comparison-Typen leiten sich aus den [`type`-Werten](#type-typ-einer-value-group) ab: Was als `type` in der Response existiert, ergibt in der Regel auch als Vergleichsgruppe Sinn.

| Comparison       | Bedeutung                                                        | Beispiel                |
|------------------|------------------------------------------------------------------|-------------------------|
| `student-<id>`   | Bestimmte:r SuS                                                  | `student-12345`         |
| `group-<id>`     | Bestimmte Lerngruppe                                             | `group-3b`              |
| `school-<id>`    | Bestimmte Schule                                                 | `school-gs-musterstadt` |
| `school-average` | Schulschnitt (Convenience für die Schule der angefragten Gruppe) | `school-average`        |
| `district-<id>`  | Bestimmte Stadt/Gemeinde                                         | `district-nord`         |
| `authority-<id>` | Bestimmtes Schulamt                                              | `authority-12345`       |
| `state-average`  | Landesmittelwert                                                 | `state-average`         |
| `year-<jahr>`    | Vergleich mit einem bestimmten Jahr                              | `year-2024`             |

Jeder Bericht kann darüber hinaus eigene Werte einführen, z.B. für besondere Vergleichsgruppen oder Shortcuts,
die mehrere Vergleichsgruppen bündeln:

| Shortcut-Beispiel       | Bedeutung                                                                       |
|-------------------------|---------------------------------------------------------------------------------|
| `group`                 | Backend trifft Entscheidung, z.B. alle Lerngruppen einer Schule                 |
| `group-parallel`        | Alle Parallelklassen                                                            | 
| `year`                  | Backend trifft Entscheidung, z.B. die letzten vier Durchgänge                   |
| `faircomparison`        | Fairer Vergleichswert (merkmalsbereinigt). Das Backend wählt die passende Ebene |
| `group-faircomparison`  | Fairer Vergleichswert auf Gruppenebene                                          |
| `school-faircomparison` | Fairer Vergleichswert auf Schulebene                                            |

#### Beispiele nach Ebene

**Lerngruppen-Ebene (`/groups/{id}/…`):**

| Szenario          | Request-Beispiel                                                           |
|-------------------|----------------------------------------------------------------------------|
| Parallelklasse(n) | `?comparison=group-3b,group-3c,group-3d` oder `?comparison=group-parallel` |
| Schulschnitt      | `?comparison=school-average`                                               |
| Landesmittelwert  | `?comparison=state-average`                                                |
| Vorjahreswerte    | `?comparison=year-2024,year-2023`                                          |
| Kombiniert        | `?comparison=state-average,year-2024`                                      |

**Schul-Ebene (`/schools/{id}/…`):**

| Szenario              | Request-Beispiel                                  |
|-----------------------|---------------------------------------------------|
| Klassen als Vergleich | `?comparison=group-3a,group-3b,group-3c,group-3d` |
| Andere Schule         | `?comparison=school-gs-musterstadt`               |
| Schuljahresvergleich  | `?comparison=year-2024,year-2023`                 |

**Landes-Ebene (`/states/{id}/…`):**

| Szenario                 | Request-Beispiel                          |
|--------------------------|-------------------------------------------|
| Bezirke als Vergleich    | `?comparison=district-nord,district-sued` |
| Schulämter als Vergleich | `?comparison=authority-12345`             |

**Hinweis zum Mock-Server:** Der Mock-Server akzeptiert aktuell einfache kommaseparierte IDs ohne Typ-Präfix (z.B. `comparison=3b-deutsch`).

---

**Abgrenzung:** `comparison` liefert Werte für **andere Gruppen** (z.B. Parallelklasse, Landesmittelwert). `aggregation` liefert **andere Sichten auf dieselbe Gruppe** (z.B. aufgeschlüsselt nach Kompetenz oder Geschlecht).

### `aggregation`: Aggregationsarten

> **Spec = freier String.** Welche Aggregationsarten ein Backend unterstützt, ist nicht durch die Spec vorgegeben.

Der `aggregation`-Parameter ist nur für den `/aggregations`-Endpunkt relevant. Er bestimmt, nach welchen Dimensionen die Ergebnisse aufgeschlüsselt werden.

| Wert         | Bedeutung               | Mock-Server         |
|--------------|-------------------------|---------------------|
| `competence` | Nach Kompetenzen        | Implementiert       |
| `gender`     | Nach Geschlecht der SuS | Implementiert       |
| `exercise`   | Nach Aufgabe            | Nicht implementiert |

Mehrere Werte können kommasepariert kombiniert werden: `aggregation=competence,gender`

Mock-Server-Beispiele:
- [/groups/3a-deutsch/aggregations?aggregation=competence](https://apps.indibit.eu/tba3-api/groups/3a-deutsch/aggregations?aggregation=competence)
- [/groups/3a-deutsch/aggregations?aggregation=gender](https://apps.indibit.eu/tba3-api/groups/3a-deutsch/aggregations?aggregation=gender)

---

## Fehlerverhalten

| HTTP-Status            | Bedeutung                                                                   | Beispiel                                                                              |
|------------------------|-----------------------------------------------------------------------------|---------------------------------------------------------------------------------------|
| `200` mit leerem Array | Parameter wird verstanden, aber es gibt keine Daten dafür                   | `?filter=domain-sp` liefert `[]`, weil keine Sprachgebrauch-Daten vorliegen           |
| `400 Bad Request`      | Syntaktisch ungültige Anfrage (in Spec definiert)                           |                                                                                       |
| `404 Not Found`        | Pfad-ID (group, school, state) ist unbekannt                                | `/groups/unbekannt/competence-levels`                                                 |
| `501 Not Implemented`  | Backend erkennt einen Query-Parameter-Wert nicht oder unterstützt ihn nicht | `?comparison=pilotierung` → `{ "message": "comparison 'pilotierung' not supported" }` |

`501 Not Implemented` ist die vereinbarte Konvention, wenn ein Backend einen Parameter-Wert prinzipiell nicht unterstützt.
Der Response-Body enthält eine erklärende Nachricht. Damit kann ein Frontend zwischen "keine Daten vorhanden" (200 + leeres Array) und "nicht unterstützt" (501) unterscheiden.

Für `filter` gilt entsprechend:

- **Präfix wird nicht unterstützt** → `501`, z.B. `?filter=district-bezirk-nord` bei einem Backend, das keine Bezirke kennt.
- **Präfix wird unterstützt, die Id ist aber unbekannt** → `200` mit leerem Array. `404` bleibt für unbekannte Pfad-IDs reserviert.
