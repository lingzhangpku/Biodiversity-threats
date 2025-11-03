"""
Created: Friday 27 June 2025
Description: Scripts to scrpe details of red list species
Scope: biodiversity threat project of Ling Zhang
Author: Quanliang Ye
Institution: IIASA
Email: yequanliang@iiasa.ac.at
"""

import requests
from concurrent.futures import ThreadPoolExecutor

import datetime
import logging
from pathlib import Path
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
import time
import ast

# Read the variable
data_home = Path("./data")
current_version = "v.6.2025"

timestamp = datetime.datetime.now()
file_timestamp = timestamp.ctime()

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,  # Set the logging level
    format="%(asctime)s - %(levelname)s - %(message)s",  # Specify the log message format
    datefmt="%Y-%m-%d %H:%M:%S",  # Specify the date format
    handlers=[
        logging.StreamHandler(),  # Log to console
        logging.FileHandler("app.log"),  # Log to a file
    ],
)

logging.info("Configure project")
current_project = "bio_threat"

logging.info("Configure paths")
path_data_raw = data_home / "raw_data" / current_project / current_version
if not path_data_raw.exists():
    path_data_raw.mkdir(parents=True, exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
    "X-Csrf-Token": "v5a7zPbDJmXbiFNbzTeWQF2GqPWmUNzXekyJfgxJTCVmJDCjc/99i5Cgbn2RCY2EfCCSHtTW3KMKcAPhl4pyxw==",
    "Cookie": "_ga=GA1.1.761810478.1705810660; _application_devise_session=aFE1TTZzWU9MbktwU2lSTnpYbXYvUTd1dHdHV2FpNE5xOWZoUEc5WVdweXhWMUFtYkhUM0cxQzV1SUt6MUxidlJVYTRrSHpZdWFYRU1oemhiejdCSFMrNUx0RStBQzRUcEhNV3l3QkV2WFA1TFhZQ1VwcHMzb2c1L3U5YjFyZEcxV1c5U3A0OEFsT1ZMRzVXbVZUV1gvZG0yTE1XTDJIQWRIZExHYW1pV3kzWGpBR1ZlY25NZG9NN3dGOWdmb1U5cUh5SFd5aW0xWWwxQ2kwc3FQWjFSdz09LS1td01jdUlqdFZzdlFSWUJYZjBNVWdRPT0%3D--e0aa4102ebfc64c038682a9751586c1b33fdc49c; _ga_66YGJWTDLZ=GS1.1.1705810660.1.1.1705811240.0.0.0; _ga_T3K17G40FC=GS1.1.1705810660.1.1.1705811241.0.0.0; _ga_6HJED7KZLB=GS1.1.1705810660.1.1.1705811241.0.0.0",
    "Referer": f"https://www.iucnredlist.org",
}


def get_species_id(species_name: str):
    """Get the id information used in the API of the species.

    Parameters
    ----------
    species_name: str
       The name of species

    Returns
    -------
    species_id: str
    species_sis_id: str
    """
    logging.info("Set the search url")
    search_url = (
        "https://www.iucnredlist.org/dosearch/assessments/_search?size=1&_source=false"
    )
    payload = {
        "stored_fields": ["sisTaxonId"],
        "query": {
            "bool": {
                "must": [
                    {
                        "multi_match": {
                            "query": species_name,
                            "type": "phrase_prefix",
                            "fields": ["scientificName^10", "commonName"],
                            "lenient": True,
                        }
                    }
                ],
                "filter": {
                    "bool": {
                        "filter": [
                            {"terms": {"scopes.code": ["1"]}},
                            {"terms": {"taxonLevel": ["Species"]}},
                        ]
                    }
                },
            }
        },
    }

    logging.info("Call the species page")
    time.sleep(1)
    species_page_req = requests.post(
        search_url, headers=HEADERS, json=payload, timeout=10
    )

    if species_page_req.status_code == 200:
        page_info = species_page_req.json()["hits"]["hits"]
    else:
        logging.raiseExceptions(
            f"No page for {species_name}, due to {species_page_req.text}"
        )
        return None, None

    if page_info:
        logging.info("Omit species with different scientific name(s)")
        if len(page_info) > 1:
            for page_info_ in page_info:
                species_name_sci = page_info_["fields"]["scientificName"][0]
                if species_name_sci == species_name:
                    page_info = [page_info_]
                    del page_info_
                else:
                    continue

        logging.info("Get basic information of species")
        species_id = page_info[0]["_id"]
        species_sis_id = page_info[0]["fields"]["sisTaxonId"][0]

        return species_id, species_sis_id
    else:
        logging.info(f"No information for {species_name}")
        return None, None


