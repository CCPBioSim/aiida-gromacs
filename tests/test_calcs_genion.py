"""Tests for calculations"""

import os

from aiida.engine import run
from aiida.plugins import CalculationFactory, DataFactory

from . import TEST_DIR


def run_genion(bash_code):
    """Run an instance of genion and return the results."""

    # Prepare input parameters
    GenionParameters = DataFactory("gromacs.genion")
    parameters = GenionParameters(
        {
            "o": "genion_1AKI_solvated_ions.gro",
            "pname": "NA",
            "nname": "CL",
            "neutral": "true",
        }
    )

    SinglefileData = DataFactory("core.singlefile")
    tprfile = SinglefileData(file=os.path.join(TEST_DIR, "input_files", "genion_1AKI_ions.tpr"))
    topfile = SinglefileData(file=os.path.join(TEST_DIR, "input_files", "genion_1AKI_topology.top"))

    # set up calculation
    inputs = {
        "code": bash_code,
        "parameters": parameters,
        "tprfile": tprfile,
        "topfile": topfile,
        "metadata": {
            "description": "genion test",
        },
    }

    result = run(CalculationFactory("gromacs.genion"), **inputs)

    return result


def test_process(bash_code):
    """Test running a genion calculation.
    Note: this does not test that the expected outputs are created of output parsing"""

    result = run_genion(bash_code)

    assert "stdout" in result
    assert "grofile" in result
    assert "topfile" in result


def test_file_name_match(bash_code):
    """Test that the file names returned match what was specified on inputs."""

    result = run_genion(bash_code)

    assert result["stdout"].base.repository.list_object_names()[0] == "genion.out"
    assert result["grofile"].base.repository.list_object_names()[0] == "genion_1AKI_solvated_ions.gro"
    assert result["topfile"].base.repository.list_object_names()[0] == "genion_1AKI_topology.top"
