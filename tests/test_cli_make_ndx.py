"""Test for mdrun cli script"""

import os
import subprocess

from aiida.orm.nodes.process.process import ProcessState

from aiida_gromacs.utils import searchprevious

from . import TEST_DIR


def test_launch_make_ndx():
    """
    Run an instance of mdrun.
    """
    # get input file paths
    gro_file = os.path.join(TEST_DIR, "input_files", "grompp2_1AKI_solvated_ions.gro")
    n_file = os.path.join(TEST_DIR, "input_files", "make_ndx_interactive_inputs.txt")

    subprocess.check_output(
        [
            "gmx_make_ndx",
            "-f",
            gro_file,
            "--instructions",
            n_file,
        ]
    )
    # append run process to qb
    qb = searchprevious.build_query()
    # check the process has completed first
    # searchprevious.check_prev_process(qb)
    prev_calc = qb.first()[0]
    # check the process has finished and exited correctly
    assert prev_calc.process_state == ProcessState.FINISHED
    assert prev_calc.exit_status == 0
