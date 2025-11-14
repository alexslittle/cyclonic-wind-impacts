This repository contains companion code for our study of future changes in European windstorm characteristics under different climate scenarios. If you use the code, please cite the paper:

> Little, A.S., Priestley, M.D.K. & Catto, J.L. Future increased risk from extratropical windstorms in northern Europe. *Nat Commun* 14, 4434 (2023). https://doi.org/10.1038/s41467-023-40102-6

![alt text](https://media.springernature.com/full/springer-static/image/art%3A10.1038%2Fs41467-023-40102-6/MediaObjects/41467_2023_40102_Fig3_HTML.png?as=webp)

## Data

Full details of the sources and processing steps used to generate input data are outlined in the companion [paper](https://doi.org/10.1038/s41467-023-40102-6). Notably, the objective feature tracking code belongs to Kevin Hodges and is available [here](https://gitlab.act.reading.ac.uk/track/track). 

## Analysis

The full analysis comprises two main steps, each of which applies a series of purpose-built functions to individual cyclone tracks:
1. **Wind speed**: Generate wind speed footprint map
2. **Storm severity index**: Generate MET-SSI and SOC-SSI map

Key parameters can be configured in `params.py`, e.g. to explore the effects on model outputs when perturbing a single variable.
