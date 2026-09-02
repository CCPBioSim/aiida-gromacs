"""Test for solvate cli script"""

import os
import subprocess

from aiida.orm.nodes.process.process import ProcessState

from aiida_gromacs.utils import searchprevious

from . import TEST_DIR


def test_launch_solvate():
    """
    Run an instance of solvate.
    """
    # get input file paths
    top_file = os.path.join(TEST_DIR, "input_files", "solvate_1AKI_topology.top")
    gro_file = os.path.join(TEST_DIR, "input_files", "solvate_1AKI_newbox.gro")

    subprocess.check_output(
        [
            "gmx_solvate",
            "-cp",
            gro_file,
            "-cs",
            "spc216.gro",
            "-p",
            top_file,
            "-o",
            "1AKI_solvated.gro",
        ]
    )
    # append run process to qb
    # pylint: disable=unused-variable
    qb = searchprevious.build_query()
    # pylint: disable=unsubscriptable-object
    prev_calc = qb.first()[0]
    # check the process has finished and exited correctly
    assert prev_calc.process_state == ProcessState.FINISHED
    assert prev_calc.exit_status == 0