def get_species_endpoint(species_id: int):
    """Get all the endpoint information of the species,
       including the previously assessment.

    Parameters
    ----------
    species_id: int
        The id of species

    Returns
    -------
    species_endpoints: dict
    """
    logging.info("Set API url for the species")
    url = f"https://www.iucnredlist.org/api/v4/species/{species_id}"

    logging.info("Call the API")
    # time.sleep(0.5)
    species_info = requests.get(url, headers=HEADERS, timeout=10)

    if species_info.status_code == 200:
        species_info = species_info.json()
    else:
        logging.raiseExceptions(
            f"No page for {species_name}, due to {species_info.text}"
        )
        return {}

    species_endpoint_info = {}
    logging.info("Get the latest assessment information")
    assess_date = species_info["citation"]["footer"][:4]
    species_endpoint_info[assess_date] = species_id
    del assess_date

    logging.info("Get the previous assessment information")
    if species_info["previousAssessments"]:
        for previous_info in species_info["previousAssessments"]:
            previous_species_id = previous_info["id"]
            previous_assess_date = previous_info["yearPublished"]
            species_endpoint_info[previous_assess_date] = previous_species_id
            del previous_species_id, previous_assess_date

    logging.info("Get all endpoints")
    return species_endpoint_info


def get_species_assessment(species_id: int):
    """Get detailed assessment information of the species

    Parameters
    ----------
    species_id: int
        The id of species

    Returns
    -------
    species_threats_details: dict
    """
    logging.info("Set API url for the species")
    url = f"https://www.iucnredlist.org/api/v4/species/{species_id}"

    logging.info("Call the API")
    time.sleep(1)
    species_info = requests.get(url, headers=HEADERS, timeout=10)

    if species_info.status_code == 200:
        species_info = species_info.json()
    else:
        logging.raiseExceptions(
            f"No page for {species_name}, due to {species_info.text}"
        )
        return {}

    logging.info("Get the latest assessment information")
    species_type = (
        species_info["taxon"]["taxonomy"]["className"]
        if species_info["taxon"]["taxonomy"]["kingdomName"] != "Plantae"
        else "Plantae"
    )
    assess_date = species_info["date"][-4:]
    threat_category = species_info["redListCategory"]["title"]["en"]
    threat_category_code = species_info["redListCategory"]["code"]
    population_trend = species_info["populationTrend"]["title"]["en"]
    if species_info["systems"]:
        habitat_1 = species_info["systems"][0]["description"]["en"]
    else:
        habitat_1 = []
    if species_info["habitats"]:
        habitat_2 = [
            habitat_info["description"]["en"]
            for habitat_info in species_info["habitats"]
        ]
    else:
        habitat_2 = []

    if species_info["threats"]:
        threat_detail = get_threat_details(species_info["threats"])
    else:
        threat_detail = []

    logging.info(f"Got all threats information for species with id {species_id}")
    species_threats_details = {
        f"{assess_date}_species_id": species_id,
        f"{assess_date}_red_list_category": threat_category,
        f"{assess_date}_red_list_category_code": threat_category_code,
        f"{assess_date}_population_trend": population_trend,
        f"{assess_date}_habitat1": habitat_1,
        f"{assess_date}_habitat2": habitat_2,
        f"{assess_date}_threats": threat_detail,
    }

    return species_type, species_threats_details


def get_threat_details(threat_info: list):
    """Get the detailed threats of the species.

    Parameters
    ----------
    threat_info: list
        A list includes all threats information with three levels

    Returns
    -------
    species_threats_all
    """
    species_threats_all = []
    logging.info("Get all threats")
    for threat_level1 in threat_info:
        threat1_name = threat_level1["description"]["en"]
        if threat_level1["children"]:
            for threat_level2 in threat_level1["children"]:
                threat2_name = threat1_name + " | " + threat_level2["description"]["en"]
                if threat_level2["children"]:
                    for threat_level3 in threat_level2["children"]:
                        threat3_name = (
                            threat2_name + " | " + threat_level3["description"]["en"]
                        )
                        species_threats_all.append(threat3_name)
                        del threat3_name
                else:
                    species_threats_all.append(threat2_name)
                    del threat2_name
        else:
            species_threats_all.append(threat1_name)
            del threat1_name

    logging.info("Get all threats")
    return species_threats_all


