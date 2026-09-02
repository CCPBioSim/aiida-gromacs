#!/usr/bin/env python
"""CLI utility to run gmx grompp with AiiDA.

Usage: gmx_grompp --help
"""

import os

import click
from aiida import cmdline, engine
from aiida.plugins import CalculationFactory, DataFactory

from aiida_gromacs import helpers
from aiida_gromacs.utils import searchprevious, topfile_utils


def launch(params):
    """Run grompp.

    Uses helpers to add gromacs on localhost to AiiDA on the fly.
    """

    # Prune unused CLI parameters from dict.
    params = {k: v for k, v in params.items() if v is not None}

    # dict to hold our calculation data.
    inputs = {
        "metadata": {
            "description": params.pop("description"),
        },
    }

    # If code is not initialised, then setup.
    if "code" in inputs:
        inputs["code"] = params.pop("code")
    else:
        computer = helpers.get_computer()
        inputs["code"] = helpers.get_code(entry_point="gromacs", computer=computer)

    # save the full command as a string in the inputs dict
    inputs = searchprevious.save_command("gmx grompp", params, inputs)

    input_file_labels = {}  # dict used for finding previous nodes
    input_file_labels[params["f"]] = "mdpfile"
    input_file_labels[params["c"]] = "grofile"
    input_file_labels[params["p"]] = "topfile"

    # Prepare input parameters in AiiDA formats.
    SinglefileData = DataFactory("core.singlefile")
    FolderData = DataFactory("core.folder")
    inputs["mdpfile"] = SinglefileData(file=os.path.join(os.getcwd(), params.pop("f")))
    inputs["grofile"] = SinglefileData(file=os.path.join(os.getcwd(), params.pop("c")))
    inputs["topfile"] = SinglefileData(file=os.path.join(os.getcwd(), params.pop("p")))

    # Find itp files and FF reference files.
    itp_files, itp_dirs = topfile_utils.itp_finder(inputs["mdpfile"], inputs["topfile"])

    # If we have itp's or FF include files then tag them.
    if itp_files is not False:
        inputs["itp_files"] = {}

        # Iterate files to assemble a dict of names and paths.
        for i, itpfile in enumerate(itp_files):
            # set correct itpfile path for tests
            if "PYTEST_CURRENT_TEST" in os.environ:
                inputs["itp_files"][f"itpfile{i}"] = SinglefileData(
                    file=os.path.join(os.getcwd(), "tests/input_files", itpfile)
                )
            else:
                inputs["itp_files"][f"itpfile{i}"] = SinglefileData(file=os.path.join(os.getcwd(), itpfile))

    # If we have included files in subdirs then process these.
    if itp_dirs is not False:
        inputs["itp_dirs"] = {}

        # for each entry establish dir path and build file tree.
        for itp_file in itp_dirs:
            # Create a folder that is empty.
            if itp_file.split("/")[0] not in inputs["itp_dirs"].keys():
                inputs["itp_dirs"][itp_file.split("/")[0]] = FolderData()

            # Now fill it with files referenced in the topology.
            inputs["itp_dirs"][itp_file.split("/")[0]].put_object_from_file(
                os.path.join(os.getcwd(), itp_file), path=itp_file
            )  # .split("/")[-1])

    if "r" in params:
        inputs["r_file"] = SinglefileData(file=os.path.join(os.getcwd(), params.pop("r")))

    if "rb" in params:
        inputs["rb_file"] = SinglefileData(file=os.path.join(os.getcwd(), params.pop("rb")))

    if "n" in params:
        inputs["n_file"] = SinglefileData(file=os.path.join(os.getcwd(), params.pop("n")))

    if "t" in params:
        inputs["t_file"] = SinglefileData(file=os.path.join(os.getcwd(), params.pop("t")))

    if "e" in params:
        inputs["e_file"] = SinglefileData(file=os.path.join(os.getcwd(), params.pop("e")))

    if "qmi" in params:
        inputs["qmi_file"] = SinglefileData(file=os.path.join(os.getcwd(), params.pop("qmi")))

    if "ref" in params:
        inputs["ref_file"] = SinglefileData(file=os.path.join(os.getcwd(), params.pop("ref")))

    GromppParameters = DataFactory("gromacs.grompp")
    inputs["parameters"] = GromppParameters(params)

    # check if inputs are outputs from prev processes
    inputs = searchprevious.link_previous_file_nodes(input_file_labels, inputs)

    # check if a pytest test is running, if so run rather than submit aiida job
    # Note: in order to submit your calculation to the aiida daemon, do:
    if "PYTEST_CURRENT_TEST" in os.environ:
        engine.run(CalculationFactory("gromacs.grompp"), **inputs)
    else:
        engine.submit(CalculationFactory("gromacs.grompp"), **inputs)


@click.command()
@cmdline.utils.decorators.with_dbenv()
@cmdline.params.options.CODE()
@click.option(
    "--description",
    default="record grompp data provenance via the aiida_gromacs plugin",
    type=str,
    help="Short metadata description",
)
# Input file options
@click.option("-f", default="grompp.mdp", type=str, help="Input parameter file")
@click.option("-c", required=True, type=str, help="Input structure file")
@click.option("-r", type=str, help="Structure file: gro g96 pdb brk ent esp tpr")
@click.option("-rb", type=str, help="Structure file: gro g96 pdb brk ent esp tpr")
@click.option("-n", type=str, help="Index file")
@click.option("-p", default="topol.top", type=str, help="Topology file")
@click.option("-t", type=str, help="Full precision trajectory: trr cpt tng")
@click.option("-e", type=str, help="Energy file")
@click.option("-qmi", type=str, help="Input file for QM program")
@click.option("-ref", type=str, help="Full precision trajectory: trr cpt tng")
# Output file options
@click.option("-o", default="conf.gro", type=str, help="Output structure file")
@click.option("-po", type=str, help="grompp input file with MD parameters")
@click.option("-pp", type=str, help="Topology file")
@click.option("-imd", type=str, help="Coordinate file in Gromos-87 format")
# Other parameter options
@click.option("-v", type=str, help="Be loud and noisy")
@click.option("-time", type=str, help="Take frame at or first after this time.")
@click.option("-rmvsbds", type=str, help="Remove constant bonded interactions with virtual sites")
@click.option(
    "-maxwarn",
    type=str,
    help="Number of allowed warnings during input processing. Not for normal use and may generate unstable systems",
)
@click.option(
    "-zero",
    type=str,
    help="Set parameters for bonded interactions without defaults to zero instead of generating an error",
)
@click.option("-renum", type=str, help="Renumber atomtypes and minimize number of atomtypes")
def cli(*args, **kwargs):
    """Run example.

    Example usage:

    $ gmx_grompp --code gmx@localhost -f ions.mdp -c 1AKI_solvated.gro -p 1AKI_topology.top -o 1AKI_ions.tpr

    Alternative (automatically tried to create gmx@localhost code, but requires
    gromacs to be installed and available in your environment path):

    $ gmx_grompp -f ions.mdp -c 1AKI_solvated.gro -p 1AKI_topology.top -o 1AKI_ions.tpr

    Help: $ gmx_grompp --help
    """

    launch(kwargs)


if __name__ == "__main__":
    cli()
