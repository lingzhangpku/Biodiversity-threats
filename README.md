This repo includes all codes used for biodiversity threat analysis.

Code and Data Processing for the Paper: Mapping escalating biodiversity threats across global supply chains

# Overview
This study quantified biodiversity threats embodied in international trade by integrating species–threat information from the IUCN Red List with the Eora multi-regional input–output (MRIO) database. The entire workflow consisted of several steps from data acquisition to spatial visualization.

# Data
All data used in this study are open accessed. 
- Species data are collected from the [IUCN Red List of Threated Species](https://www.iucnredlist.org/), and [BirdLife International](http://www.birdlife.org/). 
- The input-output tables and greenhouse gas emission data are collected from the [Eora Database](https://worldmrio.com/) . 
- The human footprint data is from [Mu et al. 2022](https://doi.org/10.1038/s41597-022-01284-8). 
- The land use data is from the [MCD12Q1 Version 6.1 product](https://developers.google.com/earth-engine/datasets/catalog/MODIS_061_MCD12Q1). 

## 1. Retrieval of species–threat information
Species data were obtained via automated queries to the IUCN Red List API. please refer to the script [data_scraper_iucn_red_list.py](data_scraper_iucn_red_list.py). The retrieved fields included scientific name, Red List category, threat codes and descriptions, habitat types, population trend, distribution, and assessment year.

Multithreaded Python scripts were used to efficiently download and parse JSON responses.

All records were saved as structured CSV files for subsequent processing.

## 2.Mapping threats to economic sectors
Each IUCN threat code was matched to the corresponding sector in the Eora MRIO framework.

Examples include: 
- Agricultural expansion → Agriculture
- Residential and urban development → Construction

This step produced a species–sector correspondence table linking biological threats with economic activities. please refer to 1_1_sector_mapping.m in MatLab code.

## 3. Estimation of spatial distribution weights
Based on species-specific data across countries (including human footprint and land area), calculate the proportion of human activity intensity and habitat area that each country represents within a species distribution range. Please refer to 1_2_weighted_threats_calculation.m in MatLab code.
This ensures that species whose distributions span multiple countries are represented according to the relative human disturbance and habitat extent in each region.

## 4. Calcultion of bioiversity threats embodied in production and trade.
We used an environmentally extended multi-regional input–output (MRIO) model to trace the biodiversity threats embodied in international trade.
The MRIO approach captures complete supply chain–wide transactions between sectors and regions, thereby linking production activities to final consumption across borders. 
The biodiversity threat–based satellite account (Bio) serves as an environmental extension of the MRIO model. It quantifies the equivalent number of species threatened per unit of sectoral output, enabling the linkage between species-level threat data and the economic production network. Through integration with the Leontief inverse matrix and final demand matrix, it allows the tracing of biodiversity threats across global supply chains. All calculations were implemented in MATLAB (see 1_3_MRIO_calculation.m).





