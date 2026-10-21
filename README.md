# aiida-gromacs
| Category       | Badges |
|----------------|--------|
| **Build**      | [![PR Checks](https://github.com/CCPBioSim/aiida-gromacs/actions/workflows/pr.yaml/badge.svg)](https://github.com/CCPBioSim/aiida-gromacs/actions/workflows/pr.yaml) [![Daily Tests](https://github.com/CCPBioSim/aiida-gromacs/actions/workflows/daily.yaml/badge.svg)](https://github.com/CCPBioSim/aiida-gromacs/actions/workflows/daily.yaml) [![Dependency Floors](https://github.com/CCPBioSim/aiida-gromacs/actions/workflows/dependency-floors.yaml/badge.svg)](https://github.com/CCPBioSim/aiida-gromacs/actions/workflows/dependency-floors.yaml) |
| **Documentation** | [![Weekly Docs](https://github.com/CCPBioSim/aiida-gromacs/actions/workflows/weekly-docs.yaml/badge.svg)](https://github.com/CCPBioSim/aiida-gromacs/actions/workflows/weekly-docs.yaml) [![Docs status](https://readthedocs.org/projects/aiida-gromacs/badge)](http://aiida-gromacs.readthedocs.io/) |
| **Citation**      | [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18392289.svg)](https://doi.org/10.5281/zenodo.18392289) |
| **PyPI**       | ![PyPI - Status](https://img.shields.io/pypi/status/aiida-gromacs?logo=pypi&logoColor=white) [![PyPI version](https://badge.fury.io/py/aiida-gromacs.svg)](https://badge.fury.io/py/aiida-gromacs)  ![PyPI - Python Version](https://img.shields.io/pypi/pyversions/aiida-gromacs) ![PyPI - Total Downloads](https://img.shields.io/pepy/dt/aiida-gromacs?logo=pypi&logoColor=white&color=blue) ![PyPI - Monthly Downloads](https://img.shields.io/pypi/dm/aiida-gromacs?logo=pypi&logoColor=white&color=blue)|
| **Anaconda**       | [![Anaconda.org](https://anaconda.org/CCPBioSim/aiida-gromacs/badges/version.svg)](https://anaconda.org/CCPBioSim/aiida-gromacs/) [![Last Updated](https://anaconda.org/CCPBioSim/aiida-gromacs/badges/latest_release_date.svg)](https://anaconda.org/CCPBioSim/aiida-gromacs) [![Platforms](https://anaconda.org/CCPBioSim/aiida-gromacs/badges/platforms.svg)](https://anaconda.org/CCPBioSim/aiida-gromacs) [![License](https://anaconda.org/CCPBioSim/aiida-gromacs/badges/license.svg)](https://anaconda.org/CCPBioSim/aiida-gromacs) [![Downloads](https://anaconda.org/CCPBioSim/aiida-gromacs/badges/downloads.svg)](https://anaconda.org/CCPBioSim/aiida-gromacs)|
| **Quality**    | [![Coverage Status](https://coveralls.io/repos/github/CCPBioSim/aiida-gromacs/badge.svg?branch=main)](https://coveralls.io/github/CCPBioSim/aiida-gromacs?branch=main) |

The GROMACS plugin for AiiDA aims to enable the capture and sharing of the full
provenance of data when parameterising and running molecular dynamics
simulations. This plugin is being developed as part of the Physical Sciences
Data Infrastructure programme to improve the practices around data within the
Physical Sciences remit area within the UK.

This package is currently a work in progress and we will be adding much more
complete functionality to this plugin in the coming months.

The design pattern we are aiming for is to simply allow researchers to capture
the full data provenance for their simulations by only switching on an AiiDA
conda environment, along with modifying your command lines very slightly.

This means that you should gain access to powerful FAIR data practices without
wholesale cultural or usage pattern shifts in your daily work.

<p align="center">
    <img src="docs/source/images/aiida-gromacs-logo.svg" alt="aiida-gromacs logo" width="300"/>
</p>

## Documentation

See [here](https://aiida-gromacs.readthedocs.io/en/latest/) for documentation for users and developers.

## License

MIT

## Contact

- james.gebbie@stfc.ac.uk
- jas.kalayan@stfc.ac.uk
