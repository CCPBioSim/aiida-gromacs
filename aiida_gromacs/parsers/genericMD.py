"""
Parsers provided by aiida_gromacs.

This parser saves outputted files from a generic command.
"""

import re

from aiida.common import exceptions
from aiida.engine import ExitCode
from aiida.orm import SinglefileData
from aiida.parsers.parser import Parser
from aiida.plugins import CalculationFactory

from aiida_gromacs.utils import fileparsers

# entry point string under which the parser class is registered:
GenericCalculation = CalculationFactory("gromacs.genericMD")


class GenericParser(Parser):
    """
    Parser class for parsing output of genericMD calculation from which
    the retrieved outputs files from the calcjob and the nodes of finished
    calculation can be accessed.
    """

    def __init__(self, node):
        """
        Initialize Parser instance

        Checks that the ProcessNode being passed was produced by a
        GenericCalculation.

        :param node: ProcessNode of calculation
        :param type node: :class:`aiida.orm.nodes.process.process.ProcessNode`
        """
        super().__init__(node)
        if not issubclass(node.process_class, GenericCalculation):
            raise exceptions.ParsingError("Can only parse GenericCalculation")

    def parse(self, **kwargs):
        """
        Parse outputs, store results in the AiiDA database.

        :returns: an exit code, if parsing fails or the user defined
            output files are not returned
        """

        # get_option() convenience method is used to get the filename of
        # the output file
        output_filename = self.node.get_option("output_filename")
        # the directory for storing parsed output files
        output_dir = self.node.get_option("output_dir")

        # Check that folder content is as expected
        files_retrieved = self.retrieved.list_object_names()
        files_expected = []  # [output_filename]
        if "output_files" in self.node.inputs:
            for name in self.node.inputs.output_files:
                files_expected.extend([str(name)])

        # Check all outputted files produced have been previously
        # defined by the user
        for file in files_expected:
            if file not in files_retrieved:
                self.logger.error(
                    f"User defined output file '{file}' not in list of retrieved files '{files_retrieved}'"
                )
                return self.exit_codes.ERROR_UNTRACKED_OUTPUT_FILES

        # passing along the std output file as a SinglefileData node.
        self.logger.info(f"Parsing '{output_filename}'")
        with self.retrieved.open(output_filename, "rb") as handle:
            output_node = SinglefileData(file=handle)

        # passing along all expected output file as SinglefileData nodes.
        for thing in files_expected:
            self.logger.info(f"Parsing '{thing}'")
            with self.retrieved.open(thing, "rb") as handle:
                output_node = SinglefileData(file=handle, filename=thing)
            self.out(self.format_link_label(thing), output_node)

        fileparsers.parse_process_files(self, files_retrieved, output_dir)

        return ExitCode(0)

    @staticmethod
    def format_link_label(filename: str) -> str:
        """
        Modified from: https://github.com/sphuber/aiida-shell/blob/master/src/aiida_shell/parsers/shell.py
        Format the link label from a given filename with prefix.
        Valid link labels can only contain alphanumeric characters and
        underscores, without consecutive underscores. So all characters
        that are not alphanumeric or an underscore are converted to
        underscores, where consecutive underscores are merged into one.
        Additional: Label cannot start with a number or underscore.

        :param filename: The filename.
        :returns: The link label.
        """
        filename = filename.split("/")[-1]
        if filename[0].isdigit() or filename[0] == "_":
            filename = "output_files_" + filename
        alphanumeric = re.sub("[^0-9a-zA-Z_]+", "_", filename)
        link_label = re.sub("_[_]+", "_", alphanumeric)

        return link_label
