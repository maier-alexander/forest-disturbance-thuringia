# Learning Log

## 27.09.2026

### Was ich gemacht habe

- Projektstruktur vorbereitet
    mkdir - erstellt ein directory
    code . - öffnet ein directory
- Git kennengelernt
    - git init
    - git status
    - git add ...
        - git add .
    - git commit -m ...
        - --amend --no-edit (letzter commit bleibt bestehen, aber wird von neuestem Stand überschrieben)
    - git config --global user.name / user.email
    - git push
    - .gitignore

### Was ich gelernt habe

**Git**
- Git ist ein Versionskontrollsystem
- GitHub ist eine Plattform zum Speichern und Teilen von Git-Repositories
- Bevor man mit Git Änderungen committen kann, muss man sie vorerst mit "git add" stagen
    - mit Leerzeichen zwischen Dateinamen mehrere in einem Befehl
    - mit "git add ." werden automatisch alle veränderten/neuen Dateien im wd gestaged
- immer mal wieder "git status"
- später mit GutHub zusätzlich "git push"
- .gitignore (File-Endung) wird bei diesem Projekt von Nutzen sein, um mehrere GB große FE-Dateien nicht auf mein GitHub zu pushen
    - wirkt schon bei git add; wird also garnicht erst gestaged
- Git speichert (staged) keine leeren Ordner

**Projekthandhabung**
- oft arbeitet man so, dass man in .ipynb ausprobiert und testet, und dann den funktionierenden Python Code in .py Dateien baut
    - src = source code

### Entscheidungen
- Mittels .gitignore werden die venv, große Rohdateien und der python cache nicht gestaged 
- Ordnerstruktur angelegt: Daten -> roh/processed, notebooks, src, outputs

**Untersuchungsgebiet**
Entscheidung:
- Süd-Thüringer Wald im Raum Steinach – Neuhaus am Rennweg – Sonneberg

Warum:
- Waldanteil hoch
- Das Gebiet ist stark vom Borkenkäfer betroffen und besteht Überwiegend aus Kiefern-Monokulturen
    - --> starke Veränderung erwartbar
- DLR-Vergleichsdaten verfügbar

- Extent wird etwa bei 20 x 20 km bzw 25km x 25km liegen 

**Vergleichszeitraum**
Entscheidung:
2018–2024

Warum:
- Beginn der starken Trocken-/Schadensperiode ab 2018
- ausreichend langer Zeitraum für deutliche Veränderungen
- DLR-Vergleich deckt ihn vollständig ab
- exakte Daten werden später, abhängig von Jahreszeit und Wolkenbedeckung, ausgewählt

**Sentinel-2 Produkt**
Entscheidung:
Sentinel-2 Level-2A

- Level-2A
- B04
- B08
- B11
- B12
- SCL

Warum:
- Level-2A enthält die bereits atmosphärisch korrigierte geschätzte Oberflächenreflexion
    - atmosphärische Einflüsse wie Streuung und Absorption bei Level-2A weitgehend korrigiert
    - bei Level-1C ist es noch die TOA-Reflexion
- -> macht die zwei Zeitpunkte vergleichbarer, im Falle atmosphärischer Unterschiede  
- Wolken und Wolkenschatten dennoch vorhanden

**zusätzliche Daten**
- DLR Foreest Canopy Cover Loss (FCCL)
- Waldmaske, vermutlich die auch vom DLR genutzt des Thünen-Instituts ((https://www.openagrar.de/receive/openagrar_mods_00084145))

### Offene Fragen
- exakte AOI-Grenzen
- exakte Sentinel-2 Aufnahmedaten


## 30.09.2026

### Was ich gemacht habe
- Forschungsfrage und Untersuchungsgebiet festgelegt
- Vergleichszeitraum 2018–2024 und Sentinel-2 Level-2A gewählt
- AOI erstellt und Lage der Sentinel-2-Tiles geprüft
- Vier Sentinel-2-Produkte ausgewählt und heruntergeladen
- Thünen-Waldmaske und DLR-FCCL-Vergleichsprodukt heruntergeladen
- Datenauswahl und wichtige Entscheidungen dokumentiert

### Was ich gelernt habe
- Bedienung des Copernicus Browsers und das finden passender FE-Daten
- Überprüfung der Tile-Anzahl 

### Entscheidungen
**AOI-Auswahl**
- AOI auf möglichst wenig verschiedenen Tiles, um Mosaikierungsaufwand gering zu halten
- teilt sich auf zwei Tiles auf -> zu Beginn des Workflows ist Mosaikierung notwendig

NW,10.970760,50.604949
NE,11.323775,50.598439
SW,10.961430,50.380249
SE,11.312778,50.373791

**Sentinel-2-Datenauswahl**

Entscheidung:
- Referenzzeitpunkt: 01.07.2018
- Vergleichszeitpunkt: 09.07.2024
- Jeweils zwei Tiles: T32UPA und T32UPB
- Produkt: Sentinel-2 Level-2A

Warum:
- ähnliche Vegetationsphase 
- 2018 nahezu wolkenfrei
- 2024 wolkenärmste geeignete Aufnahme im untersuchten Zeitraum
- verbleibende Wolken werden später maskiert
- vollständige Produktmetadaten werden separat in einer CSV dokumentiert

**DLR-Vergleichsdaten**

Entscheidung:
- DLR Forest Canopy Cover Loss (FCCL), Monthly
- Datei: FCCL_DE_P1M.tif
- Räumliche Auflösung: 10 m

Warum:
- zeitliche Erfassung des Waldkronenverlusts auf Monatsebene
- Vergleich der eigenen Change Detection mit einem bestehenden DLR-Produkt möglich
- DLR nutzt ebenfalls die Thünen-Waldmaske von 2018

Limitationen:
- DLR-Produkt ist keine unabhängige Ground Truth
- unterschiedliche Methoden und Zeiträume können zu Abweichungen führen
- monatliche Verlustangaben erlauben keine taggenaue Zuordnung
