# Entwurf: Materialien-Erweiterung für TBA3

> Status: **Vorschlag / Entwurf** — nicht Teil der offiziellen Spec.
> Zweck: Zur Diskussion stellen, wie Begleitmaterialien (Handreichungen, Fördermaterial,
> Diagnosehinweise, Lesetexte, Audio/Video, Beispiel­lösungen, …) über die TBA3-Schnittstelle
> übertragen werden können.

Dieses Dokument beschreibt eine vorgeschlagene additive Erweiterung der
TBA3-Auswertungsschnittstelle um einen eigenen Ressourcentyp **Material**. Materialien
können an verschiedene Bezugspunkte geknüpft werden:

- den **Test** als Ganzes,
- eine **Leitidee** bzw. allgemein eine Kompetenz,
- einzelne **Aufgaben** (`exercise`),
- einzelne **Items** / Lösungshäufigkeiten,
- **Kompetenzstufen**,
- oder **allgemein** (ohne spezifischen Bezug, z. B. didaktische Hinweise zum gesamten
  Vergleichsarbeitenwesen).

Die Erweiterung ist so gestaltet, dass sie sich nahtlos in die bestehende Zweiteilung
„OpenAPI-Spec (formeller Vertrag)" + „Inhaltlicher Vertrag" (siehe
[`docs/konzepte.md`](../../konzepte.md)) einfügt.

---

## 1 · Motivation

Die aktuelle TBA3-Spec deckt die statistische Auswertung ab (Kompetenzstufen­verteilungen,
Lösungshäufigkeiten, Aggregationen). In Berichten werden aber regelmäßig zusätzlich
**Materialien** benötigt, die über die reinen Zahlen hinausgehen, z. B.:

| Kontext                             | Typisches Material                                       |
| ----------------------------------- | -------------------------------------------------------- |
| Test als Ganzes                     | Durchführungs­handreichung, Antwortbogen, Transkripte    |
| Leitidee / Kompetenz                | Fachdidaktische Einordnung, Fördervorschläge             |
| Aufgabe (`exercise`)                | Ursprüngliche Aufgabenkarte, Lösungsbeispiele            |
| Einzelnes Item / Lösungshäufigkeit  | Musterlösung, typische Fehlermuster, Hinweis für Lehrkr. |
| Kompetenzstufe                      | Fördermaterial für diese Stufe, Beispielaufgaben         |
| Allgemein                           | VERA-Erklärtext, Eltern-Informationen                    |

Aktuell wird dieses Material entweder außerhalb der Schnittstelle geliefert oder
systemspezifisch in `properties` transportiert. Beides erschwert den Austausch von
Berichtselementen zwischen Backends erheblich.

Ziel dieser Erweiterung: **ein einheitlicher, flexibler und additiver Weg, Materialien
zusammen mit Auswertungsdaten auszuliefern — ohne die bestehende Spec zu brechen.**

---

## 2 · Design-Leitplanken

1. **Additiv & rückwärtskompatibel**: Alle neuen Felder sind optional. Ein Backend, das
   keine Materialien anbietet, bleibt spec-konform; ein Frontend, das Materialien nicht
   kennt, kann sie ignorieren.
2. **Ein Material — viele Bezüge**: Dasselbe Material kann an mehrere Entitäten geknüpft
   sein (z. B. „Förderheft Leseverstehen" ist verknüpft mit *Kompetenzstufe II* **und**
   *Leitidee Lesen*).
3. **Referenzielle Kompaktheit**: In Antworten werden Materialien standardmäßig nur als
   kompakte Referenz (`MaterialReference`) eingebettet. Die vollständige Material-Ressource
   ist über einen eigenen Endpunkt erreichbar — das hält Auswertungs­responses schlank.
4. **Zwei Zugriffswege**: Materialien können sowohl **eingebettet** (im Kontext der
   Auswertungsdaten) als auch **eigenständig** über einen `/materials`-Endpunkt abgefragt
   werden.
