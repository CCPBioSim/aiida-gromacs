""" Test for pdb2gmx cli script

"""

import os
import subprocess

from aiida.orm.nodes.process.process import ProcessState

from aiida_gromacs.utils import searchprevious

from . import TEST_DIR


def test_launch_pdb2gmx():
    """
    Run an instance of pdb2gmx.
    """
    # get input file paths
    pdb_file = os.path.join(TEST_DIR, "input_files", "pdb2gmx_1AKI_clean.pdb")

    subprocess.check_output(
        [
            "gmx_pdb2gmx",
            "-f",
            pdb_file,
            "-ff",
            "oplsaa",
            "-water",
            "spce",
            "-o",
            "1AKI_forcefield.gro",
            "-p",
            "1AKI_topology.top",
            "-i",
            "1AKI_restraints.itp",
        ]
    )
    # append run process to qb
    qb = searchprevious.build_query()
    prev_calc = qb.first()[0]
    # check the process has finished and exited correctly
    assert prev_calc.process_state == ProcessState.FINISHED
    assert prev_calc.exit_status == 0