"""Test for mdrun cli script"""

import os
import subprocess

from aiida.orm.nodes.process.process import ProcessState

from aiida_gromacs.utils import searchprevious

from . import TEST_DIR


def test_launch_mdrun():
    """
    Run an instance of mdrun.
    """
    # get input file paths
    tpr_file = os.path.join(TEST_DIR, "input_files", "mdrun_1AKI_em.tpr")

    subprocess.check_output(
        [
            "gmx_mdrun",
            "-s",
            tpr_file,
            "-c",
            "1AKI_minimised.gro",
            "-e",
            "1AKI_minimised.edr",
            "-g",
            "1AKI_minimised.log",
            "-o",
            "1AKI_minimised.trr",
            "-ntomp",
            "5",
            # "-ntmpi", # turn off omp and mpi for gmx patched with plumed
            # "1",
        ]
    )
    # append run process to qb
    # pylint: disable=unused-variable
    qb = searchprevious.build_query()
    # check the process has completed first
    # searchprevious.check_prev_process(qb)
    # pylint: disable=unsubscriptable-object
    prev_calc = qb.first()[0]
    # check the process has finished and exited correctly
    assert prev_calc.process_state == ProcessState.FINISHED
    assert prev_calc.exit_status == 0


def test_launch_mdrun_plumed():
    """
    Run an instance of mdrun.
    """
    # get input file paths
    tpr_file = os.path.join(TEST_DIR, "input_files", "plumed_mdrun_prod.tpr")
    plumed_file = os.path.join(TEST_DIR, "input_files", "plumed_mdrun_prod.dat")

    subprocess.check_output(
        [
            "gmx_mdrun",
            "-s",
            tpr_file,
            "-c",
            "plumed_mdrun_prod.gro",
            "-e",
            "plumed_mdrun_prod.edr",
            "-g",
            "plumed_mdrun_prod.log",
            "-o",
            "plumed_mdrun_prod.trr",
            "-plumed",
            plumed_file,
            "-ntomp",
            "5",
            "-ntmpi",  # set mpi threads to 1 when patched with plumed on conda
            "1",
        ]
    )
    # append run process to qb
    # pylint: disable=unused-variable
    qb = searchprevious.build_query()
    # check the process has completed first
    # searchprevious.check_prev_process(qb)
    # pylint: disable=unsubscriptable-object
    prev_calc = qb.first()[0]
    # check the process has finished and exited correctly
    assert prev_calc.process_state == ProcessState.FINISHED
    assert prev_calc.exit_status == 0