def process_species(species_item: tuple):
    """
    To get the id of each species

    Parameters:
        species_item: tuple
            Include the species name
    """
    logging.info("Configure the name of species")
    species_name = species_item[1]

    logging.info("Get the species id and sis id for the species")
    species_id, species_sis_id = get_species_id(species_name=species_name)
    if species_id:
        logging.info("Get endpoint of all previous assessment for the species")
        species_endpoint_all = get_species_endpoint(species_id)

        logging.info(
            "Get all the endpoints of species. Starting get species assessment details"
        )
        species_assessment_details = {
            "scientific_name": species_name,
            "species_sis_id": species_sis_id,
        }
        for species_assessment_year in species_endpoint_all.keys():
            species_id_ = int(species_endpoint_all[species_assessment_year])

            logging.info(
                f"Get all the assessment information of species with id {species_id_}"
            )
            species_type, species_assessment = get_species_assessment(species_id_)
            species_assessment_details["type"] = species_type
            species_assessment_details = species_assessment_details | species_assessment

        species_assessment_details_ = pd.DataFrame([species_assessment_details])
        species_assessment_details_.to_csv(
            path_data_raw
            / "red_list_assessment_detials_new"
            / f"species_{species_name.replace(' ','_')}_assessment_detials.csv",
            index=False,
        )


def omit_duplicate_elements(data: dict, keyword: str):
    keyword_keys = [key_ for key_ in data.keys() if keyword in key_]
    data_keyword = list(set(data[key_] for key_ in keyword_keys if data[key_] != "[]"))
    if len(data_keyword) == 1:
        unique_element = data_keyword[0]
    elif len(data_keyword) > 1:
        unique_element = set()
        for item in data_keyword:
            try:
                parsed = ast.literal_eval(item)
                if isinstance(parsed, list):
                    unique_element.update(parsed)
            except:
                pass

        unique_element = list(unique_element)
    else:
        unique_element = []
    return unique_element, keyword_keys


def process_period_assessment_results(data: dict, keyword: str, split_year: int = None):
    """
    To combine assessment details for two splited periods

    Parameters:
        - data:dict
            The assessment details

        - keyword:
            The assessment indicator.
            keyword should be: "red_list_category_weight", 'threat'

        - year:
            The year used to split the whole sutdy period, default year=2010

    Return:
        unique_element_pre
        unique_element_post
    """
    split_year = split_year if split_year else 2010

    pre_year_keys = [
        key_
        for key_ in data.keys()
        if (keyword in key_) and (int(key_[-4:]) < split_year)
    ]
    post_year_keys = [
        key_
        for key_ in data.keys()
        if (keyword in key_) and (int(key_[-4:]) >= split_year)
    ]
    if post_year_keys:
        data_post_years = list(
            set(
                data[key_]
                for key_ in post_year_keys
                if (data[key_] != "[]") and (data[key_] != "")
            )
        )

        # data_post_years = data_post_years * 2
        if data_post_years:
            if "threat" in keyword:
                unique_element = set()
                for item in data_post_years:
                    try:
                        parsed = ast.literal_eval(item)
                        if isinstance(parsed, list):
                            unique_element.update(parsed)
                    except:
                        pass

                unique_element_post = sorted(
                    set(
                        [
                            " | ".join(element_.split(" | ")[:2])
                            for element_ in unique_element
                        ]
                    )
                )
                del unique_element
            elif "weight" in keyword:
                try:
                    unique_element_post = max(data_post_years)
                except TypeError:
                    unique_element_post = max(
                        data_ for data_ in data_post_years if data_ is not None
                    )
        else:
            unique_element_post = None

        del data_post_years
    else:
        unique_element_post = None

    if pre_year_keys:
        data_pre_years = list(
            set(
                data[key_]
                for key_ in pre_year_keys
                if (data[key_] != "[]") and (data[key_] != "")
            )
        )

        if data_pre_years:
            if "threat" in keyword:
                unique_element = set()
                for item in data_pre_years:
                    try:
                        parsed = ast.literal_eval(item)
                        if isinstance(parsed, list):
                            unique_element.update(parsed)
                    except:
                        pass

                unique_element_pre = sorted(
                    set(
                        [
                            " | ".join(element_.split(" | ")[:2])
                            for element_ in unique_element
                        ]
                    )
                )
                del unique_element
            elif "weight" in keyword:
                try:
                    unique_element_pre = max(data_pre_years)
                except TypeError:
                    unique_element_pre = max(
                        data_ for data_ in data_pre_years if data_ is not None
                    )
        else:
            unique_element_pre = None
        del data_pre_years
    else:
        unique_element_pre = None

    return unique_element_pre, unique_element_post


