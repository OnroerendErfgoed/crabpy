"""
Script can be used to convert an Excel file to a JSON file.
Used to update the deelgemeenten or gemeenten data.
The script requires pandas and some other libraries.

pip install pandas
pip install openpyxl
pip install xlrd
"""
import json
import os
import re

import pandas as pd


def process_string(s):
    # Find all separators (hyphens or whitespace) and store them
    separators = re.findall(r"[-\s]", s)

    # Remove whitespace around hyphens
    s = re.sub(r"\s*-\s*", "-", s)

    # Split string into words separated by hyphens or whitespace
    words = re.split(r"[-\s]", s)

    # Capitalize each word
    capitalized_words = [word.capitalize() for word in words]

    # Rebuild the string with original separators
    processed_string = ""
    for i, word in enumerate(capitalized_words):
        processed_string += word
        if i < len(separators):
            processed_string += separators[i]

    return processed_string


def deelgemeente_mapping(row):
    naam = process_string(row["NIS6naam"])
    return {
        "id": row["NIS6_code_INS6"],
        "naam": naam,
        "gemeente_niscode": str(row["CD_MUN"]),
    }


def create_deelgemeenten_json(filename="deelgemeenten.json"):
    # Read the Excel file
    excel_file = (
        "https://github.com/OnroerendErfgoed/crabpy"
        "/files/11285927/NIS6nwithnamefrom01012019.xlsx"
    )
    df = pd.read_excel(excel_file)
    mapped_data = df.apply(deelgemeente_mapping, axis=1)
    json_data = mapped_data.to_json(orient="records")
    output_json_file = "deelgemeenten.json"
    with open(output_json_file, "w") as f:
        f.write(json_data)


gemeente_example_data = [
    {
        "provincie": "10000",
        "namen": [
            {"taal": "nl", "naam": "Antwerpen"},
            {"taal": "fr", "naam": "Anvers"},
        ],
        "niscode": "11002",
    }
]


def create_gemeenten_json(filename="gemeenten.json"):
    # Read the Excel file
    excel_file = (
        "https://statbel.fgov.be/sites/default/files"
        "/Over_Statbel_FR/Nomenclaturen/REFNIS_2019.csv"
    )
    df = pd.read_csv(excel_file, delimiter=";", encoding="utf-8")
    with open(os.path.join("provincies.json")) as f:
        provincies = json.load(f)
        province_niscodes = [int(provincie["niscode"]) for provincie in provincies]
        provincie = None
    gemeenten = []
    for _, row in df.where(pd.notnull(df), None).iterrows():
        if row["Code INS"] in province_niscodes:
            provincie = row["Code INS"]
            continue
        if row["Langue"] and row["Taal"]:
            gemeenten.append(
                {
                    "niscode": str(row["Code INS"]),
                    "provincie": str(provincie) if provincie else None,
                    "namen": [
                        {"taal": "fr", "naam": row["Entités administratives"]},
                        {"taal": "nl", "naam": row["Administratieve eenheden"]},
                    ],
                }
            )

    # Convert the list of dictionaries to a JSON string
    json_data = json.dumps(gemeenten, indent=4, ensure_ascii=False)

    # Save the JSON data to a file
    with open(filename, "w", encoding="utf-8") as f:
        f.write(json_data)


create_deelgemeenten_json()
create_gemeenten_json()
