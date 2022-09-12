Deduplication is the process of removing duplicate locations in our data


# SPLIT PHARMACIES
The first step is separating our data. We decided to separate pharmacies, laboratories and covid-19 related facilities from the rest of the health facilities. We do this in  `0_split_pharmacies.ipynb`. 

- `inputs/Assigned_CSDs.csv` is all the data together. 
- `inputs/assigned_CSDs.csv` is the health facilities WITHOUT pharmacies/covid-19 related facilities.
- The pharmacies/covid-19/laboratories data only can be found in `/pharmacies_and_covid/inputs/pharmacies_only.csv`


# CREATE PAIRS
This step of the process creates compares all pairs of facilities (not actually all combinations, explained below) and keeps the pairs that have a value of Name_CS (cosine method of comparing strings) bigger than a certain threshold between 0 and 1 (the closer to 1, the more the two facility names are similar). As you can see, we create pairs in 4 separate instances (steps 1, 4, 7 and 9). 

First, in  `1_create_pairs_PC.py`, we only compare facilities that have the same postal_code, so the output would be pairs of facilities with the same postal code and with a Name_CS > 0. 
Then, in `4_create_pairs_CSD.py`, we use CSDs innstead of postal codes, since not every facility has a postal code or there could be a mistake in the postal code entered. So the output would be pairs of facilities with the same CSDs and with a Name_CS > 0.3.

In `7_create_pairs_CIHI.py`, we use provinces instead of postal codes or CSDs. This makes the processing a lot slower, but it's a necessry drawback (explained later). We only keep the pairs that include one or two facilities that come from the `CIHI_healthcare_facilities.csv` dataset. The reasoning for this will also be explained later

In `9_create_pairs_PROV.py`, we once again compare facilities based on provinces, but we don't limit the pairs to having CIHI data. This is a final, more general check in case we missed anything in previous steps.

Each of these files creates a file in `/output/` named `Pairs.csv`. These csv's are all the pairs with a Name_CS higher than the value chosen and with the same postal-code/CSD/province.


# CLASSIFY
Steps 2, 5 and 91 are cl. These use the `Pairs.csv` files from the respective previous steps and with machine learning, determine which pairs are probable duplicates. the output from these 3 scripts are `/output/probable_duplicates.csv`. The pairs in these files are not necessarily duplicates, we will decide if they are in the following step, but simply limit the options and processing time thanks to the machine learning. The machine learning uses the file `inputs/ODHF_CandidatePairs_Training_Update.csv` to 'learn'

Why is there no classify step for `pairs_CIHI.csv`? CIHI data was reverse geocoded, meaning we found the addresses with the geocoordinates provided. However, in the vast majority of cases, the geocoordinates were incorrect, thus making the address incorrect. With different addresses, even if both locations have the same name, the "AI" won't recognize the pair as a probable duplicate. So we skip the machine learning and only use pairs_CIHI.csv in the next step. This fact also explains why we had to compare facilities based on if they are from the same province. CSDs are based on the geocoordinate of the location, and in some cases the distance between the CIHI location and the real, duplicate location, is far enough that they are in different CSDs. So if we had created pairs based on CSD, some pairs that are duplicates wouldn't have been paired up. 


# SCRATCH DUPLICATES
Using `probable_duplicates.csv` (or `pairs_CIHI.csv`), we must decide which pairs are actually duplicates. The first step in the script: deciding which facility in each pair we should prioritise to keep. This is based on many factors: file, if it has number of beds, if it has address, etc. The idx to remove can be found in the 'to_remove' column in both `duplicates.csv` and `NOT_duplicates.csv` (although the idx won't be removed if it's not a duplicate!)

Following this, I created various 'checks' based on multiple factors such as distance, Name_CS, Address_CS and Street_Num. If one or more of the checks is True, the pair goes to the respective `duplicates.csv` file. If all checks are False, the pair goes to `NOT_duplicates.csv`. 

From the duplicates file, the script grabs the idx's from the 'to remove' column and removes them from the previous file containing all facilities. What is meant by previous file? `3_scratch_duplicates_PC.ipynb` is the first 'scratch duplicates', so it will remove duplicates from `inputs/assigned_CSDs.csv` and with the removed duplicates, it outputs the file `deduplicated_PC.csv`. The second scratch duplicates `6_scratch_duplicates_CSD.ipynb` removes duplicates from `deduplicated_PC.csv` and outputs `deduplicated_CSD.csv`. This pattern continues until `92_scratch_duplicates_PROV.ipynb` which outputs the final `deduplicated.csv` file.

`8_scratch_duplicates_CIHI.py` is a .py file for processing reasons. It is normal that it takes a longer time to run (I would guess 10 minutes? Never actually timed it)


# OTHER INFORMATION

- The JSONs in `inputs/` are simply to replace certain springs in the dataframe and make the names more streamlined, thus making deduplication more accurate.
- `rl_helper.py` acts as a library used in `classify.py` to make the addresses more streamlined, remove accents and claculate distances between locations based on lat/long