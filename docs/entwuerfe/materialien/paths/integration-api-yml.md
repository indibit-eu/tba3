# Integrationsskizze: Ergänzungen zu `api/api.yml`

Damit sich die Materialien-Erweiterung in die bestehende Spec einfügt, müssten in
`api/api.yml` folgende Ergänzungen erfolgen (hier nur als Referenz — der Entwurf
selbst greift nicht in die Spec ein):

```yaml
tags:
  - name: groups
    description: Ergebnisse auf Ebene einer Lerngruppe
  - name: schools
    description: Ergebnisse zusammengefasst nach Schule
  - name: states
    description: Ergebnisse auf Landesebene
  - name: materials           # NEU
    description: Begleitmaterialien zu Tests, Aufgaben, Items, Kompetenzen und Kompetenzstufen

paths:
  # ... bestehende Pfade ...

  /materials:                 # NEU
    $ref: 'paths/materials/list.yml'
  /materials/{id}:            # NEU
    $ref: 'paths/materials/by-id.yml'
```

Optional (Convenience-Schicht pro Ebene):

```yaml
  /groups/{id}/materials:     # OPTIONAL
    $ref: 'paths/groups/materials.yml'
  /schools/{id}/materials:    # OPTIONAL
    $ref: 'paths/schools/materials.yml'
  /states/{id}/materials:     # OPTIONAL
    $ref: 'paths/states/materials.yml'
```

Zusätzlich müssten die bestehenden Schemas ergänzt werden. Beispiel für
`api/components/schemas/competence-level.yml`:

```yaml
type: object
required:
  - nameShort
properties:
  # ... bestehende Felder ...
  materials:                  # NEU, optional
    type: array
    description: Materialien, die an diese Kompetenzstufe gebunden sind (kompakte Referenzen)
    items:
      $ref: './material-reference.yml'
```

Analog in `value-group.yml`, `exercise.yml`, `item.yml`, `competence.yml`.

Alle Ergänzungen sind **additiv** — bestehende Backends und Frontends bleiben spec-konform,
auch wenn sie die Materialien nicht kennen.
