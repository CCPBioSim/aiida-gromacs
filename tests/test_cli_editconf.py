"""Test for editconf cli script"""

import os
import subprocess

from aiida.orm.nodes.process.process import ProcessState

from aiida_gromacs.utils import searchprevious

from . import TEST_DIR


def test_launch_editconf():
    """
    Run an instance of editconf.
    """
    # get input file paths
    gro_file = os.path.join(TEST_DIR, "input_files", "editconf_1AKI_forcefield.gro")

    subprocess.check_output(
        [
            "gmx_editconf",
            "-f",
            gro_file,
            "-center",
            "0",
            "-d",
            "1.0",
            "-bt",
            "cubic",
            "-o",
            "1AKI_newbox.gro",
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
