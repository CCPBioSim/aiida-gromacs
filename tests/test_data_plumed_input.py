"""Test for plumed input parser functions"""

import os

from aiida_gromacs.data.plumed_input import PlumedInputData


def test_PlumedInputData():
    """test for checking all inputs and outputs parsed from plumed input file
    are collected."""
    inputs = {}
    # Prepare input parameters in AiiDA formats.
    # Set the plumed script as a PlumedInputData type node
    inputs["plumedscript"] = PlumedInputData(file=os.path.join(os.getcwd(), "tests/input_files", "mdrun_plumed.dat"))

    # Find the inputs and outputs referenced in the plumed script
    calc_inputs, calc_outputs = inputs["plumedscript"].calculation_inputs_outputs
    # print(calc_inputs["plumed_inpfiles"].keys(), calc_outputs["plumed_outfiles"])
    # add input files and dirs referenced in plumed file into inputs
    inputs.update(calc_inputs)
    inputs.update(calc_outputs)

    assert calc_outputs["plumed_outfiles"] == [
        "HILLS1",
        "HILLS2",
        "HILLS3",
        "HILLS4",
        "HILLS5",
        "HILLS6",
        "HILLS7",
        "HILLS8",
        "HILLS9",
        "COLVAR1",
        "COLVAR2",
        "COLVAR3",
        "COLVAR4",
        "COLVAR5",
        "COLVAR5b",
        "COLVAR6",
        "COLVAR7",
        "COLVAR6b",
        "COLVAR7b",
        "COLVAR8",
        "COLVAR9",
        "COLVAR8b",
        "COLVAR9b",
        "COLVAR10",
        "COLVAR11",
        "COLVAR10b",
        "COLVAR11b",
        "COLVAR12",
        "COLVAR13",
        "COLVAR12b",
        "COLVAR13b",
        "COLVAR14",
        "COLVAR15",
        "COLVAR16",
        "COLVAR14b",
        "COLVAR15b",
        "COLVAR16b",
    ]
    assert "plumed_input_test1" in calc_inputs["plumed_inpfiles"].keys()
    assert "plumed_input_test2" in calc_inputs["plumed_inpfiles"].keys()
