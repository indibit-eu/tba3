# TBA III Auswertungsschnittstelle

In diesem Repository befindet sich - aktuell im Vorschlag- und Entwurfsstadium - die Spezifikation der gemeinsamen Auswertungsschnittstelle im TBA III Projekt.

Der aktuelle Stand kann in [`tba3-spec.yml`](./tba3-spec.yml) eingesehen werden. Diese lässt sich für einen besseren Zugang in der Swagger UI öffnen, z.B. direkt ohne Umwege über diesen Link: [Spezifikation Auswertungsschnittstelle (in der Swagger UI)](https://petstore.swagger.io/?url=https%3A%2F%2Fraw.githubusercontent.com%2Findibit-eu%2Ftba3%2Frefs%2Fheads%2Fmain%2Ftba3-spec.yml).

## Ziel und Zweck

Ziel dieses Projekts ist, einen gemeinsamen Standard für Endpunkte und Datenformate von Auswertungsdaten im VERA-Kosmos zu schaffen, der aber auch darüber hinaus eingesetzt werden kann.

Die Schnittstelle ist darauf ausgelegt, zwischen einem berechnenden Backend und einem anzeigenden Frontend alle relevanten Daten zu transferieren, die einen Bericht „mit Leben“ füllen können. Das heißt, Stamm- und Metadaten für die Durchführung und Verwaltung sind nicht Teil der Spezifikation. So sind etwa keine Endpunkte für verfügbare Klassen / Lerngruppen / ... oder für Testheftzusammensetzungen vorgesehen. Auch Authentifizierungsmechanismen werden nicht spezifiziert.

Die geschaffene Spezifikation soll es erleichtern, untereinander Berichtselemente mit geringem bis minimalem Aufwand auszutauschen. Eine vollständige Standardisierung aller Bestandteile der Test- und Auswertungssysteme ist aufgrund der Heterogenitäten, besonders frontendseitig und bei Bedien- und Stammdatenmanagementkonzepten, äußerst schwierig und nicht angestrebt.

## Konzepte und Begriffe

Um die Aufgabe der Schnittstelle zu verstehen, werden im Nachfolgenden ein paar Begriffe erläutert und dabei um ihre Rolle im Kontext dieser Schnittstelle ergänzt.

### Lerngruppe

Lerngruppe ist hier als Sammelbegriff für Gruppierungen von Schüler:innen verwendet, um damit verschiedenen Anforderungen gerecht zu werden.

Die Schnittstelle ist nicht auf eine bestimmte Form davon ausgerichtet und verwendet hierfür den Begriff `group` / `groups`. Was eine `group` ist, unterscheidet sich je nach System und wird in der Regel vom Backend festgelegt. Berichtselemente, die mit der Schnittstelle kompatibel sind, können dann beispielsweise bei System A die Kompetenzstufenverteilung einer Schulklasse mit unterschiedlichen Fächern anzeigen, während sie in System B die Verteilung in einem bestimmten fachspezifischen Kurs darstellen. Welcher Kontext angezeigt wird, steuert meistens der aufrufende Bericht.

### Bericht

Ein Bericht ist eine Ansicht auf einen Datenausschnitt mit definiertem Kontext, z.B. ein Klassenbericht oder ein Schulbericht. Die Zusammensetzung eines Berichts wird dabei von der aufrufenden Anwendung, z.B. einem Web-Frontend oder einem PDF-Generator definiert und kann neben dynamischen Berichtselementen, deren Datenzufuhr über diese Schnittstelle definiert werden soll, auch weitere statische Elemente wie Erklärtexte beinhalten.

Informationen über verfügbare Berichte (Individualbericht, Klassenbericht, Fachbericht, ...) verfügbare Kontexte (Auswahl der angezeigten Klasse / Schüler:in, ...) ist nicht Teil der Schnittstelle und muss von der aufrufenden selbst anderweitig (z.B. über Endpunkte für Authentifizierung oder Stammdatenmanagement) ermittelt werden.

### Berichtselement

Ein Berichtselement ist eine für sich alleine stehende Darstellung von Auswertungsdaten, etwa eine Kompetenzstufenverteilung mit Vergleichswerten oder mittlere Lösungshäufigkeiten je Aufgabe. Es bieten sich zwei Wege an, Berichtselemente unter Zuhilfename der hier spezifizierten Schnittstelle austauschbar zu gestalten:

1. Der aufrufende Bericht übermittelt dem Berichtselement über einen Parameter den relevanten Kontext (z.B. eine Lerngruppen-Id, eventuell konfigurierte Filter). Innerhalb des Berichtselement werden dann die benötigten Endpunkte aufgerufen, die Daten transformiert und anschließend angezeigt. Hierdurch wird der Integrationsaufwand in neue Berichte auf ein Minimum reduziert, da solche Berichtselemente sehr self-contained sind, kann aber zu redundanten API-Aufrufen und komplexerem Code innerhalb der Elemente führen. Auch eine Implementation über Web Components wird erleichtert, da hier Attribute für den Datentransfer genutzt werden können.
2. Der aufrufende Bericht lädt die Daten vorab und übermittelt den gesamten Datensatz an das Berichtselement. Dieses Vorgehen empfiehlt sich besonders dann, wenn viele Berichtselemente in einem Bericht existieren, die auf die selben Daten zugreifen, um redundante API-Zugriffe zu vermeiden. Hierbei sollte für einfache Portabilität jedoch darauf geachtet werden, die Inputs möglichst simpel zu halten und im Idealfall die Daten aus den Endpunkten 1:1 zu übermitteln, anstatt sie schon vorher zu transformieren. Nachteilig ist, dass hier beim Einsatz neuer Berichtselemente potenziell der aufrufende Bericht umfangreicher erweitert werden muss, um die zusätzlichen Daten zu laden.

### TBD

Weitere Begriffe, die in diesem Kontext erklärungsbedürftig scheinen, werden hier in Zukunft ebenfalls erläutert.

## Anpassung der Spezifikation

Im Ordner `/api` liegen die Quelldateien für die Spezifikation, zur besseren Wartbarkeit und leichteren Erweiterung sind diese in einzelne Dateien aufgeteilt. Diese folgen dabei auch im Einzelnen jeweils dem OpenAPI Format. Mit dem Befehl `npx @redocly/openapi-cli@latest bundle api/api.yml -o tba3-spec.yml` kann eine kombinierte Datei erzeugt werden, die alle Teile enthält und sich so leichter in Clients wie SwaggerUI laden lässt.