5. **Stufen-Modell analog zu Konzepte.md**:
   - *Stufe 1* — Spec-konformer `/materials`-Endpunkt mit Filtern. Frontend kann Materialien
     generisch listen/darstellen.
   - *Stufe 2* — Konventionen für `kind`, `audience`, `attachments[].scope` usw. sind
     dokumentiert; Berichtselemente können Materialien semantisch platzieren.
6. **Offenheit**: Alle typisierenden Felder (`kind`, `audience`, `scope`, …) sind offene
   Strings mit empfohlenen Werten — analog zu `type`, `comparison`, `aggregation` in der
   bestehenden Spec.

---

## 3 · Datenmodell

### 3.1 · `Material`

Eine **eigenständige Ressource** mit ID. Trägt den Inhalt (bzw. URL) und eine Liste von
`attachments`, die die Verknüpfung(en) zu bestehenden Entitäten beschreiben.

```text
Material
├── id             (Pflicht)  Eindeutige Kennung
├── title          (Pflicht)  Kurzer Titel
├── description    (optional) Längere Beschreibung
├── kind           (Pflicht)  Art des Materials (siehe Tabelle)
├── format         (optional) MIME-Typ, z. B. 'application/pdf'
├── language       (optional) BCP47, z. B. 'de', 'de-DE', 'en'
├── url            (Pflicht*) Direktlink (kann auth-pflichtig sein)
├── content        (optional) Inline-Inhalt für kurze Materialien (HTML/Markdown/Text)
├── thumbnailUrl   (optional)
├── size           (optional) Bytes
├── duration       (optional) Sekunden (für Audio/Video)
├── license        (optional) SPDX-Kennung oder Freitext
├── source         (optional) z. B. 'IQB', 'VERA', 'Schulträger-XY'
├── version        (optional)
├── audience       (optional) 'teacher' | 'student' | 'parents' | 'other'
├── tags[]         (optional) Freitext-Schlagworte
├── properties[]   (optional) Key-Value-Erweiterungen (wie in value-group.yml)
└── attachments[]  (Pflicht)  Bezugspunkte — siehe 3.2
```

*) Entweder `url` **oder** `content` muss vorhanden sein.

**Vorgeschlagene Werte für `kind`** (Stufe-2-Konvention, erweiterbar):

| `kind`           | Bedeutung                                                  |
| ---------------- | ---------------------------------------------------------- |
| `support`        | Förder-/Übungsmaterial                                     |
| `diagnostic`     | Diagnosehinweise für Lehrkräfte                            |
| `didactic`       | Fachdidaktische Einordnung, Handreichung                   |
| `anchor-text`    | Aufgabentext / Lesetext / Hörtext                          |
| `solution`       | Musterlösung, Erwartungshorizont                           |
| `example`        | Beispielaufgabe ähnlicher Art                              |
| `audio`          | Audiodatei (Hörverstehen)                                  |
| `video`          | Videomaterial                                              |
| `transcript`     | Transkript zu Audio/Video                                  |
| `info`           | Allgemeiner Erklärtext (für SuS, Eltern, Öffentlichkeit)   |
| `other`          | Sonstiges — `title` / `description` beschreiben das Näher. |

### 3.2 · `MaterialAttachment` — die Verknüpfung

Ein Material trägt **einen oder mehrere** `attachments`. Jeder Eintrag beschreibt genau
einen Bezugspunkt:

```text
MaterialAttachment
├── scope     (Pflicht)   'test' | 'exercise' | 'item' | 'competence'
│                         | 'competence-level' | 'general'
├── refId     (bedingt)   ID der verknüpften Entität (Pflicht außer bei 'general')
├── refName   (optional)  Lesbare Kennung, falls hilfreich (z. B. '2.5.1', 'Ia')
├── refKind   (optional)  Qualifier bei mehrdeutigen IDs, z. B. 'iqbId' vs. 'internalId'
├── subject   (optional)  Fach, falls verknüpft (Objekt wie in value-group.yml)
├── domain    (optional)  Domäne, falls verknüpft
└── properties[] (optional) Freie Key-Value-Metadaten zur Verknüpfung
```

