# cyclonic-wind-impacts

This repository contains companion code for our study of future changes in European windstorm characteristics under different climate scenarios. If you use the code, **please cite the paper**:

> Little, A.S., Priestley, M.D.K. & Catto, J.L. Future increased risk from extratropical windstorms in northern Europe. *Nat Commun* 14, 4434 (2023). https://doi.org/10.1038/s41467-023-40102-6

![alt text](https://media.springernature.com/full/springer-static/image/art%3A10.1038%2Fs41467-023-40102-6/MediaObjects/41467_2023_40102_Fig3_HTML.png?as=webp)

## Installation 
The code was originally used in an isolated Python 3.8 environment. Besides [numpy](https://github.com/numpy/numpy) and [pandas](https://github.com/pandas-dev/pandas), the packages required include:
- [xarray](https://github.com/pydata/xarray): Handles multi-dimensional (e.g., spatio-temporal) arrays
- [b2sdk](https://github.com/Backblaze/b2-sdk-python): Provides access to data in B2 cloud storage
- [netCDF4](https://github.com/Unidata/netcdf4-python): Enables `xarray` to read NetCDF files
- [tqdm](https://github.com/tqdm/tqdm): Displays progress bar during analysis

Assuming `conda` is installed, an environment can be setup in a local version of the repository as follows:
```
conda create --name=cyclonic-wind-impacts python=3.8
conda activate cyclonic-wind-impacts
conda install --file requirements.txt
```
The code has only been tested on machines running MacOS 12 (Monterey) and MacOS 13 (Ventura).

## Data
We used three sets of input data in our study, all stored on a private encrypted BackBlaze bucket owned by the main author. These must be downloaded to a local repository *prior* to analysis by running `python get_data.py`. The ID/key pair needed to access the API are hardcoded into this file; there is no security risk as the full contents of the bucket are non-sensitive and open-access.

| Name | Source | File type | Total size | 
| :--- | :----: | :----: | ---:
| Wind field | ERA5/CMIP6 data nodes (re-gridded) | NetCDF| ~650 MB|
| Tracks | Derived using objective feature tracking | Text| ~554 MB|
| Population | NASA SEDAC (re-gridded) | NetCDF| ~35 KB|

Full details of the sources and processing steps used to generate these input data are outlined in the companion [paper](https://doi.org/10.1038/s41467-023-40102-6). Notably, the objective feature tracking code belongs to Kevin Hodges and is available [here](https://gitlab.act.reading.ac.uk/track/track). 

> **Note:**  There is a daily data bandwidth limit associated with the BackBlaze bucket, as it is operated on a free plan. This unfortunately means that downloads via the API are limited to **1 request per day**.

## Analysis

The full analysis comprises two main steps, each of which applies a series of purpose-built functions to all individual cyclone tracks in the selected experiment/model combinations:
- **Wind footprints**: Generate cyclonic wind speed maps
- **Storm severity index**: Calculate `MET-SSI` and `SOC-SSI` maps

One or both steps can be executed as follows (must be in this order):
```
python generate_footprints.py
python generate_ssis.py
```

All cyclone maps produced are saved to the `outputs/` directory, which is structured similarly to that of `data/`. Examples can be seen in figures accompanying the main text of the companion [paper](https://doi.org/10.1038/s41467-023-40102-6).

Several key parameters underpinning the model can be configured in `params.py`. This allows the following tasks to be achieved readily:
- Explore the effects on model outputs when perturbing a single variable
- Reduce the extent of the domain bounding box *and/or* experiment/model combinations, for shorter computation times

## License
This code is licensed under the GNU General Public License v3.0.

## Author
Alex Little 

[![LinkedIn](https://img.shields.io/badge/linkedin-%230077B5.svg?style=for-the-badge&logo=linkedin&logoColor=white)](www.linkedin.com/in/alexslittle)

## Acknowledgements
Thanks to the co-authors for assisting with code structure and development throughout the project:
- Matthew Priestley
- Jennifer Catto
