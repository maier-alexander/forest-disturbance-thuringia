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
- git diff --cached --stat
    - git diff: zeigt Unterschiede zwischen Dateiversionen
    - --cached: berücksichtigt nur Änderungen in der Staging Area
    - --stat: zeigt nur eine kompakte Statistik statt der vollständigen Änderungen
- git remote add [Name_für_Github_Acc] [link]; muss i.d.R. nur einmal eingestellt werden
- git branch -M  [gewünschter_Branchname]
    - git branch verwaltet lokale Branches
    - M erzwingt die Umbenennung (Move/rename mit Force), auch wenn bereits ein Branch mit dem Zielnamen existiert
- git push -u origin main
    - "Pushe den lokalen Stand des Hauptbranches (main) auf mein GitHub (origin)"
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

## 08.–12.10.2026

### Was ich gemacht habe
- Mit NumPy 2D-Raster indexiert, ausgeschnitten und elementweise verrechnet (u. a. NDVI)
- Gültigkeits- und Vegetationsmasken erstellt; NoData-/NaN-Werte bei Berechnungen berücksichtigt
- Überlappende Rasterkacheln per NumPy zu Mosaiken kombiniert und AOI-Ausschnitte erzeugt
- Sentinel-2-Band B04 (10 m) mit Rasterio geöffnet, Metadaten und ein 100×100-Pixel-Fenster ausgelesen
- Rasterausschnitt mit Matplotlib dargestellt – erst mit Pixelindizes, danach georeferenziert mit UTM-Koordinaten

### Was ich gelernt habe
**NumPy**
- `ndarray` statt Python-Liste: gemeinsame Datentypen, mehrere Achsen und elementweise Rechenoperationen; `shape` = Form, `ndim` = Dimensionszahl, `size` = Elementanzahl, `dtype` = Datentyp
- Indexierung/Slicing: `a[zeile, spalte]`, `a[start:stop, :]` (`stop` exklusiv)
- Boolean Indexing: Bedingungen erzeugen Masken; `&` kombiniert, `~` invertiert; `a[maske]` liest und `a[maske] = wert` verändert gezielt Elemente
- Fehlende Werte und Statistik: `np.isnan()`, `np.nanmean()`, `np.sum()` zum Zählen von `True`; `np.divide(..., out=..., where=...)` für Berechnungen nur an gültigen Positionen
- Slicing erzeugt meist einen *View* (gemeinsame Daten); `.copy()` eine unabhängige Kopie
- Rasterarrays kombinieren: `np.vstack()` untereinander, `np.hstack()` nebeneinander; bei echten Satellitendaten ist zusätzlich räumliche Ausrichtung nötig

**Rasterio und Visualisierung**
- `rasterio.open(pfad)` öffnet eine Rasterdatei (`.jp2`/`.tif`); `with` schließt sie automatisch
- Metadaten: `width`/`height` (Pixel), `crs` (EPSG:32632), `res` (10 m), `count` (Bänder), `dtypes`, `bounds`
- `src.read(1, window=Window(spalte, zeile, breite, höhe))` liest einen Ausschnitt direkt als NumPy-Array; spart Zeit und RAM
- `src.xy(zeile, spalte)` liefert Pixelmittelpunkt als (Easting, Northing); Rasterzeilen steigen nach Süden
- `src.transform` verbindet Pixelposition und Kartenkoordinaten; `src.window_transform(fenster)` berücksichtigt den verschobenen Ausschnitt
- `plt.imshow()` zeigt ein Array mit Pixelachsen; `rasterio.plot.show(ausschnitt, transform=transform)` zeigt UTM-Koordinaten. `cmap` ändert nur die Darstellung, nicht die Pixelwerte

## 13.–17.10.2026

