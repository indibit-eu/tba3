# TBA3-Auswertungsschnittstelle: Rezepte

Hier sind Erkenntnisse aus verschiedenen Diskussionen festgehalten, die im Laufe der Schnittstellen Entwicklung
und vor allem Nutzung entstanden sind.

## Umgang mit Kovariaten auf Schüler- und Gruppenebene

### Auf Schülerebene: Covariates direkt an der Value-Group

Auf SuS-Ebene sind Kovariaten eindeutig und werden direkt an der Value-Group mitgeliefert:

```json
{
  "name": "Schüler 1",
  "type": "student",
  "covariates": [
    { "type": "gender", "label": "Geschlecht", "value": "female" },
    { "type": "languageAtHome", "label": "Sprache zu Hause", "value": "german" }
  ],
  "items": []
}
```

### Auf Gruppenebene: Aggregations statt Covariates

Auf Gruppen- oder Schulebene ist eine Kovariate wie "Geschlecht" keine einzelne Ausprägung mehr, sondern eine Verteilung (z.B. 12 weiblich, 8 männlich, 1 divers). Das passt nicht in das `type/label/value`-Schema der Covariates, weil dort ein einzelner Wert erwartet wird.

Stattdessen eignet sich der `/aggregations`-Endpunkt: Er schlüsselt die Ergebnisse nach einer Dimension auf und liefert dabei automatisch die Häufigkeiten mit.

**Request**

```
GET /groups/3a-deutsch/aggregations?aggregation=gender
```

**Antwort**

Die Antwort enthält pro Geschlecht eine Aggregation mit deskriptiver Statistik. Die `descriptiveStatistics` liefern sowohl die Anzahl der SuS in dieser Gruppe (`total` bzw. `frequency`) als auch die mittlere Lösungsquote.

```json
{
  "name": "Klasse 3a",
  "type": "group",
  "domain": { "name": "Leseverstehen" },
  "aggregations": [
    {
      "type": "gender",
      "value": "female",
      "descriptiveStatistics": { "total": 20, "frequency": 12, "mean": 0.72, "standardDeviation": 0.15 }
    },
    {
      "type": "gender",
      "value": "male",
      "descriptiveStatistics": { "total": 20, "frequency": 8, "mean": 0.68, "standardDeviation": 0.18 }
    }
  ]
}
```

### Auf Gruppenebene: Covariates als Einordnung der Gruppe

Kovariaten können auch auf Gruppenebene sinnvoll sein – wenn man nicht die Verteilung innerhalb der Gruppe darstellen will, sondern die Gruppe als Ganzes nach einem Merkmal einordnen möchte.

**Beispiel:** Beim Vergleich mehrerer Klassen soll sichtbar sein, ob die Geschlechterverteilung einen Einfluss auf die Ergebnisse hat. Dafür wird jede Klasse mit einer aggregierten Kovariate versehen:

```json
{
  "name": "Klasse 3a",
  "type": "group",
  "covariates": [
    { "type": "gender", "label": "Geschlechterverteilung", "value": "majority-female" }
  ],
  "competenceLevels": []
}
```

So lassen sich Gruppen nach diesem Merkmal vergleichen oder filtern, ohne die vollständige Verteilung aufschlüsseln zu müssen.

### Zusammenfassung

| Ebene | Ziel | Mechanismus | Beispiel |
|---|---|---|---|
| SuS | Merkmal einer Person | Covariate an der Value-Group | `"value": "female"` |
| Gruppe | Verteilung innerhalb der Gruppe sehen | `/aggregations`-Endpunkt | `?aggregation=gender` |
| Gruppe | Gruppe als Ganzes einordnen | Covariate mit aggregiertem Wert | `"value": "majority-female"` |

---

## Leitideen in Mathematik: Domäne vs. Competences

### Hintergrund

In Deutsch, Französisch und Englisch gibt es in der Regel zwei Domänen (z.B. Leseverstehen und Rechtschreibung), für die jeweils eigene Kompetenzstufen berechnet werden.
Die Responses werden nach Domäne gruppiert – jede Domäne ergibt eine eigene Value-Group.

In Mathematik ist das anders: Aktuell wird in vielen Fällen sowohl in V3 als auch V8 nach dem **Globalmodell** ausgewertet.
Es gibt nur eine Kompetenzstufe für das gesamte Fach.
Der Begriff "Leitidee" wird dabei für zwei verschiedene Konzepte verwendet:

