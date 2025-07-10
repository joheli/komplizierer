import marimo

__generated_with = "0.14.10"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""# <a href="https://www.rki.de/DE/Themen/Infektionskrankheiten/Meldewesen/DEMIS/DEMIS_inhalt.html" target = "_blank">DEMIS</a> <a href="https://loinc.org/" target="_blank">LOINC</a> UND <a href="https://www.bfarm.de/EN/Code-systems/Terminologies/SNOMED-CT/_node.html" target="_blank">SNOMED</a> *KOMPLIZIERER*""")
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
    code_url = 'https://simplifier.net/guide/rki.demis.laboratory/Home/resources/terminologies/codesystems/guide-notificationCategory.guide.md?version=current'
    response = requests.get(code_url)
    response.raise_for_status()
    jetzt = datetime.now(tz=ZoneInfo("Europe/Berlin")).strftime("%d.%m.%Y (%H:%Mh)")
    #response.status_code
    return ZoneInfo, code_url, datetime, jetzt, requests, response


@app.cell
def _(mo):
    mo.md(
        """
    ## Anleitung

    Bitte wählen Sie die Zeile mit dem passenden Meldecode ("Code") in der [nachfolgenden Tabelle](#meldecodes). Nach Auswahl einer Zeile werden darunter die entsprechenden

      * [Labor-LOINCs](#labor)
      * [SNOMED Materialcodes](#material)
      * [SNOMED Answercodes](#answer)

    automatisch abgefragt und dargestellt.
    """
    )
    return


@app.cell
def _(mo):
    mo.md(
        r"""
    /// details | Tipps

      * Durch Anklicken auf die Spaltenüberschrift rechts können Einträge gefiltert werden!
      * Links unten gibt es auch ein Suchfeld (Lupe)!

    ///
    """
    )
    return


@app.cell
def _():
    import pandas as pd
    from io import StringIO
    return StringIO, pd


@app.cell
def _(StringIO, pd, response):
    dfs2 = pd.read_html(StringIO(response.text), header=0, flavor="html5lib")
    code_data_frame = dfs2[1][['Display', 'Code']]
    #code_data_frame
    return (code_data_frame,)


@app.cell
def _(code_url, jetzt, mo):
    mo.md(
        f"""
    ## <a name="meldecodes"></a>Meldecodes (Code)

    Abfragezeitpunkt: {jetzt}, Quelle: <a href="{code_url}" target="_blank">html</a>
    """
    )
    return


@app.cell
def _(code_data_frame, mo):
    marimo_table = mo.ui.table(code_data_frame, selection="single", initial_selection=[0])
    marimo_table
    return (marimo_table,)


@app.cell
def _(marimo_table):
    selected_row = marimo_table.value
    meldecode = ""
    if not selected_row.empty:
        meldecode = selected_row.iloc[0]["Code"]
    # meldecode
    return (meldecode,)


@app.cell
def _(requests):
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

    def sets(meldecode:str, art: Literal["labor", "material", "answer"]) -> dict:
        url_stamm = {"labor": "https://fhir.simplifier.net/rki.demis.laboratory/ValueSet/laboratoryTest", 
                     "material": "https://fhir.simplifier.net/rki.demis.laboratory/ValueSet/material", 
                     "answer": "https://fhir.simplifier.net/rki.demis.laboratory/ValueSet/answerSet"}
        url_final = url_stamm[art] + meldecode.upper()
        jetzt = datetime.now(tz=ZoneInfo("Europe/Berlin")).strftime("%d.%m.%Y (%H:%Mh)")
        tabelle = [{"Information": "Abfrage folgt."}]
        fehler = [{"Fehler": f"Die Abfrage von {url_final} war fehlerhaft."}]
        abfrage = query_url(url = url_final)
        erfolgreich = 0
        if abfrage:
            try:
                tabelle = abfrage.json()["compose"]["include"][0]["concept"]
                erfolgreich = 1
            except Exception:
                tabelle = fehler
        else:
            tabelle = fehler
        return {"url": url_final, "zeitpunkt": jetzt, "tabelle": tabelle, "erfolgreich": erfolgreich}
    return (sets,)


@app.cell
def _(meldecode, mo, pd, sets):
    labor_set = sets(meldecode = meldecode, art = "labor")
    labor_zeitpunkt = labor_set["zeitpunkt"]
    labor_url = labor_set["url"]
    labor_df = pd.DataFrame(labor_set["tabelle"])
    labor_mo_table = mo.ui.table(labor_df)
    labor_demis_seite = f"https://simplifier.net/guide/rki.demis.laboratory/Home/resources/terminologies/valuesets/laboratoryTest/guide-laboratoryTest{meldecode.upper()}.guide.md?version=current"
    mo.md(f"""
    ## <a name="labor"></a>LOINC Optionen für Meldecode {meldecode.upper()}

    Abfragezeitpunkt: {labor_zeitpunkt}, Quellen: <a href="{labor_url}" target="_blank">json</a>, <a href="{labor_demis_seite}" target="_blank">html</a>
    """)
    return (labor_df,)


@app.cell
def _(labor_df):
    labor_df
    return


@app.cell
def _(meldecode, mo, pd, sets):
    answer_set = sets(meldecode = meldecode, art = "answer")
    answer_zeitpunkt = answer_set["zeitpunkt"]
    answer_url = answer_set["url"]
    answer_df = pd.DataFrame(answer_set["tabelle"])
    answer_demis_seite = f"https://simplifier.net/rki.demis.laboratory/answerset{meldecode}"
    if (answer_set["erfolgreich"] == 1):
        answer_df = answer_df[["display", "code"]]
    answer_mo_table = mo.ui.table(answer_df)
    mo.md(f"""
    ## <a name="answer"></a>SNOMED Answerset für Meldecode {meldecode.upper()}

    Abfragezeitpunkt: {answer_zeitpunkt}, Quellen: <a href="{answer_url}" target="_blank">json</a>, <a href="{answer_demis_seite}" target="_blank">html</a>
    """)
    return (answer_df,)


@app.cell
def _(answer_df):
    answer_df
    return


@app.cell
def _(meldecode, mo, pd, sets):
    material_set = sets(meldecode = meldecode, art = "material")
    material_zeitpunkt = material_set["zeitpunkt"]
    material_url = material_set["url"]
    material_demis_seite = f"https://simplifier.net/rki.demis.laboratory/material{meldecode}"
    material_df = pd.DataFrame(material_set["tabelle"])
    if (material_set["erfolgreich"] == 1):
        material_df = material_df[["display", "code"]]
    material_mo_table = mo.ui.table(material_df)
    mo.md(f"""
    ## <a name="material"></a>SNOMED Materialien für Meldecode {meldecode.upper()}

    Abfragezeitpunkt: {material_zeitpunkt}, Quellen: <a href="{material_url}" target="_blank">json</a>, <a href="{material_demis_seite}" target="_blank">html</a>
    """)
    return (material_df,)


@app.cell
def _(material_df):
    material_df
    return


@app.cell
def _(mo):
    mo.md(
        r"""
    ## Autor

    Johannes Elias
    """
    )
    return


if __name__ == "__main__":
    app.run()
