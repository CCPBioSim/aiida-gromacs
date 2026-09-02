"""Test for genericMD calculation"""

import os
import shutil
import tempfile

from aiida import orm
from aiida.engine import run
from aiida.plugins import CalculationFactory

from . import TEST_DIR


def check_output_path(output_dir):
    """Delete existing output_dir and create a new one

    :param output_dir: directory path to check existence of
    :type output_dir: str
    """
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
        os.makedirs(output_dir)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)


def run_genericMD_pdb2gmx(gromacs_code):
    """Run an instance of genericMD and return the results of the calculation.
    Used as an example calculation for tests.

    :param gromacs_code: The query entries of previous processes in the AiiDA database
    :type gromacs_code: :py:class:`aiida.orm.nodes.data.code.installed.InstalledCode`
    :returns: Results from genericMD calculation
    :rtype: dict
    """

    # input files used in pdb2gmx command
    inputs = ["pdb2gmx_1AKI_clean.pdb"]
    input_files = {}
    for filename in list(inputs):
        file_path = os.path.join(TEST_DIR, "input_files", filename)
        input_files["pdbfile"] = orm.SinglefileData(file=file_path)

    # output files produced from pdb2gmx command
    output_files = [
        "pdb2gmx_1AKI_restraints.itp",
        "pdb2gmx_1AKI_topology.top",
        "pdb2gmx_1AKI_forcefield.gro",
    ]

    # full pdb2gmx command to run
    command = (
        "pdb2gmx -i pdb2gmx_1AKI_restraints.itp "
        "-o pdb2gmx_1AKI_forcefield.gro -p pdb2gmx_1AKI_topology.top "
        "-ff oplsaa -water spce -f pdb2gmx_1AKI_clean.pdb"
    )

    # set path to temp dir
    with tempfile.TemporaryDirectory() as temp_dir:
        output_dir = os.path.join(TEST_DIR, temp_dir)

    # check output_dir doesn't already exist
    check_output_path(output_dir)

    # create input dictionary for calculation.
    process_inputs = {
        "code": gromacs_code,
        "command": orm.Str(command),
        "input_files": input_files,
        "output_files": orm.List(output_files),
        "metadata": {
            "label": "generic-execute",
            "description": "Run CLI job and save input and output file provenance.",
            "options": {
                "output_filename": "file.out",
                "output_dir": output_dir,
                "parser_name": "gromacs.genericMD",
            },
        },
    }

    # run calculation via aiida
    result = run(CalculationFactory("gromacs.genericMD"), **process_inputs)

    return result, output_dir


def test_process(gromacs_code):
    """Test running a genericMD calculation using the pdb2gmx command as
    an example.
    Note: this does not test that the expected outputs are created of
    output parsing"""

    result, output_dir = run_genericMD_pdb2gmx(gromacs_code)

    assert "pdb2gmx_1AKI_forcefield_gro" in result
    assert "pdb2gmx_1AKI_topology_top" in result
    assert "pdb2gmx_1AKI_restraints_itp" in result


def test_file_name_match(gromacs_code):
    """Test that the file names returned match what was specified on inputs."""

    result, output_dir = run_genericMD_pdb2gmx(gromacs_code)

    assert result["pdb2gmx_1AKI_forcefield_gro"].base.repository.list_object_names()[0] == "pdb2gmx_1AKI_forcefield.gro"
    assert result["pdb2gmx_1AKI_topology_top"].base.repository.list_object_names()[0] == "pdb2gmx_1AKI_topology.top"
    assert result["pdb2gmx_1AKI_restraints_itp"].base.repository.list_object_names()[0] == "pdb2gmx_1AKI_restraints.itp"
