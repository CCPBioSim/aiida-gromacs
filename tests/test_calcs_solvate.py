"""Tests for calculations"""

import os

from aiida.engine import run
from aiida.plugins import CalculationFactory, DataFactory

from . import TEST_DIR


def run_solvate(gromacs_code):
    """Run an instance of solvate and return the results."""

    # Prepare input parameters
    SolvateParameters = DataFactory("gromacs.solvate")
    parameters = SolvateParameters({"cs": "spc216.gro", "o": "solvate_1AKI_solvated.gro"})

    SinglefileData = DataFactory("core.singlefile")
    grofile = SinglefileData(file=os.path.join(TEST_DIR, "input_files", "solvate_1AKI_newbox.gro"))
    topfile = SinglefileData(file=os.path.join(TEST_DIR, "input_files", "solvate_1AKI_topology.top"))

    # set up calculation
    inputs = {
        "code": gromacs_code,
        "parameters": parameters,
        "grofile": grofile,
        "topfile": topfile,
        "metadata": {
            "description": "solvate test",
        },
    }

    result = run(CalculationFactory("gromacs.solvate"), **inputs)

    return result


def test_process(gromacs_code):
    """Test running a solvate calculation.
    Note: this does not test that the expected outputs are created of output parsing"""

    result = run_solvate(gromacs_code)

    assert "stdout" in result
    assert "grofile" in result
    assert "topfile" in result


def test_file_name_match(gromacs_code):
    """Test that the file names returned match what was specified on inputs."""

    result = run_solvate(gromacs_code)

    assert result["stdout"].base.repository.list_object_names()[0] == "solvate.out"
    assert result["grofile"].base.repository.list_object_names()[0] == "solvate_1AKI_solvated.gro"
    assert result["topfile"].base.repository.list_object_names()[0] == "solvate_1AKI_topology.top"
