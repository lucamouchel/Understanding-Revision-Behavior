# Understanding Revision Behavior

This repository is the official implementation of the paper submitted at EDM 2023 entitled "Understanding Revision Behavior in Adaptive Writing Support Systems in Education", by Luca Mouchel, Thiemo Wambsganss, Paola Mejia and Tanja Käser.

`RevisionBehavior.ipynb` is the principal component of this study, combining most of the useful tools to study and visualize revision behavior.
Otherwise `src/scripts/` consists of additional files to apply pattern mining, process mining and extract keystroke features.

## Project Overview
We analyze log data from a writing experiment (`data/keystroke-recipes.csv`) to measure users' self-regulated learning and observe revision behavior by extracting multiple keystroke features. A description of our analysis and results can be consulted in our paper. 

We apply a pattern mining algorithm on insert-delete sequences to extract relevant sequences groups have in common (more in `src/scripts/patternmining.py`) and process mining to produce directly-follows graphs on event logs (availabe at `data/eventlogs`) recording user activity in each group (`src/scripts/processmining.py`).

This project started in September 2022 at EPFL and has been accepted at EDM 2023 as a poster paper, taking place in Bangalore, India.

## Usage guide
- Install relevant dependencies with `pip install -r requirements.txt`, or simply run `RevisionBehavior.ipynb`, this command is already implemented. 

- You can also run the scripts for pattern mining and process mining to generate DFGs and observe common patterns.

- Results can already be observed in `results/`, where multiple plots and figures are already available.

## Contributing
This code is provided for educational purposes and aims to facilitate reproduction of our results, and further research in this direction. We have done our best to document, refactor our code.

If you find this code useful for any related works and research, please cite our work with the following : TODO

If you find any bugs or would like to contribute please let us know. Feel free to file issues and pull requests on the repo and we will address them as we can.

## License 
This code is free software: you can redistribute it and/or modify it under the terms of the MIT License.

This software is distributed in the hope that it will be useful, but without any warranty; without even the implied warranty of merchantability or fitness for a particular purpose. See the MIT License for details.