**Warum eine Liste von Attachments (nicht getrennte Felder wie `testId`, `exerciseId`, …)?**

- Ein Material kann mehrfach zugeordnet sein. Eine Liste ist dafür das natürliche Modell.
- Neue `scope`-Werte sind rückwärtskompatibel ergänzbar (konsistent zu den bestehenden
  offen-String-Konventionen in der Spec).
- Frontends können einheitlich über `attachments[]` iterieren, statt mehrere
  Sonderfall-Felder zu behandeln.

**`scope`-Werte im Detail**

| `scope`            | `refId` verweist auf                                  | Typischer Use-Case                              |
| ------------------ | ----------------------------------------------------- | ----------------------------------------------- |
| `test`             | Test-/Testheft-Kennung (z. B. `V8-2024-DE-TH01`)      | Handreichung zum Gesamttest                     |
| `exercise`         | `exercise.id`                                         | Materialien zur Aufgabe                         |
| `item`             | `item.id` **oder** `item.iqbId` (mit `refKind`)       | Musterlösung zu einem Item                      |
| `competence`       | `competence.id` (Kompetenz oder Leitidee)             | Fördermaterial zu einer Leitidee                |
| `competence-level` | `competence-level.id` **oder** `competence-level.nameShort` | Fördermaterial je Stufe                  |
| `general`          | —                                                     | Allgemeine Erklärtexte, Eltern-Informationen    |

### 3.3 · `MaterialReference` — kompakte Einbettung

In Auswertungs­responses werden Materialien **nicht vollständig** eingebettet, sondern nur
als kompakte Referenz (ID + Mini-Metadaten), damit die Antworten schlank bleiben. Das volle
Objekt ist über `GET /materials/{id}` abrufbar.

```text
MaterialReference
├── id       (Pflicht)  Verweist auf Material.id
├── title    (optional) Für Anzeige ohne Nachladen
├── kind     (optional) Für Icon/Filter ohne Nachladen
├── url      (optional) Direktlink (wenn ohne Vorverarbeitung nutzbar)
└── audience (optional)
```

Ein Backend kann wahlweise nur `id` liefern (Frontend lädt nach) oder zusätzlich
`title`/`kind`/`url` vorab mitgeben.

Siehe YAML-Skizzen unter [`./schemas/`](./schemas/).

---

## 4 · Endpunkte

### 4.1 · `GET /materials` — generische Materialsuche

Einen einzigen neuen Endpunkt. Filter über Query-Parameter:

| Parameter          | Typ                | Beschreibung                                                       |
| ------------------ | ------------------ | ------------------------------------------------------------------ |
| `scope`            | `string` (komma-sep) | Filter auf Attachment-Scopes (`test,exercise,item,competence,competence-level,general`) |
| `test`             | `string`           | Testheft-Kennung                                                   |
| `exercise`         | `string`           | Aufgabe-ID                                                         |
| `item`             | `string`           | Item-ID oder `iqbId:AB1021`                                        |
| `competence`       | `string`           | Kompetenz-ID (Leitidee, Kompetenz)                                 |
| `competenceLevel`  | `string`           | Kompetenzstufen-ID oder `nameShort:Ia`                             |
| `subject`          | `string`           | Fachkürzel (`de`, `ma`, …) — analog bestehender `domain`-Parameter |
| `domain`           | `string`           | Domäne (`le`, `rs`, …)                                             |
| `kind`             | `string` (komma-sep) | Material-Arten                                                     |
| `language`         | `string`           | BCP47                                                              |
| `audience`         | `string`           | `teacher`, `student`, `parents`, …                                 |

Antwort: `200` mit Array von `Material`-Objekten.

Kombinierbar: `?scope=competence-level&competenceLevel=nameShort:Ia&audience=teacher`.

### 4.2 · `GET /materials/{id}` — Einzelabruf

Für den Fall, dass in Auswertungs­responses nur eine `MaterialReference` (id) kam und das
Frontend das vollständige Material nachladen will.

### 4.3 · Optional: kontextsensitive Materialien pro Berichtsebene

