"""
Parsers provided by aiida_gromacs.

This calculation configures the ability to use the 'gmx mdrun' executable.
"""

import json
import os
from pathlib import Path
import tempfile

from aiida.common import exceptions
from aiida.engine import ExitCode
from aiida.orm import Dict, SinglefileData
from aiida.parsers.parser import Parser
from aiida.plugins import CalculationFactory

from aiida_gromacs.utils import fileparsers, inputFile_utils

MdrunCalculation = CalculationFactory("gromacs.mdrun")


class MdrunParser(Parser):
    """
    Parser class for parsing output of calculation.
    """

    def __init__(self, node):
        """
        Initialize Parser instance

        Checks that the ProcessNode being passed was produced by a MdrunCalculation.

        :param node: ProcessNode of calculation
        :param type node: :class:`aiida.orm.nodes.process.process.ProcessNode`
        """
        super().__init__(node)
        if not issubclass(node.process_class, MdrunCalculation):
            raise exceptions.ParsingError("Can only parse MdrunCalculation")

    def parse(self, **kwargs):
        """
        Parse outputs, store results in database.

        :returns: an exit code, if parsing fails (or nothing if parsing succeeds)
        """
        # the directory for storing parsed output files
        output_dir = Path(self.node.get_option("output_dir"))
        # Map output files to how they are named.
        outputs = ["stdout"]
        output_template = {
            "c": "grofile",
            "e": "enfile",
            "g": "logfile",
            "o": "trrfile",
            "x": "x_file",
            "cpo": "cpo_file",
            "dhdl": "dhdl_file",
            "field": "field_file",
            "tpi": "tpi_file",
            "tpid": "tpid_file",
            "eo": "eo_file",
            "px": "px_file",
            "pf": "pf_file",
            "ro": "ro_file",
            "ra": "ra_file",
            "rs": "rs_file",
            "rt": "rt_file",
            "mtx": "mtx_file",
            "if": "if_file",
            "swap": "swap_file",
        }

        for item in output_template:
            if item in self.node.inputs.parameters.keys():
                outputs.append(output_template[item])

        # check if there are any plumed output files and add these to the outputs list
        if "plumed_outfiles" in self.node.inputs:
            for name in self.node.inputs.plumed_outfiles:
                # make sure the node name is formatted correctly
                outputs.extend([f"plumed_{inputFile_utils.format_link_label(str(name))}"])

        # Grab list of retrieved files.
        files_retrieved = self.retrieved.base.repository.list_object_names()

        # Grab list of files expected and remove the scheduler stdout and stderr files.
        files_expected = [
            files
            for files in self.node.get_option("retrieve_list")
            if files not in ["_scheduler-stdout.txt", "_scheduler-stderr.txt"]
        ]

        # check if any trajectory file is in files_retrieved
        files_retrieved, files_expected = MdrunParser.check_trajectory_format(files_retrieved, files_expected)

        # Check if the expected files are a subset of retrieved.
        if not set(files_expected) <= set(files_retrieved):
            self.logger.error(f"Found files '{files_retrieved}', expected to find '{files_expected}'.")
            return self.exit_codes.ERROR_MISSING_OUTPUT_FILES

        # Map retrieved files to data nodes.
        for i, f in enumerate(files_expected):
            self.logger.info(f"Parsing '{f}'")
            with self.retrieved.base.repository.open(f, "rb") as handle:
                output_node = SinglefileData(filename=f, file=handle)
            self.out(outputs[i], output_node)
            # Include file parsers here
            if outputs[i] == "logfile":

                with tempfile.TemporaryDirectory(prefix="mdrun_metadata_") as temp_dir:
                    temp_dir = Path(temp_dir)
                        
                    topology_node = self.node.inputs.tprfile
                    topology_path = self.copy_repository_file(
                        topology_node.base.repository,
                        topology_node.filename,
                        temp_dir,
                    )

                    trajectory_index = outputs.index("trrfile")
                    trajectory_f = files_expected[trajectory_index]
                    trajectory_path = self.copy_repository_file(
                        self.retrieved,
                        trajectory_f,
                        temp_dir,
                    )

                    log_path = self.copy_repository_file(
                        self.retrieved,
                        f,
                        temp_dir,
                    )

                    MdrunParser.parse_file_contents(
                        self,
                        topology_path,
                        trajectory_path,
                        log_path,
                        temp_dir,
                        fileparsers.extract_gromacs_files,
                        node_name="simulation_metadata",
                    )

        # If not in testing mode, then copy back the files.
        if "PYTEST_CURRENT_TEST" not in os.environ:
            self.retrieved.copy_tree(output_dir)

        return ExitCode(0)

    def copy_repository_file(self, repository, filename, output_dir):
        """Copy a repository file to output_dir and return its local path."""
        output_dir.mkdir(parents=True, exist_ok=True)
        destination = output_dir / filename

        with repository.open(filename, "rb") as source, destination.open("wb") as target:
            target.write(source.read())

        return destination

    def parse_file_contents(self, top_file, traj_file, log_file, output_dir, parser_func, node_name):
        """
        Read in the gromacs output file, save into a dictionary node and
        output dictionary as a json file.

        :param top_file: temp path to topology file
        :param traj_file: temp path to trajectory file
        :param log_file: temp path to log file
        :param output_dir: temp path to where json file should be saved
        :param parser_func: the function used to parse the file f
        :type parser_func: `class 'function'`
        :param node_name: the name of the outputted Dict node
        :type node_name: str
        """
        metadata_dict = parser_func(top_file, traj_file, log_file)
        metadata_node = Dict(metadata_dict)
        self.out(node_name, metadata_node)
        MdrunParser.output_parsed_metadata(log_file, output_dir, metadata_dict)

    def output_parsed_metadata(f, output_dir, metadata_dict):
        """
        Save a dictionary into a json file if not in testing mode.

        :param f: the name of the file node outputted from mdrun
        :param output_dir: path to where json file should be saved
        :param metadata_dict: the aiida dictionary containing metadata
        """
        # If not in testing mode, then copy back dict as json file.
        if "PYTEST_CURRENT_TEST" not in os.environ:
            f_prefix = f.stem
            file_path = os.path.join(output_dir, f"{f_prefix}_metadata.json")
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(metadata_dict, f, ensure_ascii=False, indent=4)

    def check_trajectory_format(files_retrieved: list, files_expected: list):
        """
        In the case where nstxout-compressed = >0, gromacs should produce a
        xtc file instead of what is requested for -o flag in mdrun. Check
        if an unexpected xtc file is produced, if so, add this to
        files_expected, and if a file defined from the -o file is not in the
        files_retrieved list, then remove it as we have the xtc file instead.

        :param files_retrieved: list of file names returned from calc
        :param files_expected: list of file names expected to be returned
            from calc
        """
        for file in files_retrieved:
            if file.split(".")[-1] == "xtc":
                if file not in files_expected:
                    files_expected.append(file)
                for file2 in files_expected:
                    if file2.split(".")[-1] in ["trr", "cpt", "tng"] and file2 not in files_retrieved:
                        files_expected.remove(file2)
        return files_retrieved, files_expected
