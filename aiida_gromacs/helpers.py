""" Helper functions for automatically setting up computer & code.
Helper functions for setting up

 1. An AiiDA localhost computer
 2. A "gmx" code on localhost

Note: Point 2 is made possible by the fact that the ``diff`` executable is
available in the PATH on almost any UNIX system.
"""
import shutil
import tempfile

from aiida.common.exceptions import NotExistent
from aiida.common import exceptions
from aiida.orm import InstalledCode, Computer, load_code

LOCALHOST_NAME = "localhost"

executables = {
    "gromacs": "gmx",
    "bash": "bash",
}


def get_path_to_executable(executable):
    """Get path to local executable.
    
    :param executable: Name of executable in the $PATH variable
    :type executable: str
    :return: path to executable
    :rtype: str
    """
    path = shutil.which(executable)
    if path is None:
        raise ValueError(f"'{executable}' executable not found in PATH.")
    return path


def get_computer(name=LOCALHOST_NAME, workdir=None):
    """Get AiiDA computer.
    Loads computer 'name' from the database, if exists.
    Sets up local computer 'name', if it isn't found in the DB.

    :param name: Name of computer to load or set up.
    :param workdir: path to work directory
        Used only when creating a new computer.
    :return: The computer node
    :rtype: :py:class:`aiida.orm.computers.Computer`
    """

    try:
        computer = Computer.collection.get(label=name)
    except NotExistent:
        if workdir is None:
            workdir = tempfile.mkdtemp()

        computer = Computer(
            label=name,
            description="localhost computer set up by aiida-gromacs plugin",
            hostname=name,
            workdir=workdir,
            transport_type="core.local",
            scheduler_type="core.direct",
        )
        computer.store()
        computer.set_minimum_job_poll_interval(0.0)
        computer.configure()

    return computer


def get_code(entry_point, computer):
    """Get local code.
    Sets up code for given entry point on given computer.

    :param entry_point: Entry point of calculation plugin
    :param computer: (local) AiiDA computer
    :return: The code node
    :rtype: :py:class:`aiida.orm.nodes.data.code.installed.InstalledCode`
    """

    try:
        executable = executables[entry_point]
    except KeyError as exc:
        raise KeyError(
            f"Entry point '{entry_point}' not recognized. Allowed values: {list(executables.keys())}"
        ) from exc

    codes = InstalledCode.collection.find(
        filters={"label": executable}
    )  # pylint: disable=no-member
    if codes:
        return codes[0]

    path = get_path_to_executable(executable)
    code = InstalledCode(
        label = executable,
        default_calc_job_plugin=entry_point,
        computer=computer,
        filepath_executable=path,
    )

    return code.store()


def setup_generic_code(code):
    """Try to set up any code for running a genericMD process

    :param code: executable@computer of the code being run
    """
    # Create or load code
    try:
        code = load_code(code)
    except exceptions.NotExistent:
        # Setting up code via python API (or use "verdi code setup")
        executable = code.split('@')[0]
        path = get_path_to_executable(executable)
        code = InstalledCode(
            label=executable, computer= get_computer(), 
            filepath_executable=path, 
            default_calc_job_plugin='genericMD'
        )
    return code
