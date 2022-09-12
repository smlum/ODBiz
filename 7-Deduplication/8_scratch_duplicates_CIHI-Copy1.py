import pandas as pd

df = pd.read_csv('outputs/pairs_CIHI.csv')
final = pd.read_csv("inputs/deduplicated_CSD.csv", low_memory=False)


# CIHI_healthcare_facilities.csv

df = df[(df['FileName_1']  == "CIHI_healthcare_facilities.csv") | (df['FileName_2']  == "CIHI_healthcare_facilities.csv" )]
df.to_csv('outputs/pairs_CIHI.csv', index=False)


def hierarchy(id1, id2): 

#    try:

    check_file1 = final.loc[final.idx == id1].filename.item()
    check_file2 = final.loc[final.idx == id2].filename.item()
    check_name1 = final.loc[final.idx == id1].facility_name.item()
    check_name2 = final.loc[final.idx == id2].facility_name.item()


    if check_file1 == 'CIHI_healthcare_facilities.csv' and check_file2 != 'CIHI_healthcare_facilities.csv':
        return id1

    elif check_file2 == 'CIHI_healthcare_facilities.csv' and check_file1 != 'CIHI_healthcare_facilities.csv':
        return id2

    else:
        return id1

#    except ValueError:
 #       return "Item not found."

df["to_remove"] = df.apply(lambda x: hierarchy( id1 = x.idx1, id2 = x.idx2), axis = 1)





def check_1(name, distance, postalcode):

    if distance != None:
        if name > 0.5 and distance < 1 and postalcode == 1:
            return True
        else:
            return False

    else:
        return False

df["Check_1"] = df.apply(lambda x: check_1(name = x.Name_CS, distance = x.Distance, postalcode = x.PC_Match), axis=1)




def check_2(name, distance, postalcode):

    if distance != None:
        if name > 0.85 and distance < 5 and postalcode == 1:
            return True
        else:
            return False

    else:
        return False

df["Check_2"] = df.apply(lambda x: check_2(name = x.Name_CS, distance = x.Distance, postalcode = x.PC_Match), axis=1)




def check_3(name, distance):

    if distance != None:
        if name > 0.95 and distance < 5:
            return True
        else:
            return False

    else:
        return False

df["Check_3"] = df.apply(lambda x: check_3(name = x.Name_CS, distance = x.Distance), axis=1)




def check_4(name):

    if name > 0.99:
        return True
    else:
        return False

df["Check_4"] = df.apply(lambda x: check_4(name = x.Name_CS), axis=1)





rows = df.index[(df['Check_1'] == True) | (df['Check_2'] == True) | (df['Check_3'] == True) | (df['Check_4'] == True)].tolist()
false_rows = df.index[(df['Check_1'] == False) & (df['Check_2'] == False) & (df['Check_3'] == False) | (df['Check_4'] == True)].tolist()

df_true = df.loc[rows]
df_false = df.loc[false_rows]

df_true.to_csv('outputs/duplicates_CIHI.csv', index=False)
df_false.to_csv('outputs/NOT_duplicates_CIHI.csv', index=False)

hashes = df_true['to_remove'].tolist()

final = final[~final['idx'].isin(hashes)]
final.to_csv('deduplicated_CIHI.csv', index=False)
final.to_csv('inputs/deduplicated_CIHI.csv', index=False)