Als Ergänzung — **nicht zwingend Teil der Mindestversion**:

```
GET /groups/{id}/materials
GET /schools/{id}/materials
GET /states/{id}/materials
```

Diese Endpunkte können ergebnisorientiert filtern, z. B. „Liefere alle Fördermaterialien,
die zu den tatsächlich auffälligen Items / Stufen der Klasse 8a passen." Die Entscheidung,
welche Materialien „passen", trifft das Backend. Antwort identisch zu `/materials`.

Diese Endpunkte sind eine Convenience-Schicht: semantisch gleichwertig zu
`GET /materials?…` mit passenden Filtern, sparen dem Frontend aber die Auswertungslogik.

### 4.4 · Einbettung in bestehende Responses

Zusätzlich zu den Endpunkten wird ein optionales Feld `materials[]` (Array von
`MaterialReference`) an folgenden Stellen vorgesehen:

| Ort                                                 | Bedeutung                                                   |
| --------------------------------------------------- | ----------------------------------------------------------- |
| `value-group.yml`                                   | Materialien mit Bezug zur gesamten Wertegruppe / zum Test   |
| `exercise.yml`                                      | Materialien zur Aufgabe                                     |
| `item.yml` (damit auch in `/items`-Response)        | Materialien zum Item (Musterlösung, Fehlermuster)           |
| `competence.yml` (via `aggregations`)               | Materialien zu Kompetenz/Leitidee                           |
| `competence-level.yml` (via `/competence-levels`)   | Materialien je Stufe                                        |

Bei hoher Materialanzahl **sollte** das Backend hier nur die wichtigsten oder gar keine
Referenzen inline liefern und auf `/materials?…` verweisen — Analogie zu Paginierung.

---

## 5 · Fehlerverhalten

Konsistent zu den Konventionen aus der Endpunkt-Referenz:

| HTTP            | Bedeutung                                                                     |
| --------------- | ----------------------------------------------------------------------------- |
| `200` + `[]`    | Filter verstanden, aber keine passenden Materialien vorhanden                 |
| `400`           | Syntaktisch ungültige Anfrage                                                 |
| `404`           | `/materials/{id}` — Material nicht gefunden                                   |
| `501`           | Backend unterstützt einen Filter-Wert prinzipiell nicht (z. B. unbekanntes `scope`) |

---

## 6 · Beispiele

Konkrete JSON-Beispiele liegen unter [`./beispiele/`](./beispiele/):

- [`material-list.json`](./beispiele/material-list.json) — Response von `GET /materials?scope=competence-level&competenceLevel=nameShort:Ia`
- [`competence-levels-with-materials.json`](./beispiele/competence-levels-with-materials.json) — `/groups/{id}/competence-levels` mit eingebetteten `materials[]`-Referenzen pro Stufe
- [`items-with-materials.json`](./beispiele/items-with-materials.json) — `/groups/{id}/items` mit Musterlösungs-Referenzen pro Item

---

## 7 · YAML-Schema-Skizzen

Die OpenAPI-YAML-Dateien liegen unter [`./schemas/`](./schemas/) bzw. [`./paths/`](./paths/)
und folgen demselben Aufbau wie `api/components/schemas/` im Hauptverzeichnis.

Für eine Integration in die offizielle Spec wären folgende Schritte nötig:

1. `api/components/schemas/material.yml`, `material-attachment.yml`,
   `material-reference.yml` anlegen (kopiert aus `./schemas/`).
2. `api/paths/materials/list.yml` und `api/paths/materials/by-id.yml` anlegen.
3. In `api/api.yml` die neuen Pfade und einen neuen Tag `materials` registrieren.
4. Die bestehenden Schemas `value-group.yml`, `exercise.yml`, `item.yml`, `competence.yml`,
   `competence-level.yml` um ein optionales `materials`-Feld ergänzen.
5. Parameter-Definitionen in `api/components/parameters.yml` ergänzen.

---

## 8 · Verhältnis zu LOM, LRMI und AMB