### Was ich gemacht habe
- Sentinel-2-Vorverarbeitung fertiggestellt: zwei Tiles je Aufnahmedatum mosaikiert, Bänder auf gemeinsames 10-m-Raster ausgerichtet und SCL-Klassen 4/5/6 als gültig übernommen
- Referenzgitter direkt aus der AOI erzeugt, sodass `preprocess.py` ohne bereits vorhandene Ergebnisdatei erneut durchlaufen kann; Rastergitter und Maskierung überprüft
- BOA-Offset von −1000 und Quantifizierungswert von 10000 berücksichtigt; NDVI, NDMI und NBR für 2018 und 2024 berechnet
- Pixelweise Differenzen (2024 − 2018) erstellt und nur gemeinsam gültige Pixel verglichen; unplausible Indexwerte außerhalb [−1, 1] ausgeschlossen
- Veränderungen auf die Thünen-Waldflächen von 2018 beschränkt und mit dem DLR-FCCL-Produkt (zeitlich gefiltert) verglichen
- ΔNDMI und ΔNBR anhand räumlich aufgeteilter Trainings- und Testdaten ausgewertet; binäre ΔNBR-Klassifikation und Vergleichskarten erstellt
- Python-Skripte thematisch zusammengeführt und Verarbeitungsschritte übersichtlicher organisiert

### Was ich gelernt habe
**Rasterverarbeitung und NumPy**
- `rasterio.merge.merge()` für Mosaike; `reproject()` mit `Resampling.nearest` für SCL-Klassen und `bilinear` für SWIR-Bänder
- Gemeinsames Referenzgitter aus AOI-Grenzen, 10-m-Auflösung und `from_origin()` erstellen; keine Abhängigkeit von vorhandenen Ausgabedateien
- `np.isin()` für SCL- und Klassenmasken, `np.isfinite()` für gültige Indexwerte, `np.ma.masked_invalid()` für Karten mit NoData
- `src.profile.copy()` und `.update()` für GeoTIFF-Metadaten; `NaN` als NoData bei Indexrastern, `255` bei binären Klassifikationen
- `Path.parent.mkdir(parents=True, exist_ok=True)` erstellt fehlende Ausgabeordner

**Fernerkundung und Auswertung**
- NDVI = (B08 − B04)/(B08 + B04), NDMI = (B08 − B11)/(B08 + B11), NBR = (B08 − B12)/(B08 + B12)
- Bei Sentinel-2 L2A die BOA-Offsets vor Indexberechnungen berücksichtigen; `DN = 0` nicht als gültigen Reflexionswert behandeln
- Ein negativer ΔIndex bedeutet Indexrückgang, aber nicht zwangsläufig Waldverlust; DLR ist ein Vergleichsprodukt, keine unabhängige Ground Truth
- Perzentile und Schwellenwerte zur Untersuchung der Verteilungen; Precision, Recall und F1-Score für Klassifikationsvergleiche
- Räumlich getrennte Trainings- und Testblöcke verringern die Verzerrung gegenüber einer zufälligen Pixelaufteilung, sind aber keine vollständig unabhängige externe Validierung
- Matplotlib: `plt.subplots()`, `zip()`, `plotting_extent()`, `ListedColormap`, `Patch`, Legenden und `fig.savefig()` für georeferenzierte Vergleichskarten

### Ergebnisse und Entscheidungen
- Auf ursprünglichen Waldflächen mittlere Veränderungen: ΔNDVI −0,106; ΔNDMI −0,179; ΔNBR −0,171
- DLR-Kronendachverlust im aufbereiteten Vergleichsdatensatz: 20.337,10 ha; einfache ΔNBR-Klassifikation: 22.196,07 ha (Flächen nicht ohne identische Gültigkeitsmaske direkt vergleichen)
- Beste getestete ΔNBR-Schwelle: −0,125; Test-Precision 0,672, Recall 0,732, F1 0,700; ΔNDMI mit F1 0,680 etwas schwächer
- Entscheidung: Für dieses Portfolio-Projekt zunächst beim interpretierbaren ΔNBR-Schwellenwertmodell bleiben, statt zusätzlich Machine Learning einzusetzen

### Nächste Schritte
- Finale Karten grafisch überarbeiten und räumliche Abweichungen zwischen eigener Klassifikation und DLR diskutieren
- Methodische Grenzen, Ergebnisse und Reproduzierbarkeit im README dokumentieren; Git-Commit erstellen
