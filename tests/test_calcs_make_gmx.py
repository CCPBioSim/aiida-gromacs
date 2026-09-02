"""Tests for calculations"""

import os

from aiida.engine import run
from aiida.plugins import CalculationFactory, DataFactory

from . import TEST_DIR


def run_make_ndx(gromacs_code):
    """Run an instance of make_ndx and return the results."""

    # Prepare input parameters
    Make_ndxParameters = DataFactory("gromacs.make_ndx")
    parameters = Make_ndxParameters(
        {
            "o": "index.ndx",
        }
    )

    SinglefileData = DataFactory("core.singlefile")
    gro_file = SinglefileData(file=os.path.join(TEST_DIR, "input_files", "grompp2_1AKI_solvated_ions.gro"))
    n_file = SinglefileData(file=os.path.join(TEST_DIR, "input_files", "make_ndx_interactive_inputs.txt"))

    # set up calculation
    inputs = {
        "code": gromacs_code,
        "parameters": parameters,
        "grofile": gro_file,
        "instructions_file": n_file,
        "metadata": {
            "description": "make_ndx test",
            "options": {"stdin_filename": "make_ndx_interactive_inputs.txt"},
        },
    }

    result = run(CalculationFactory("gromacs.make_ndx"), **inputs)

    return result


def test_process(gromacs_code):
    """Test running a mdrun calculation.
    Note: this does not test that the expected outputs are created of output parsing"""

    result = run_make_ndx(gromacs_code)

    assert "stdout" in result
    assert "n_file_out" in result


def test_file_name_match(gromacs_code):
    """Test that the file names returned match what was specified on inputs."""

    result = run_make_ndx(gromacs_code)

    assert result["stdout"].base.repository.list_object_names()[0] == "make_ndx.out"
    assert result["n_file_out"].base.repository.list_object_names()[0] == "index.ndx"

    # check index file produced is the same in tests/input_files
    ref_n_file = os.path.join(TEST_DIR, "input_files", "make_ndx_index.ndx")
    with open(ref_n_file, encoding="utf-8") as f:
        content = f.read()
    with result["n_file_out"].open("index.ndx", "r") as f2:
        content2 = f2.read()
    assert content == content2