Für Bildungs­ressourcen existieren etablierte Metadatenstandards, die in großen
OER-Infrastrukturen (edu-sharing, WirLernenOnline, Deutscher Bildungsserver, Mundo, …)
bereits verwendet werden:

| Standard     | Beschreibung                                                                   |
| ------------ | ------------------------------------------------------------------------------ |
| **LOM**      | IEEE 1484.12.1 *Learning Object Metadata* — umfangreich, XML-geprägt, ~80 Felder |
| **LRMI**     | *Learning Resource Metadata Initiative* — auf schema.org aufsetzende, schlanke Erweiterung; JSON-LD-freundlich |
| **AMB**      | *Allgemeines Metadatenprofil für Bildungsressourcen* der DINI-AG KIM — deutsches Anwendungsprofil von LRMI/schema.org; in DE der De-facto-Standard für neue OER-Plattformen |

### Warum TBA3 diese Standards **nicht nachbaut**

Die TBA3-Spec folgt dem Leitbild aus [`konzepte.md`](../../konzepte.md):
Stufe 3 (vollständige Standardisierung) ist bewusst nicht das Ziel. LOM/LRMI in
voller Breite in der Auswertungs­schnittstelle abzubilden würde

- Backends zwingen, Metadatenfelder zu produzieren, die kein Frontend anzeigt,
- eine zweite parallele Modellierung neben `attachments[]`/`properties` schaffen,
- die Bindung an ein spezifisches Bildungs­metadaten-Ökosystem erzwingen, obwohl
  TBA3 primär eine *Auswertungs*­schnittstelle ist.

### Warum ein schlanker Brückenmechanismus trotzdem sinnvoll ist

Materialien, die in der Rückmeldung erscheinen, existieren oft schon in einem
LRMI/AMB-konformen Repository. Frontends im OER-Ökosystem profitieren, wenn sie auf den
reichen Metadatensatz durchgreifen können, ohne ihn in TBA3 zu duplizieren.

### Lösung: drei kleine Brückenpunkte

**1. `Material.externalMetadata[]`** — optionaler Verweis auf externe Metadatensätze.

```json
"externalMetadata": [
  {
    "schema": "amb",
    "url": "https://wirlernenonline.de/entry/9a21ad44.jsonld",
    "mediaType": "application/ld+json"
  }
]
```

Kosten: ein optionales Array. Nutzen: LRMI-fähige Frontends dereferenzieren bei Bedarf
und erhalten den vollen AMB-Datensatz. Schlichte Frontends ignorieren das Feld.

**2. `MaterialAttachment.refKind: 'curriculumUri'`** — Bezugspunkte dürfen als URI aus
einem Kompetenz-/Curriculum-Vokabular angegeben werden (z. B. aus dem KMK-Bildungs­standards-
oder Lehrplan-Vokabular). Diese URIs passen ohne Umrechnung in LRMI/AMB
`alignmentObject.targetUrl` (`alignmentType ∈ {teaches, assesses, requires, …}`).

```json
{
  "scope": "competence",
  "refId": "https://w3id.org/kim/schulfaecher/s1002",
  "refKind": "curriculumUri",
  "refName": "Leitidee Lesen"
}
```

**3. `Material.kind` als Stufe-2-Konvention an AMB/LRMI-`learningResourceType` angelehnt**

`kind` bleibt ein kleines, kontrolliertes Vokabular für einfache Berichtselemente
(Icon/Filter/Platzierung). Wer feingranularere Klassifikation braucht, nutzt
`externalMetadata` und erhält dort `learningResourceType` aus einem Vokabular wie
`https://w3id.org/kim/hcrt/`.

Empfohlenes Mapping:

