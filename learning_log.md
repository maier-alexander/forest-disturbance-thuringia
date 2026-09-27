# Learning Log

## 2026-09-27

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

### Offene Fragen

