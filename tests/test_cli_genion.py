"""Test for genion cli script"""

import os
import subprocess

from aiida.orm.nodes.process.process import ProcessState

from aiida_gromacs.utils import searchprevious

from . import TEST_DIR


def test_launch_genion():
    """
    Run an instance of genion.
    """
    # get input file paths
    top_file = os.path.join(TEST_DIR, "input_files", "genion_1AKI_topology.top")
    tpr_file = os.path.join(TEST_DIR, "input_files", "genion_1AKI_ions.tpr")

    subprocess.check_output(
        [
            "gmx_genion",
            "-s",
            tpr_file,
            "-p",
            top_file,
            "-pname",
            "NA",
            "-nname",
            "CL",
            "-neutral",
            "true",
            "-o",
            "1AKI_solvated_ions.gro",
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