| TBA3 `kind`    | AMB / LRMI `learningResourceType` (Vokabular `w3id.org/kim/hcrt/`) | Bemerkung                   |
| -------------- | ------------------------------------------------------------------ | --------------------------- |
| `support`      | `worksheet`, `exercise`, `drill_and_practice`                      | Feinere Unterscheidung via externalMetadata |
| `didactic`     | `teaching_module`, `guide`, `lesson_plan`                          |                             |
| `anchor-text`  | `text`, `reading`                                                  | Lesetext/Aufgabenstamm      |
| `solution`     | `assessment` + Zusatzkontext im LRMI-Datensatz (`solution`)        | LRMI `EducationalAssessment` bietet mehr Felder |
| `example`      | `assessment`, `case_study`                                         |                             |
| `audio`        | `audio`                                                            | 1:1                         |
| `video`        | `video`                                                            | 1:1                         |
| `transcript`   | `transcript`                                                       | 1:1                         |
| `info`         | `web_page`, `other`                                                |                             |
| `other`        | `other`                                                            |                             |

### Was das NICHT ist

- **Kein LOM-Parser in der Spec.** TBA3 definiert nur, *dass* verlinkt werden kann,
  nicht *wie* LRMI/AMB selbst aufgebaut ist — dafür gilt der jeweilige Standard.
- **Keine Pflicht.** Ein Backend ohne OER-Anbindung lässt `externalMetadata` einfach weg.
- **Keine Datenkopie.** Die TBA3-Kernfelder (`title`, `kind`, `url`, `license`, …)
  bleiben die kanonische Quelle für das, was in einem TBA3-Bericht gezeigt wird.
  `externalMetadata` ist nur eine Brücke, keine Schattenkopie.

---

## 9 · Offene Punkte / Diskussion

- **Authentifizierung von `url`**: Muss ein Frontend mit der gleichen Auth wie die TBA3-API
  auf die Material-URL zugreifen können? Vorschlag: Offenlassen; Backend dokumentiert
  Verhalten (z. B. pre-signed URLs).
- **Caching / Versionierung**: Sollten Materialien ETag/Last-Modified tragen? Vorschlag:
  HTTP-Standardheader nutzen, nichts Zusätzliches in der Spec.
- **Inline vs. URL**: Wann sollte `content` (Inline) statt `url` genutzt werden?
  Vorschlag: Nur für kleine, selbstenthaltende Texte (z. B. kurze Hinweise ≤ 5 KB).
- **Mehrsprachigkeit**: Reicht `language` pro Material, oder sollte ein Material
  Übersetzungen als Varianten tragen? Vorschlag: Ein Material pro Sprache, Übersetzungen
  via gemeinsame `tags` oder `properties[key=translationOf]` verknüpfen.
- **Reihenfolge/Relevanz**: Soll `MaterialReference` eine `relevance` oder `priority`
  tragen? Oder sortiert das Backend implizit?
- **`test`-Scope**: Soll `test` eine eigene Entität in der Spec werden, oder reicht ein
  freier String als `refId`? Vorschlag: Freier String (analog Booklets in `properties`).
- **Zusammenspiel mit `properties`**: Dürfen Materialien auch in Value-Group-`properties`
  weiterhin als Link gelistet werden? Vorschlag: Ja, aber `materials[]` ist für neue
  Implementierungen der kanonische Ort.

---

## 10 · Zusammenfassung

Die vorgeschlagene Erweiterung

- führt **eine neue Ressource** `Material` mit frei definierbaren Bezugspunkten
  (`attachments[]`) ein,
- ergänzt die Spec um **einen zwingenden neuen Endpunkt** `GET /materials` (+
  `/materials/{id}`) und eine **optionale Convenience-Schicht** pro Ebene,
- erweitert bestehende Schemas **rückwärtskompatibel** um ein optionales
  `materials[]`-Referenzfeld,
- bietet über `externalMetadata[]`, `refKind: curriculumUri` und ein AMB-nahes
  `kind`-Vokabular eine **schlanke Brücke zu LRMI/AMB/LOM**, ohne diese Standards
  in der Spec nachzubauen,
- bleibt der Spec-Philosophie („offen wo möglich, Konventionen wo sinnvoll") treu.

Damit können Berichte und Berichtselemente neben den reinen Auswertungsdaten auch das
zugehörige Begleit- und Fördermaterial einheitlich konsumieren — sowohl testweit als auch
präzise an Leitidee, Aufgabe, Item, Lösungshäufigkeit oder Kompetenzstufe hängend.
