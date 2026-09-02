#!/usr/bin/env python
"""
Create AiiDA database archive from loaded profile.
"""

from aiida import load_profile
import subprocess
import click
import os

def create_archive(options):
    """
    Create .aiida file of archived database.
    https://aiida.readthedocs.io/projects/aiida-core/en/latest/howto/share_data.html
    """
    output_file = options["filename"]
    load_profile()
    # Run the `verdi archive create` command using subprocess
    subprocess.run(['verdi', 'archive', 'create', '--all', output_file])


@click.command()
@click.option(
    "--filename",
    default=os.path.join(os.getcwd()) + "/archive.aiida",
    type=str,
    help="path + filename of AiiDA database archive to be saved.",
)
def cli(**kwargs):
    """Create AiiDA archive file.

    Example usage:

    $ createarchive.py --filename archive.aiida

    Help: $ createarchive.py --help
    """
    create_archive(kwargs)


if __name__ == "__main__":
    cli()

