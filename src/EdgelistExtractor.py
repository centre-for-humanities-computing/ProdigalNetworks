#!/usr/bin/env python
# coding: utf-8

# import packages
import re
import pandas as pd
from bs4 import BeautifulSoup
from collections import defaultdict

# Function definitions

def extract_all_characters(soup):
    """
    Function to extract characters from XML file of a play.

    Extracts the value of two tag attributes

        One relates to Act/Scene divisions and the other is for
        the name of the speaking character. These should be fairly
        clear from the code.

    This function should be modified to deal with different XML schema.
    """
    idList = []
    for a in soup.findAll(['div', 'sp']):
        if 'type' in a.attrs.keys():
            idList.append(a.attrs['type'])
        elif 'who' in a.attrs.keys():
            idList.append(a.attrs['who'])
            df = pd.DataFrame(idList, columns=['names'])
            return df

def character_pairings_in(l):
    """
    Function to create list of tuples of character pairings from extracted data

    This also (quite crudely) removes any Act or Scene divisions, which have all
    been tagged using an asterisk.
    """
    # Create list from Pandas DF
    #l = dataframe[0].tolist()
    l = [x for x in l if str(x) != 'nan']
    # Create pairings from list
    l2 = [(l[i],l[i+1]) for i in range(len(l)-1)]
    # Remove all Act and Scene markers
    #x = [[t for t in a if not '#' in t] for a in l2]
    # Keep only pairs of characters
    y = [row for row in l2 if len(row) > 1]
    # Create list of tuples
    character_pairings = [tuple(l) for l in y]

    return character_pairings

def create_edgelist_from(pairs):
    """
    Function to create edgelists for "speaking-in-turn" pairs

    Returns results in a way that will be useful in Gephi
    """
    # Create edgelist using defaultDict
    edges = defaultdict(int)
    for people in pairs:
        for personA in people:
            for personB in people:
                if personA < personB:
                    edges[personA + ",undirected," + personB] += 1

    # Create a dataframe from the defaultDict
    df = pd.DataFrame.from_dict(edges, orient='index')
    df.reset_index(level=0, inplace=True)

    # Split cell on comma into muliple columns
    split = (df['index'].str.split(',', expand=True).rename(columns=lambda x: f"col{x+1}"))

    # Merge these split columns with the 'weights' from the first df
    merged = split.join(df[0])

    # Rename columns for use in Gephi
    merged.columns = ["Source", "Type", "Target", "Weight"]

    return merged

if __name__=="__main__":
# List of filenames
    targets =  ["KL", "ado", "2h4", "wt"]

    # Read in play and create BeautifulSoup object
    for target in targets:
        filename = f"/Users/au564346/Desktop/{target}.xml"
        with open(filename, 'r') as file:
            raw = file.read()
            soup = BeautifulSoup(raw, 'lxml')

        # Create list using extract function
        character_list = extract_all_characters(soup)

        # Cleaning

        #cleaned = pd.read_csv(f"{target}.csv", header=None)
        #merged = pd.merge(character_list, cleaned, left_on="names", right_on=0, how="left")
        #merged = merged[1].dropna()
        #merged = merged[~merged.str.contains('#')]

        # Create edgelist
        edgelist_df = create_edgelist_from(character_pairings_in(character_list))
        print(edgelist_df)
        # Save to csv
        edgelist_df.to_csv(f"{target}.csv", sep=",", index=False, header=True)
