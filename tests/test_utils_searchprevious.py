"""Test for searchprevious utility functions"""

import os

from aiida import orm

from aiida_gromacs.utils import searchprevious

from . import test_calcs_genericMD


def test_link_formats():
    """
    Tests if given strings are formatted correctly with format_link_label
    function
    """

    str1 = searchprevious.format_link_label("1?.consecutive__underscores..txt")
    assert str1 == "1_consecutive_underscores_txt"


def test_qb_returns(gromacs_code):
    """
    Test for checking a query returns the correct outputs

    :param gromacs_code: The query entries of previous processes in the AiiDA database
    :type gromacs_code: :py:class:`aiida.orm.nodes.data.code.installed.InstalledCode`
    """

    # pylint: disable=unused-variable
    result, output_dir = test_calcs_genericMD.run_genericMD_pdb2gmx(gromacs_code)
    qb = searchprevious.build_query()
    expected_outputs = [
        "log",
        "pdb2gmx_1AKI_forcefield_gro",
        "pdb2gmx_1AKI_restraints_itp",
        "pdb2gmx_1AKI_topology_top",
        "remote_folder",
        "retrieved",
    ]
    retrieved_outputs = list(qb.all()[0][0].outputs)
    assert retrieved_outputs.sort() == expected_outputs.sort()


def test_previous_input_retrieval(gromacs_code):
    """
    Tests whether outputs from a previous process are used as inputs for
    a current process

    :param gromacs_code: The query entries of previous processes in the AiiDA database
    :type gromacs_code: :py:class:`aiida.orm.nodes.data.code.installed.InstalledCode`
    """

    # pylint: disable=unused-variable
    result, output_dir = test_calcs_genericMD.run_genericMD_pdb2gmx(gromacs_code)

    qb = searchprevious.build_query()

    # input files used in editconf command
    inputs = ["pdb2gmx_1AKI_forcefield.gro"]
    input_files = {}
    for filename in list(inputs):
        file_path = os.path.join(output_dir, filename)
        input_files["grofile"] = orm.SinglefileData(file=file_path)

    # output files produced from editconf command
    output_files = [
        "editconf_1AKI_newbox.gro",
    ]

    # full editconf command to run
    command = "editconf -f pdb2gmx_1AKI_forcefield.gro -center 0 0 0 -d 1.0 -bt cubic -o editconf_1AKI_newbox.gro"

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

    # check if previous processes have run and add previous outputs
    # as inputs for new process if file names match
    process_inputs_new = {}
    if qb.count() > 0:
        process_inputs_new = searchprevious.append_prev_nodes(qb, inputs, process_inputs.copy(), output_dir)

    # check output grofile from pdb2gmx process is an input in the
    # editconf process
    assert "grofile" in process_inputs["input_files"]
    assert "pdb2gmx_1AKI_forcefield_gro" in process_inputs_new["input_files"]
