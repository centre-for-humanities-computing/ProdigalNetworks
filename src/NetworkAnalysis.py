#!/usr/bin/env python
# coding: utf-8

import re
import pandas as pd
from bs4 import BeautifulSoup
import networkx as nx
import matplotlib.pyplot as plt

# Define functions
def list_xmlfiles(directory):
    """
    Return a list of filenames ending in '.txt' in DIRECTORY.
    Not strictly necessary but will be useful if we try to scale.
    """
    xmlfiles = []
    for filename in listdir(directory):
        if filename.endswith(".xml"):
            xmlfiles.append(filename)
    return xmlfiles

def list_textfiles(directory):
    """
    Return a list of filenames ending in '.txt' in DIRECTORY.
    Not strictly necessary but will be useful if we try to scale.
    """
    textfiles = []
    for filename in listdir(directory):
        if filename.endswith(".txt"):
            textfiles.append(filename)
    return textfiles

def count_totals(character_list):
    """
    Function to count the total number of speech acts and lines per character in each play
    """
    counts = []
    for character in character_list:
        lines = [[line.text for line in test(['l','p'])] for test in soup.findAll(who=character)]
        words = [[word.replace('\n', ' ').replace('\r', '') for word in words] for words in lines]
        x = []
        for item in words:
            for s in item:
                x.append(len(re.findall(r'\w+', s)))

        speech_acts = len(lines)
        total_words = sum(x)
        totals = (character, speech_acts, total_words)
        counts.append(totals)
    df = pd.DataFrame(counts, columns=["character", "lines", "words"])
    return df

def folger_count(character_list):
    """
    Hacky function to deal with Folger Shakespeare editions
    """
    counts = []
    for character in character_list:
        lines = [test('lb') for test in soup.findAll(who=character)]
        words = [test('w') for test in soup.findAll(who=character)]
        speech_acts = sum([sum(v != 0 for v in i) for i in lines])
        total_words = sum([sum(v != 0 for v in i) for i in words])
        totals = (character, speech_acts, total_words)
        counts.append(totals)

    df = pd.DataFrame(counts, columns=["character", "lines", "words"])
    return df


def total_rankings(df):
    """
    Create count rankings based on word and line lengths.
    """
    df["line_rank"] = df["lines"].sort_values(ascending=False).rank(method='dense', ascending=False).astype(int)
    df["word_rank"] = df["words"].sort_values(ascending=False).rank(method='dense', ascending=False).astype(int)
    df["count_rank"] = ((df["line_rank"] + df["word_rank"])/2).astype(int)
    return df

def metric_rankings(df):
    """
    Create metrics rankings based on node metrics from .Gephi file I don't like this function very much. It's too pandas-y. But it works.
    """
    df["WD_rank"] = df["weighted_degree"].sort_values(ascending=False).rank(method='dense', ascending=False).astype(int)
    df["EC_rank"] = df["eigenvector"].sort_values(ascending=False).rank(method='dense', ascending=False).astype(int)
    df["degree_rank"] = df["degree"].sort_values(ascending=False).rank(method='dense', ascending=False).astype(int)
    df["BC_rank"] = df["betweenness"].sort_values(ascending=False).rank(method='dense', ascending=False).astype(int)
    df["metrics_rank"] = ((df["WD_rank"] + df["EC_rank"] + df["degree_rank"] + df["BC_rank"])/4).astype(int)
    return df

# list of filenames
indir = os.path.join("data", "text")

def main(): 
    # Read in plays and create BeautifulSoup object
    for target in indir:
        print(f"Reading {target}...")
        filename = os.path.join(indir, "{target}.xml")
        with open(filename, 'r') as file:
            raw = file.read()
            soup = BeautifulSoup(raw, 'lxml')

        # create list of characters based on lines
        idList = []
        for a in soup.findAll('sp'):
            if 'who' in a.attrs.keys():
                idList.append(a.attrs['who'])

        # Only unique characters
        unique = set(idList)

        # Calculate lines and words for all characters
        if target in ("1H4","2H4"):
            out = folger_count(unique)
            totals = out
        else:
            totals = count_totals(unique)

        # Cleanup tables and rank measures

        cleaned = pd.read_csv(f"../data/character_lists/{target}.csv", header=None)
        merged = pd.merge(totals, cleaned, left_on="character", right_on=0)
        merged = merged[[1, "lines", "words"]]
        merged = merged.dropna()
        merged = merged[~merged[1].str.contains('#')]
        merged = merged.groupby(1)[['lines', 'words']].sum().reset_index()
        merged.columns.values[0] = 'character'

        # Calculate + save count ranks
        count_ranks = total_rankings(merged)

        # Calculate metric measures using networkx
        edgelist_df = pd.read_csv(f"../data/edgelists/{target}.csv")

        G = nx.from_pandas_edgelist(edgelist_df, "Source", "Target", ["Weight"])
        nx.write_gexf(G, f"../data/graphs/{target}.gexf")
        plt.figure(figsize=(14,14))
        #nx.draw(G, with_labels=True, font_size=20)
        #plt.draw()

        # betweenness centrality
        bcentrality = nx.betweenness_centrality(G, normalized=False)
        between = sorted(((float(c), v) for v,c in bcentrality.items()), reverse=True)

        # eigenvector centrality
        ecentrality = nx.eigenvector_centrality_numpy(G)
        eigen = sorted(((float(c), v) for v,c in ecentrality.items()), reverse=True)

        # degree and weighted degree
        degree = list(map(list, [(k,v) for k, v in nx.degree(G)]))
        weighted_degree = list(map(list, [(k,v) for k, v in nx.degree(G, weight="Weight")]))

        # merge centrality measures
        centrality = pd.merge(pd.DataFrame(between), pd.DataFrame(eigen), on=1)
        centrality.columns = ["betweenness", "character", "eigenvector"]

        # merge degree measures
        degrees = pd.merge(pd.DataFrame(degree), pd.DataFrame(weighted_degree), on=0)
        degrees.columns = ["character", "degree", "weighted_degree"]

        # merge all
        metrics = pd.merge(centrality, degrees, on="character")
        metrics = metrics[['character', 'betweenness', 'eigenvector', 'degree', 'weighted_degree']]

        # Calculate + save ranked metric measures
        metric_ranks = metric_rankings(metrics)

        # Check for consistency
        len(metric_ranks) == len(count_ranks)

        # Combine tables
        print(f"Saving data for {target}...")

        count_ranks["character"] = [c.strip() for c in count_ranks["character"]]
        metric_ranks["character"] = [c.strip() for c in metric_ranks["character"]]

        # Save abridged ranks
        ranks = pd.merge(count_ranks, metric_ranks, left_on="character", right_on="character")
        ranks = ranks[["character", "line_rank", "word_rank", "WD_rank", "BC_rank"]]
        ranks.to_csv(f"{target}_abridged_ranks.csv", header=True, sep="\t")

        # Create a larger table that brings together all of our desired metrics into a single table.

        all_ranks = pd.merge(count_ranks, metric_ranks, left_on="character", right_on="character")
        all_ranks = all_ranks[["character", "lines", "words", "degree", "weighted_degree",
                                    "eigenvector", "betweenness", "line_rank", "word_rank", "degree_rank",
                                        "WD_rank","BC_rank", "EC_rank", "count_rank", "metrics_rank"]]
        all_ranks.to_csv(f"../data/tables/full/{target}_full_ranks.csv")

        # Calculate + save spearman's rho
        corr = ranks.corr(method='spearman').round(2)
        corr.to_csv(f"{target}.csv",header=True, sep="\t")

if __name__=="__main__":
    main()        
