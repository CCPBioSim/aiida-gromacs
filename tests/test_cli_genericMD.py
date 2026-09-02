"""Test for genericMD cli script"""

import os
import subprocess
import tempfile

from aiida.orm.nodes.process.process import ProcessState

from aiida_gromacs.utils import searchprevious

from . import TEST_DIR


def test_launch_genericMD():
    """
    Run an instance of genericMD using the grompp gmx command
    as an example.
    """
    # get input file paths
    top_file = os.path.join(TEST_DIR, "input_files", "grompp_ions.mdp")
    mdp_file = os.path.join(TEST_DIR, "input_files", "solvate_1AKI_topology.top")
    gro_file = os.path.join(TEST_DIR, "input_files", "solvate_1AKI_newbox.gro")
    with tempfile.TemporaryDirectory() as temp_dir:
        output_dir = os.path.join(TEST_DIR, temp_dir)
    subprocess.check_output(
        [
            "genericMD",
            "--code",
            "gmx@localhost",
            "--command",
            "grompp -o 1AKI_ions.tpr -f grompp_ions.mdp -c solvate_1AKI_newbox.gro -p solvate_1AKI_topology.top",
            "--inputs",
            mdp_file,
            "--inputs",
            top_file,
            "--inputs",
            gro_file,
            "--outputs",
            "1AKI_ions.tpr",
            "--output_dir",
            output_dir,
        ]
    )
    # append run process to qb
    qb = searchprevious.build_query()
    prev_calc = qb.first()[0]
    # check the process has finished and exited correctly
    assert prev_calc.process_state == ProcessState.FINISHED
    assert prev_calc.exit_status == 0