if __name__ == "__main__":
    logging.info("Get the full list of species")
    with open(path_data_raw / "list.txt", encoding="utf-8") as f:
        name_list = [(i, line.strip()) for i, line in enumerate(f) if line.strip()]

    path_data_output = path_data_raw / "red_list_assessment_details"
    if not path_data_output.exists():
        path_data_output.mkdir(parents=True, exist_ok=True)

    logging.info("Check the total number of data facts")
    species_assessment_list = [file for file in path_data_output.glob("*.csv")]
    if len(species_assessment_list) < len(name_list) * 0.8:
        logging.info("We need to re-download the data")
        logging.info("This may take 12 hours")
        logging.info("Start downloading the assessment details")
        with ThreadPoolExecutor(max_workers=2) as executor:
            executor.map(process_species, name_list)
    else:
        logging.info("No data need to be downloaded")

    logging.info("Combine species assessment results")
    threat_level_mapping = {
        "CR": 4,
        "CT": 1,
        "E": 3,
        "EN": 3,
        "EW": 5,
        "EX": 5,
        "Ex": 5,
        "Ex/E": 5,
        "Ex?": 5,
        "LC": 0,
        "LR/cd": 0,
        "LR/lc": 0,
        "LR/nt": 0,
        "NT": 1,
        "O": 0,
        "R": 0,
        "T": 1,
        "V": 2,
        "VU": 2,
        "nt": 0,
    }
    species_assessment_details_all = []
    species_assessment_details_columns = []  # for the final columns
    for species_assessment_file in species_assessment_list:
        species_results = pd.read_csv(species_assessment_file).to_dict("records")[0]
        species_basic_columns = ["type", "scientific_name", "species_sis_id"]

        logging.info("Change the header names")
        species_results_keys = list(species_results.keys())[3:]
        for key_ in species_results_keys:
            key_name = key_[5:] + "_" + key_[:4]
            species_results[key_name] = species_results.pop(key_)
            if "red_list_category_code_" in key_name:
                try:
                    species_results[key_name.replace("_code_", "_weight_")] = (
                        threat_level_mapping[species_results[key_name]]
                    )
                except KeyError:
                    species_results[key_name.replace("_code_", "_weight_")] = None
            del key_, key_name
        species_results_keys = list(species_results.keys())[3:]

        logging.info("Unique habitats")
        species_habitat1, species_habitat1_keys = omit_duplicate_elements(
            species_results, "habitat1"
        )
        species_results_keys = [
            key_ for key_ in species_results_keys if key_ not in species_habitat1_keys
        ]
        species_habitat2, species_habitat2_keys = omit_duplicate_elements(
            species_results, "habitat2"
        )
        species_results_keys = [
            key_ for key_ in species_results_keys if key_ not in species_habitat2_keys
        ]
        logging.info("Update habitat results")
        species_results["habitat1"] = species_habitat1
        species_results["habitat2"] = species_habitat2
        species_basic_columns = species_basic_columns + ["habitat1", "habitat2"]

        logging.info("Include period results for red list category, and threats")
        split_year = 2010  # we split the available years into pre-2010 and post-2010
        for keyword_ in ["red_list_category_weight", "threat"]:
            assessment_pre_period, assessment_post_period = (
                process_period_assessment_results(
                    species_results, keyword=keyword_, split_year=split_year
                )
            )
            species_results[f"{keyword_}_pre_{split_year}"] = assessment_pre_period
            species_results[f"{keyword_}_post_{split_year}"] = assessment_post_period
            species_basic_columns = species_basic_columns + [
                f"{keyword_}_pre_{split_year}",
                f"{keyword_}_post_{split_year}",
            ]
            del assessment_pre_period, assessment_post_period

        logging.info("Append the assessment results")
        species_assessment_details_all.append(species_results)

        logging.info("Update final columns")
        species_assessment_details_columns = list(
            np.unique(species_assessment_details_columns + species_results_keys)
        )

        del (
            species_assessment_file,
            species_results,
            species_results_keys,
            species_habitat1,
            species_habitat1_keys,
            species_habitat2,
            species_habitat2_keys,
        )

    species_assessment_details_all = pd.DataFrame(species_assessment_details_all)[
        species_basic_columns + species_assessment_details_columns
    ]
    del species_basic_columns

    logging.info("Done, save data")
    species_assessment_details_all.to_csv(
        path_data_raw / "iucn_species_assessment_details_time_series.csv", index=False
    )
