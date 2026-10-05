import marimo

__generated_with = "0.24.0"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # <a href="https://www.rki.de/DE/Themen/Infektionskrankheiten/Meldewesen/DEMIS/DEMIS_inhalt.html" target = "_blank">DEMIS</a> <a href="https://loinc.org/" target="_blank">LOINC</a> UND <a href="https://www.bfarm.de/EN/Code-systems/Terminologies/SNOMED-CT/_node.html" target="_blank">SNOMED</a> *KOMPLIZIERER*
    """)
    return


@app.cell(hide_code=True)
def _():
    import marimo as mo

    return (mo,)


@app.cell
async def _():
    import micropip
    #import pyodide
    await micropip.install("html5lib")
    #await pyodide.loadPackage('tzdata')
    await micropip.install("tzdata")
    return


@app.cell
def _():
    import requests
    from datetime import datetime
    from zoneinfo import ZoneInfo
    from bs4 import BeautifulSoup

    # Hartkodiert
    # Die Seite `code_url` enthält eine HTML-Tabelle zu den Meldecodes, die ich brauche.
    code_url = 'https://simplifier.net/guide/rki.demis.laboratory/Home/resources/terminologies/codesystems/guide-notificationCategory.guide.md?version=current'
    response = requests.get(code_url)

    # Wenn die Seite nicht erreichbar ist, wird ein Fehler ausgelöst.
    response.raise_for_status()

    # Speichere den Zeitpunkt der Abfrage
    jetzt = datetime.now(tz=ZoneInfo("Europe/Berlin")).strftime("%d.%m.%Y (%H:%Mh)")

    # DEBUG: gib Status Code aus: (auskommentieren für Produktion)
    #response.status_code
    return ZoneInfo, code_url, datetime, jetzt, requests, response


@app.cell
def _(mo):
    mo.md("""
    ## Anleitung

    Bitte wählen Sie die Zeile mit dem passenden Meldecode ("Code") in der [nachfolgenden Tabelle](#meldecodes). Nach Auswahl einer Zeile werden darunter die entsprechenden

    -  [Labor-LOINCs](#labor)
    -  [SNOMED Materialcodes](#material)
    -  [SNOMED Answercodes](#answer)

    automatisch abgefragt und dargestellt.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    /// details | Tipps

      * Durch Anklicken auf die Spaltenüberschrift rechts können Einträge gefiltert werden!
      * Links unten gibt es auch ein Suchfeld (Lupe)!

    ///
    """)
    return


@app.cell
def _():
    import pandas as pd
    from io import StringIO

    return StringIO, pd


@app.cell
def _(StringIO, pd, response):
    # Extrahiere aus der o.g. html Antwort (response) alle Tabellen
    dfs2 = pd.read_html(StringIO(response.text), header=0, flavor="html5lib")

    # Speichere die dritte Tabelle (index 2) dar, aber nur Spalten `Display` und `Code`
    code_data_frame = dfs2[2][['Display', 'Code']]

    # DEBUG: gib Tabelle aus (Auskommentieren für Produktivversion)
    #code_data_frame
    return (code_data_frame,)


@app.cell
def _(code_url, jetzt, mo):
    mo.md(f"""
    ## <a name="meldecodes"></a>Meldecodes (Code)

    Abfragezeitpunkt: {jetzt}, Quelle: <a href="{code_url}" target="_blank">html</a>
    """)
    return


@app.cell
def _(code_data_frame, mo):
    # Wandle die extrahierte Tabelle in eine Marimo Tabelle um - dies ermöglicht die Auswahl von Zeilen
    marimo_table = mo.ui.table(code_data_frame, selection="single", initial_selection=[0])
    marimo_table
    return (marimo_table,)


@app.cell
def _(marimo_table):
    # Extrahiere die Zeile (in ein pandas data frame)
    selected_row = marimo_table.value
    meldecode = ""

    # Wenn nicht leer, extrahiere Feld "Code" 
    if not selected_row.empty:
        # iloc[0] hier bedeutet nur: erste Zeile des data frame `selected_row`
        meldecode = selected_row.iloc[0]["Code"]

    # DEBUG: zeige `meldecode` - in Produktivversion auskommentiert
    #meldecode
    return (meldecode,)


@app.cell
def _(requests):
    # Methode, um eine URL abzufragen
    def query_url(url:str, timeout: int = 5) -> requests.models.Response:
        try:
            rspns = requests.get(url = url, timeout = timeout)
        except Exception:
            return
        if (rspns.status_code != 200):
            return
        else:
            return rspns

    return (query_url,)


@app.cell
def _(ZoneInfo, datetime, query_url):
    from typing import Literal

    # Methode, um eine Tabelle zu labor (LOINC Optionen), material (Material Optionen), oder answer (SNOMED Optionen) zu liefern
    def sets(meldecode:str, art: Literal["labor", "material", "answer"]) -> dict:
        # es gibt drei verschiedene Quellen
        url_stamm = {"labor": "https://fhir.simplifier.net/rki.demis.laboratory/ValueSet/laboratoryTest", 
                     "material": "https://fhir.simplifier.net/rki.demis.laboratory/ValueSet/material", 
                     "answer": "https://fhir.simplifier.net/rki.demis.laboratory/ValueSet/answerSet"}
    
        # ergänze die URL durch den Meldecode (in Großbuchstaben)
        url_final = url_stamm[art] + meldecode.upper()

        #speichere den Zeitpunkt
        jetzt = datetime.now(tz=ZoneInfo("Europe/Berlin")).strftime("%d.%m.%Y (%H:%Mh)")

        # Standardwert für Ausgabe `tabelle`
        tabelle = [{"Information": "Abfrage folgt."}]

        # Eine einfache, aber nichtssagende,  Fehlermeldung
        fehler = [{"Fehler": f"Die Abfrage von {url_final} war fehlerhaft."}]

        # Führe die Abfrage aus
        abfrage = query_url(url = url_final)
        erfolgreich = 0

        # Wenn die Abfrage erfolgreich war, wandle die Antwort in json um und extrahiere das relevante Feld
        if abfrage:
            try:
                tabelle = abfrage.json()["compose"]["include"][0]["concept"]
                erfolgreich = 1
            except Exception:
                tabelle = fehler
        else:
            tabelle = fehler

        # Liefere ein dict als Antwort mit den relevanten Feldern
        return {"url": url_final, "zeitpunkt": jetzt, "tabelle": tabelle, "erfolgreich": erfolgreich}

    return (sets,)


@app.cell
def _(meldecode, mo, pd, sets):
    # Frage Labordaten (LOINC Optionen) ab
    labor_set = sets(meldecode = meldecode, art = "labor")

    # Extrahiere relevante Informationen
    labor_zeitpunkt = labor_set["zeitpunkt"]
    labor_url = labor_set["url"]
    labor_df = pd.DataFrame(labor_set["tabelle"])

    # Nimm die Tabelle und wandle sie in eine Marimo Tabelle um
    labor_mo_table = mo.ui.table(labor_df)

    # DEMIS Seite für den ausgesuchten Meldecode (wird als Link angeboten)
    labor_demis_seite = f"https://simplifier.net/guide/rki.demis.laboratory/Home/resources/terminologies/valuesets/laboratoryTest/guide-laboratoryTest{meldecode.upper()}.guide.md?version=current"

    # Markdown für 
    mo.md(f"""
    ## <a name="labor"></a>LOINC Optionen für Meldecode {meldecode.upper()}

    Abfragezeitpunkt: {labor_zeitpunkt}

    ### Quellen: 
    """)
    return labor_demis_seite, labor_df, labor_url


@app.cell
def _(labor_demis_seite, labor_url, mo, pd):
    # Quellen
    labor_quellen_urls = pd.DataFrame({"Format": ["json", "html"], "url": [labor_url, labor_demis_seite]})
    mo.ui.table(labor_quellen_urls, show_search=False, selection = None, column_widths={"Format": 80, "url": 600})
    return


@app.cell
def _(mo):
    mo.md("""
    ### Optionen (alphabetisch):
    """)
    return


@app.cell
def _(labor_df):
    # Stelle die Tabelle für LOINC Optionen dar, nur Spalten `display` und `code`
    labor_df.sort_values(by = ['display'], ignore_index=True)[['display', 'code']]
    return


@app.cell
def _(meldecode, mo, pd, sets):
    # Answer Sets (SNOMED Optionen): erstelle Abfrage
    answer_set = sets(meldecode = meldecode, art = "answer")

    # Extrahiere relevante Informationen
    answer_zeitpunkt = answer_set["zeitpunkt"]
    answer_url = answer_set["url"]
    answer_df = pd.DataFrame(answer_set["tabelle"])

    # Erstelle DEMIS URL (wird als Link angeboten)
    answer_demis_seite = f"https://simplifier.net/rki.demis.laboratory/answerset{meldecode}"

    if (answer_set["erfolgreich"] == 1):
        answer_df = answer_df[["display", "code"]]

    # Wandle in Marimo Tabelle um
    answer_mo_table = mo.ui.table(answer_df)

    # Generiere Markdown zur Darstellung
    mo.md(f"""
    ## <a name="answer"></a>SNOMED Answerset für Meldecode {meldecode.upper()}

    Abfragezeitpunkt: {answer_zeitpunkt}

    ### Quellen:
    """)
    return answer_demis_seite, answer_df, answer_url


@app.cell
def _(answer_demis_seite, answer_url, mo, pd):
    # Quellen
    answer_quellen_urls = pd.DataFrame({"Format": ["json", "html"], "url": [answer_url, answer_demis_seite]})
    mo.ui.table(answer_quellen_urls, show_search=False, selection = None,column_widths={"Format": 80, "url": 600})
    return


@app.cell
def _(mo):
    mo.md("""
    ### Optionen (alphabetisch):
    """)
    return


@app.cell
def _(answer_df):
    # Stelle SNOMED Optionen dar
    answer_df.sort_values(by = ["display"], ignore_index=True)
    return


@app.cell
def _(meldecode, mo, pd, sets):
    # Frage Material Optionen ab
    material_set = sets(meldecode = meldecode, art = "material")

    # Extrahiere relevante Informationen
    material_zeitpunkt = material_set["zeitpunkt"]
    material_url = material_set["url"]
    material_df = pd.DataFrame(material_set["tabelle"])

    # Genierere URL für DEMIS Seite - wird unten angeboten
    material_demis_seite = f"https://simplifier.net/rki.demis.laboratory/material{meldecode}"

    # Wenn erfolgreich, extrahiere Tabelle mit Spalten Display und Code
    if (material_set["erfolgreich"] == 1):
        material_df = material_df[["display", "code"]]

    # Wandle Tabelle in Marimo Tabelle um
    material_mo_table = mo.ui.table(material_df)

    # Generiere Markdown zur Darstellung
    mo.md(f"""
    ## <a name="material"></a>SNOMED Materialien für Meldecode {meldecode.upper()}

    Abfragezeitpunkt: {material_zeitpunkt}

    ### Quellen: 
    """)
    return material_demis_seite, material_df, material_url


@app.cell
def _(material_demis_seite, material_url, mo, pd):
    # Quellen
    material_quellen_urls = pd.DataFrame({"Format": ["json", "html"], "url": [material_url, material_demis_seite]})
    mo.ui.table(material_quellen_urls, show_search=False, selection = None, column_widths={"Format": 80, "url": 600})
    return


@app.cell
def _(mo):
    mo.md("""
    ### Optionen (alphabetisch):
    """)
    return


@app.cell
def _(material_df):
    # Stelle Material Optionen als Tabelle dar
    material_df.sort_values(by = ["display"], ignore_index=True)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Autor

    Johannes Elias
    """)
    return


if __name__ == "__main__":
    app.run()
