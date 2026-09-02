#!/usr/bin/env python
"""CLI utility to run gmx mdrun with AiiDA.

Usage: gmx_mdrun --help
"""

import os

import click
from aiida import cmdline, engine
from aiida.plugins import CalculationFactory, DataFactory

from aiida_gromacs import helpers
from aiida_gromacs.data.plumed_input import populate_plumed_files_to_inputs
from aiida_gromacs.utils import searchprevious


def launch(params):
    """Run mdrun.

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
    inputs = searchprevious.save_command("gmx mdrun", params, inputs)

    input_file_labels = {}  # dict used for finding previous nodes
    input_file_labels[params["s"]] = "tprfile"
    if "plumed" in params:
        input_file_labels[params["plumed"]] = "plumed_file"

    # Prepare input parameters in AiiDA formats.
    SinglefileData = DataFactory("core.singlefile")
    inputs["tprfile"] = SinglefileData(file=os.path.join(os.getcwd(), params.pop("s")))

    if "cpi" in params:
        inputs["cpi_file"] = SinglefileData(file=os.path.join(os.getcwd(), params.pop("cpi")))

    if "table" in params:
        inputs["table_file"] = SinglefileData(file=os.path.join(os.getcwd(), params.pop("table")))

    if "tableb" in params:
        inputs["tableb_file"] = SinglefileData(file=os.path.join(os.getcwd(), params.pop("tableb")))

    if "tablep" in params:
        inputs["tablep_file"] = SinglefileData(file=os.path.join(os.getcwd(), params.pop("tablep")))

    if "rerun" in params:
        inputs["rerun_file"] = SinglefileData(file=os.path.join(os.getcwd(), params.pop("rerun")))

    if "ei" in params:
        inputs["ei_file"] = SinglefileData(file=os.path.join(os.getcwd(), params.pop("ei")))

    if "multidir" in params:
        inputs["multidir_file"] = SinglefileData(file=os.path.join(os.getcwd(), params.pop("multidir")))

    if "awh" in params:
        inputs["awh_file"] = SinglefileData(file=os.path.join(os.getcwd(), params.pop("awh")))

    if "membed" in params:
        inputs["membed_file"] = SinglefileData(file=os.path.join(os.getcwd(), params.pop("membed")))

    if "mp" in params:
        inputs["mp_file"] = SinglefileData(file=os.path.join(os.getcwd(), params.pop("mp")))

    if "mn" in params:
        inputs["mn_file"] = SinglefileData(file=os.path.join(os.getcwd(), params.pop("mn")))

    if "plumed" in params:
        inputs = populate_plumed_files_to_inputs(inputs, params.pop("plumed"))

    MdrunParameters = DataFactory("gromacs.mdrun")
    inputs["parameters"] = MdrunParameters(params)

    # check if inputs are outputs from prev processes
    inputs = searchprevious.link_previous_file_nodes(input_file_labels, inputs)

    # check if a pytest test is running, if so run rather than submit aiida job
    # Note: in order to submit your calculation to the aiida daemon, do:
    if "PYTEST_CURRENT_TEST" in os.environ:
        engine.run(CalculationFactory("gromacs.mdrun"), **inputs)
    else:
        engine.submit(CalculationFactory("gromacs.mdrun"), **inputs)


@click.command()
@cmdline.utils.decorators.with_dbenv()
@cmdline.params.options.CODE()
# Plugin options
@click.option(
    "--description",
    default="record mdrun data provenance via the aiida_gromacs plugin",
    type=str,
    help="Short metadata description",
)
# Input file options
@click.option("-s", default="topol.tpr", type=str, help="Portable xdr run input file")
@click.option("-cpi", type=str, help="Checkpoint file")
@click.option("-table", type=str, help="xvgr/xmgr file")
@click.option("-tablep", type=str, help="xvgr/xmgr file")
@click.option("-tableb", type=str, help="xvgr/xmgr file")
@click.option("-rerun", type=str, help="Trajectory: xtc trr cpt gro g96 pdb tng")
@click.option("-ei", type=str, help="ED sampling input")
@click.option("-multidir", type=str, help="Run directory")
@click.option("-awh", type=str, help="xvgr/xmgr file")
@click.option("-membed", type=str, help="Generic data file")
@click.option("-mp", type=str, help="Topology file")
@click.option("-mn", type=str, help="Index file")
@click.option("-plumed", type=str, help="PLUMED input file")
# Output file options
@click.option("-o", default="topol.gro", type=str, help="Trajectory output file")
@click.option("-x", type=str, help="Compressed trajectory (tng format or portable xdr format)")
@click.option("-cpo", type=str, help="Checkpoint file")
@click.option("-c", default="confout.gro", type=str, help="Structure file")
@click.option("-e", default="ener.edr", type=str, help="Energy file")
@click.option("-g", default="md.log", type=str, help="MD log file")
@click.option("-dhdl", type=str, help="xvgr/xmgr file")
@click.option("-field", type=str, help="xvgr/xmgr file")
@click.option("-tpi", type=str, help="xvgr/xmgr file")
@click.option("-tpid", type=str, help="xvgr/xmgr file")
@click.option("-eo", type=str, help="xvgr/xmgr file")
@click.option("-px", type=str, help="xvgr/xmgr file")
@click.option("-pf", type=str, help="xvgr/xmgr file")
@click.option("-ro", type=str, help="xvgr/xmgr file")
@click.option("-ra", type=str, help="Log file")
@click.option("-rs", type=str, help="Log file")
@click.option("-rt", type=str, help="Log file")
@click.option("-mtx", type=str, help="Hessian matrix")
@click.option("-if", type=str, help="xvgr/xmgr file")
@click.option("-swap", type=str, help="xvgr/xmgr file")
# Other parameters
@click.option("-xvg", default="none", type=str, help="xvg plot formatting: xmgrace, xmgr, none")
@click.option("-dd", type=str, help="Domain decomposition grid, 0 is optimize")
@click.option("-ddorder", type=str, help="DD rank order: interleave, pp_pme, cartesian")
@click.option("-npme", type=str, help="Number of separate ranks to be used for PME, -1 is guess")
@click.option("-nt", type=str, help="Total number of threads to start (0 is guess)")
@click.option("-ntmpi", type=str, help="Number of thread-MPI ranks to start (0 is guess)")
@click.option("-ntomp", type=str, help="Number of OpenMP threads per MPI rank to start (0 is guess)")
@click.option("-ntomp_pme", type=str, help="Number of OpenMP threads per MPI rank to start (0 is -ntomp)")
@click.option("-pin", type=str, help="Whether mdrun should try to set thread affinities: auto, on, off")
@click.option("-pinoffset", type=str, help="The lowest logical core number to which mdrun should pin the first thread")
@click.option(
    "-pinstride",
    type=str,
    help="Pinning distance in logical cores for threads, use 0 to minimize the number of threads per physical core",
)
@click.option("-gpu_id", type=str, help="List of unique GPU device IDs available to use")
@click.option("-gputasks", type=str, help="List of GPU device IDs, mapping each PP task on each node to a device")
@click.option("-ddcheck", type=str, help="Check for all bonded interactions with DD")
@click.option(
    "-rdd",
    type=str,
    help="The maximum distance for bonded interactions with DD (nm), 0 is determine from initial coordinates",
)
@click.option("-rcon", type=str, help="Maximum distance for P-LINCS (nm), 0 is estimate")
@click.option("-dlb", type=str, help="Dynamic load balancing (with DD): auto, no, yes")
@click.option(
    "-dds",
    type=str,
    help="Fraction in (0,1) by whose reciprocal the initial DD cell size will be increased in order to provide a "
    "margin in which dynamic load balancing can act while preserving the minimum cell size.",
)
@click.option("-nb", type=str, help="Calculate non-bonded interactions on: auto, cpu, gpu")
@click.option("-nstlist", type=str, help="Set nstlist when using a Verlet buffer tolerance (0 is guess)")
@click.option("-tunepme", type=str, help="Optimize PME load between PP/PME ranks or GPU/CPU")
@click.option("-pme", type=str, help="Perform PME calculations on: auto, cpu, gpu")
@click.option("-pmefft", type=str, help="Perform PME FFT calculations on: auto, cpu, gpu")
@click.option("-bonded", type=str, help="Perform bonded calculations on: auto, cpu, gpu")
@click.option("-update", type=str, help="Perform update and constraints on: auto, cpu, gpu")
@click.option("-v", type=str, help="Be loud and noisy")
@click.option("-pforce", type=str, help="Print all forces larger than this (kJ/mol nm)")
@click.option("-reprod", type=str, help="Try to avoid optimizations that affect binary reproducibility")
@click.option("-cpt", type=str, help="Checkpoint interval (minutes)")
@click.option("-cpnum", type=str, help="Keep and number checkpoint files")
@click.option(
    "-append",
    type=str,
    help="Append to previous output files when continuing from checkpoint instead of adding the simulation part "
    "number to all file names",
)
@click.option(
    "-nsteps",
    type=str,
    help="Run this number of steps (-1 means infinite, -2 means use mdp option, smaller is invalid)",
)
@click.option("-maxh", type=str, help="Terminate after 0.99 times this time (hours)")
@click.option("-replex", type=str, help="Attempt replica exchange periodically with this period (steps)")
@click.option(
    "-nex",
    type=str,
    help="Number of random exchanges to carry out each exchange interval (N^3 is one suggestion). -nex zero or "
    "not specified gives neighbor replica exchange.",
)
@click.option("-reseed", type=str, help="Seed for replica exchange, -1 is generate a seed")
def cli(*args, **kwargs):
    """Run example.

    Example usage:

    $ gmx_mdrun --code gmx@localhost -s 1AKI_em.tpr -c 1AKI_minimised.gro \
        -e 1AKI_minimised.edr -g 1AKI_minimised.log -o 1AKI_minimised.trr

    Alternative (automatically tried to create gmx@localhost code, but requires
    gromacs to be installed and available in your environment path):

    $ gmx_mdrun -s 1AKI_em.tpr -c 1AKI_minimised.gro \
        -e 1AKI_minimised.edr -g 1AKI_minimised.log -o 1AKI_minimised.trr

    Help: $ gmx_mdrun --help
    """

    launch(kwargs)


if __name__ == "__main__":
    cli()
