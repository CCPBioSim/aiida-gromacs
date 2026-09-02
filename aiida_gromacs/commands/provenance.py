#!/usr/bin/env python
"""
Show text output of the provenance of commands performed in gmx
"""

import click

from aiida_gromacs.utils.displayprovenance import show_provenance_text


@click.group()
def provenance():
    """commandline help for provenance command
    Help: $ verdi data provenance --help"""


@provenance.command("show")
def show_provanance():
    """Print out the provenance of aiida-gromacs processes run on current
    loaded aiida profile

    Help: $ verdi data provenance show --help"""
    show_provenance_text()
