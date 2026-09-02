""" Test for grompp cli script

"""

import os
import subprocess

from aiida.orm.nodes.process.process import ProcessState

from aiida_gromacs.utils import searchprevious

from . import TEST_DIR


def test_launch_grompp():
    """
    Run an instance of grompp.
    """
    # get input file paths
    mdp_file = os.path.join(TEST_DIR, "input_files", "grompp_ions.mdp")
    gro_file = os.path.join(TEST_DIR, "input_files", "grompp_1AKI_solvated.gro")
    top_file = os.path.join(TEST_DIR, "input_files", "grompp_1AKI_topology.top")

    subprocess.check_output(
        [
            "gmx_grompp", 
            "-f", 
            mdp_file, 
            "-c", 
            gro_file, 
            "-p", 
            top_file, 
            "-o", 
            "1AKI_ions.tpr",
        ]
    )
    # append run process to qb
    qb = searchprevious.build_query()
    prev_calc = qb.first()[0]
    # check the process has finished and exited correctly
    assert prev_calc.process_state == ProcessState.FINISHED
    assert prev_calc.exit_status == 0


def test_launch_grompp2():
    """
    Run an instance of grompp.
    """
    # get input file paths
    mdp_file = os.path.join(TEST_DIR, "input_files", "grompp2_min.mdp")
    gro_file = os.path.join(TEST_DIR, "input_files", "grompp2_1AKI_solvated_ions.gro")
    top_file = os.path.join(TEST_DIR, "input_files", "grompp2_1AKI_topology.top")

    subprocess.check_output(
        [
            "gmx_grompp", 
            "-f", 
            mdp_file, 
            "-c", 
            gro_file, 
            "-p", 
            top_file, 
            "-o", 
            "1AKI_min.tpr",
        ]
    )
    # append run process to qb
    qb = searchprevious.build_query()
    prev_calc = qb.first()[0]
    # check the process has finished and exited correctly
    assert prev_calc.process_state == ProcessState.FINISHED
    assert prev_calc.exit_status == 0


def test_launch_grompp3():
    """
    Run an instance of grompp.
    """
    # get input file paths
    mdp_file = os.path.join(TEST_DIR, "input_files", "grompp3_nvt.mdp")
    gro_file = os.path.join(TEST_DIR, "input_files", "grompp3_1AKI_minimised.gro")
    top_file = os.path.join(TEST_DIR, "input_files", "grompp2_1AKI_topology.top")
    # itp_file = os.path.join(TEST_DIR, "input_files", "1AKI_restraints.itp")

    subprocess.check_output(
        [
            "gmx_grompp", 
            "-f", 
            mdp_file, 
            "-c", 
            gro_file, 
            "-r", 
            gro_file, 
            "-p", 
            top_file, 
            "-o", 
            "1AKI_nvt.tpr", 
        ]
    )
    # append run process to qb
    qb = searchprevious.build_query()
    prev_calc = qb.first()[0]
    # check the process has finished and exited correctly
    assert prev_calc.process_state == ProcessState.FINISHED
    assert prev_calc.exit_status == 0