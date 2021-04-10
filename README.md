# ProdigalNetworks

This repository contains code and repo in relation the following publication:

Ladegaard, J. & Kristensen-McLachlan, R.D. (2021). "*Prodigal Heirs and Their Social Networks in Early Modern English Drama, 1590–1640*", Law and Literature, doi: [10.1080/1535685X.2021.1902635](https://doi.org/10.1080/1535685X.2021.1902635)

In this article, we present the results of a network analysis on a collection of Early Modern English plays related to the theme of prodigality.

## Content

All code used in the article can be found in the folder ```src```. All code is written in Python and is modular. Scripts are numbered sequentially, in the order that they should be executed, with each creating transformed data for the next script to use.

The is presented for evaluative purposes only. These scripts require substantial refactoring in order to be considered production-ready. 

The results of the final script in ```src``` is a weighted edgelist, which is to then be read into the network analysis software [Gephi](https://gephi.org/).

## Output

There are a number of relevant and interrelated outputs in the ```output``` folder. These are:

| File | Description|
|--------|:-----------|
| edgelists | Weighted edgelsits of character interactions, one per play, for use in something like Gephi|
| graphs | Graph files created by Gephi, one per play |
| tables | Abridge and complete tables of network metrics, one per play|

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
