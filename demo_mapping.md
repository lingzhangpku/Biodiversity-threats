We use gross industrial output and species-country level adjustment coefficient to attribute each threat causes to associated countries and sectors. We assume there is one species $p$ threatened by $h$ threats, and its geographic range covers $m$ countries.
We then use the concordance table between threats and economic sectors in MRIO tables to allocate each threat across regions and sectors. 

We assume threat type $q$ can be caused by production of $n$ economic sectors in the MRIO tables. Outputs of the sector $i$ in country $r$ are denoted as $x_i^r$. The habitat size of species $p$ in country $r$ is $LA^r$. Human footprint with distribution range in country $r$ is $HF^r$. The threat type $q$ (measured in one unit) is allocated to sector $i$ in country $r$ via:

$$
B_i^{q,r}=
    \frac
        {x_i^r \times \eta^r}
        {\sum_{s\in m} {\sum_{j \in n} {x_j^s \times \eta^s}}}
$$
(Eq. 1)


$$
\eta^r=
    \frac
        {\alpha^r \times \beta^r}
        {\sum_{s\in m} {\alpha^s \times \beta^s}}
$$
(Eq. 2)

$$
\alpha^r=
    \frac
        {LA^r}
        {\sum_{s\in m} {LA^s}}
$$
(Eq. 3)

$$
\beta^r=
    \frac
        {HF^r}
        {\sum_{s\in m} {HF^s}}
$$
(Eq. 4)

where $B_i^{q,r}$ is weighted threats allocated to production of sector $i$ in country $r$. $\eta^r$ is allocation fraction of country $r$ calculated based on $LA^r$ and $HF^r$. $\alpha^r$ is the share of habitat size in country $r$ in total habitat sizes of all $m$ countries. $\beta^r$ is the share of human footprints in country $r$ in total human footprints of all $m$ countries. We still use Eq. 1 to allocate climate-related threats across sectors and countries but rely on sector-level greenhouse gas emissions instead of total outputs. Lastly, we normalize h threats with same weights and construct only one row vector for species $p$ in the satellite account for MRIO modelling.

Here is an example to show satellite calculation progress. We assume:

- Species A is distributed across three countries, X, Y, and Z.
- The economic sectors include S1, S2, S3, and S4.
- Among the identified threats, threat type Ta is associated with sectors S1, S2, and S3; Tb is linked to S2 and S3; Tc corresponds to S4; and Td represents climate-related threats, which are assumed to be associated with all sectors.

The country-level adjustment coefficient is derived from the species’ habitat preference and human footprint intensity, normalized across countries for the species. The sectoral-level adjustment coefficients, reflecting the economic or climate influence of threats, are based on two inputs: sectoral gross outputs ($x$, in USD) or sectoral greenhouse gas emissions ($E$ in Mt CO₂). Both are row-normalized for each threat type, and the resulting coefficients are used to allocate threat intensity across sectors.


{: .note }
>  **(a) Link the species A’s threats with industrial sectors.** * value ‘1’ means that the production of column sector causes the row threat.
>  
|Species A|Distributed Countries and Related Sectors||||||||||||
|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|
| |X||||Y||||Z||||
|**Threats**|S1|S2|S3|S4|S1|S2|S3|S4|S1|S2|S3|S4|
|Ta|1|1|1||1|1|1||1|1|1||
|Tb||1|1|||1|1|||1|1||
|Tc||||1||||1||||1|
|Td (climate-related)|1|1|1|1|1|1|1|1|1|1|1|1|
||||||||||||||
|**Sectoral Gross Output ($x$, in USD)**|20|30|40|50|200|300|500|100|70|30|60|80|
|**Sectoral GHG Emissions ($E$, in Mt $CO_2$)**|50|40|30|20|100|500|300|200|80|60|30|70|
|**Species habitat ($LA$, in $km^2$)**|100||||500||||400||||
|**Human interaction ($HF$, in human footprint)**|5||||15||||30||||


{: .note }
>  **(b) Attribute each threat causes extent by gross industrial output / GHG emissions and the construction of country-level adjustment coefficients.**
>  
|Species A|Distributed Countries and Related Sectors|||||||||||||
|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|
| |X||||Y||||Z||||**Sum**|
|**Threats**|S1|S2|S3|S4|S1|S2|S3|S4|S1|S2|S3|S4|
|Ta|20|30|40|0|200|300|500|0|70|30|60|0|**1250**|
|Tb|0|30|40|0|0|300|500|0|0|30|60|0|**960**|
|Tc|0|0|0|50|0|0|0|100|0|0|0|80|**230**|
|Td (climate-related)|50|40|30|20|100|500|300|200|80|60|30|70|**1480**|
|||||||||||||||
|**Sector-level shares by threats (economic or climate influence of threats)**|||||||||||||
|Ta|0.02|0.02|0.03|0|0.16|0.24|0.40|0|0.06|0.02|0.05|0|**1**|
|Tb|0|0.03|0.04|0|0|0.31|0.52|0|0|0.03|0.06|0|**1**|
|Tc|0|0|0|0.22|0|0|0|0.43|0|0|0|0.35|**1**|
|Td (climate-related)|0.03|0.03|0.02|0.01|0.07|0.34|0.20|0.14|0.05|0.04|0.02|0.05|**1**|
|**Share of habitat size ($\alpha$)**|0.1||||0.5||||0.4||||**1**|
|**Share of human footprint ($\beta$)**|0.1||||0.3||||0.6||||**1**|
|**Allocation fraction ($\eta$)**|0.03||||0.38||||0.6||||**1**|

{: .note }
>  **(c) Calculation weighted threats and satellite accounts of species A.**
>  
|Species A|Distributed Countries and Related Sectors|||||||||||||
|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|
| |X||||Y||||Z||||**Sum**|
|**Allocated threats ($B^q$)**|S1|S2|S3|S4|S1|S2|S3|S4|S1|S2|S3|S4||
|Ta|0.001|0.002|0.002|0|0.158|0.238|0.396|0|0.089|0.038|0.076|0|**1**|
|Tb|0|0.002|0.003|0|0|0.316|0.527|0|0|0.051|0.101|0|**1**|
|Tc|0|0|0|0.014|0|0|0|0.432|0|0|0|0.553|**1**|
|Td|0.002|0.002|0.001|0.001|0.067|0.335|0.201|0.134|0.086|0.064|0.032|0.075|**1**|
|**Normalized threats (B)**|0.001|0.001|0.002|0.004|0.056|0.222|0.281|0.142|0.044|0.038|0.052|0.157|**1**|



