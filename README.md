# WatchList - Sorozatkövető webalkalmazás
## Készítette: Vizi Fanni - FOF695

Az alkalazás Flask alapú, a TVMaze API-t használ a sorozatok adatainak lekérdezésére, a többi adat tárolásához SQLite adatbázist használ.

### Funkciók

- Bejelentkezés nélkül a látogató megtekintheti a sorozatok listáját és ezek oldalát
- A sorozat oldalán megtekinthető a sorozat képe, leírása, értékelése, valamint a részek évadonként.
- Az oldalon lehet felhasználókat regisztrálni.
- A regisztrált felhasználó be tud jelentkezni
- Bejelentkezés után a sorozat oldalán meg tudjuk jelölni a már látott részeket.
- A profil oldalon megtekinthetőek a felhasználó adatai, statisztikai adatok és a megtekintett részek.
- A megtekintett részekre kattintva elérjük a sorozat oldalát.

### Technológiák

- Python 3.10
- Flask
- SQLite
- További csomagok a requirements.txt-ben

### Projekt felépítése

- python_gyak
  - data: adatbázis
  - static: css
  - templates: html fájlok
- tests: Unittestek és a kódelemző eszközök eredménye

### Kódelemző eszközök:

- Pylint
- Flake8

### Bemutató videó:

- python_project.mkv
