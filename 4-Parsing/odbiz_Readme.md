# What is the goal of parsing in the project?
We have different formats for addresses. If you take a look at the `input/ODBiz_Merged.csv` file, you will notice that some addresses are all together under the full_address column, while some addresses are split into street_no, street_name, postal_code, etc. 

The objective is to split the addresses that are NOT split (which is the majority), and make a individual columns for street number and name, unit number, city and postal code

# parse_csv.py
This python script's purpose is to to separate the full addresses thanks to the pypostal library. New columns (LP_...) are created with the parsed addresses, WITHOUT including the addresses that were already split. The output of this file is parsed.csv. 

There exists an issue with the LP_street_no column: sometimes, full addresses will have unit number and street number separated with a dash (12-235, for example). The parsing code recognizes this as a full street number, instead of 2 different values, which is why we split these wherever necessary. This is why there are two additional columns in the parsed file: LP2_unit and LP2_street_no. These two columns are created to combine any unit and street number that we already had, plus the ones we split afterwards. Addionally, some entries have multiple values seperated with multiple dashes. This is dealth with in `odbiz_custom_parse.py`.

To run this script, go into terminal and enter: `python parse_csv.py input/ODBiz_Merged.csv full_address output/parsed_biz.csv`. If there is no module named postal, enter `conda install postal` into the terminal

# odbiz_custom_parse.py
In the `LP_street_no` column, some entries have multiple number and letter values that are seperated by multiple dashes (4-flr-777, for example). This script handles most of these odd cases.

# combine_parsed_cols.py
This script's purpose is to merge columns together. As mentionned previously, some adresses were already split from data collection, so there are already some values in the columns street_no, street_name, etc. This script simply fills NAN values in these columns with values from LP2_street_no, LP_street_name, etc. 

# Pipeline for ODBiz Parsing
1.	Do a preliminary parsing of the data using the `parse_csv.py` script
2.	Use `odbiz_custom_parse.py` to apply some more specific parsing scripts to the odbiz dataset
3.	Manually parse the rare pattern addresses, write changes on a separate csv, then use a script to update the main csv. Create a new subdirectory for this task!
4.	Remove rural addresses and un-googlable addresses
5.	Fill in the blank values of street_no, street_name, etc. (without the ‘LP_’ prefix) using `combine_parsed_cols.py`
6.	Remove entries with insufficient address info
