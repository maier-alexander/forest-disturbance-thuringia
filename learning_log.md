# Learning Log

## 27.09.2026

### Was ich gemacht habe

- Projektstruktur vorbereitet
    mkdir - erstellt ein directory
    code . - öffnet ein directory in vsc
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
- Mittels .gitignore werden die venv, große Rohdateien und den python cache nicht gestaged 
- Ordnerstruktur angelegt: Daten -> roh/processed, notebooks, src, outputs

**Untersuchungsgebiet**
Entscheidung:
Süd-Thüringer Wald im Raum Steinach – Neuhaus am Rennweg – Sonneberg

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
- Exakte Daten werden später, abhängig von Jahreszeit und Wolkenbedeckung, ausgewählt

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
- ...
- ...

**zusätzliche Daten**
- DLR Foreest Canopy Cover Loss (FCCL)
- Waldmaske, vermutlich die auch vom DLR genutzt des Thünen-Instituts ((https://www.openagrar.de/receive/openagrar_mods_00084145))
### Offene Fragen