1. **Leitidee als Domäne:** Die Ebene, auf der theoretisch Kompetenzstufen berechnet werden könnten.
2. **Leitidee als Item-Eigenschaft:** Welcher inhaltliche Bereich in einer Aufgabe abgefragt wird. Ein Item kann auch mehreren Leitideen zugeordnet sein.

### Empfehlung

Die Daten in Mathematik **nicht** nach Domäne gruppieren.
Leitideen als inhaltliche Zuordnung stehen in den `competences`-Metadaten an den Items.
Die Response kommt flach zurück, das Frontend kann bei Bedarf über die `competences` gruppieren und darstellen.

Sollte ein System in Mathe nach Leitideen-Domänen auswerten (also Kompetenzstufen je Leitidee berechnen),
steht es ihm frei, die Leitideen als `domain` zu verwenden und die Response entsprechend zu gruppieren. Beides ist spec-konform.

**Beispiel: Items in Mathe**

```
GET /groups/8a-mathe/items
```

```json
[
  {
    "name": "Klasse 8a",
    "type": "group",
    "domain": null,
    "subject": { "name": "Mathematik" },
    "items": [
      {
        "name": "01.02",
        "competences": [{ "name": "L1 - Zahlen und Operationen" }],
        "descriptiveStatistics": { "total": 20, "frequency": 15, "mean": 0.75 }
      },
      {
        "name": "02.01",
        "competences": [{ "name": "L3 - Raum und Form" }],
        "descriptiveStatistics": { "total": 20, "frequency": 12, "mean": 0.60 }
      }
    ]
  }
]
```

Die Value-Group hat hier keine `domain` – die Zuordnung zu Leitideen steckt in den `competences` der einzelnen Items. Ein Frontend, das nach Leitidee gruppieren möchte, kann das lokal tun.

---

## Aggregationen auf verschiedenen Ebenen kombinieren

### Hintergrund

In der Praxis gibt es zwei unabhängige Hierarchien, auf denen Daten aggregiert werden können:

1. **Bildungsstandard:** Items → Aufgaben → Kompetenzbereiche/Leitideen → Domänen → Fach
2. **Gruppe:** SuS → Lerngruppe → Schule → Bezirk → Land

Diese Hierarchien sind orthogonal zueinander: Eine Aggregation nach Kompetenzbereich kann sowohl auf Schülerebene als auch auf Klassenebene erfolgen.

### Umsetzung über die Schnittstelle

Die Kombination von `type` und `aggregation` bildet genau diese Verschachtelung ab:

**Lösungshäufigkeiten nach Leitidee auf Klassenebene:**

```
GET /groups/8a-mathe/aggregations?aggregation=competence
```

Liefert pro Leitidee die mittlere Lösungsquote der Klasse.

**Lösungshäufigkeiten nach Leitidee auf Klassen- und Schülerebene:**

```
GET /groups/8a-mathe/aggregations?type=group,students&aggregation=competence
```

Liefert pro Leitidee die mittlere Lösungsquote der Klasse **und** je SuS. Mit `comparison` lassen sich zusätzlich Referenzwerte (z.B. Pilotierung, Landesmittelwert) ergänzen:

```
GET /groups/8a-mathe/aggregations?type=group,students&aggregation=competence&comparison=state-average
```

### Aufteilen in mehrere Requests

Man muss nicht alles in einen einzigen Request packen. Gerade bei der Kombination mehrerer `type`-Werte können die Responses sehr groß werden.
Stattdessen kann man die Daten in kleinere, übersichtlichere Requests aufteilen – z.B. nach `type` getrennt:

```
GET /groups/8a-mathe/aggregations?type=group&aggregation=competence
GET /groups/8a-mathe/aggregations?type=students&aggregation=competence
```

Das liefert die gleichen Daten wie ein kombinierter Request mit `type=group,students`, aber in kleineren, leichter verarbeitbaren Responses.
Welcher Weg besser passt, hängt vom Anwendungsfall ab.

### Zusammenfassung

| Was                                        | Wie                                                                    |
|--------------------------------------------|------------------------------------------------------------------------|
| Bista-Ebene wählen (z.B. Kompetenzbereich) | `aggregation=competence`                                               |
| Gruppen-Ebene wählen (z.B. Klasse + SuS)   | `type=group,students`                                                  |
| Referenzwerte ergänzen                     | `comparison=state-average`                                             |
| Alles kombinieren                          | `?type=group,students&aggregation=competence&comparison=state-average` |
| Alternativ: aufteilen                      | Separate Requests je `type` für kleinere Responses                     |

