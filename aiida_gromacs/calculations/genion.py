"""
Calculations provided by aiida_gromacs.

This calculation configures the ability to use the 'gmx genion' executable.
"""

import os

from aiida.common import CalcInfo, CodeInfo
from aiida.engine import CalcJob
from aiida.orm import SinglefileData, Str
from aiida.plugins import DataFactory

GenionParameters = DataFactory("gromacs.genion")


class GenionCalculation(CalcJob):
    """
    AiiDA calculation plugin wrapping the 'gmx genion' executable.

    AiiDA plugin wrapper for converting PDB files to GRO files.
    """

    @classmethod
    def define(cls, spec):
        """Define inputs and outputs of the calculation."""
        # yapf: disable
        super().define(spec)

        # Define inputs and outputs of the calculation.
        spec.input('command',
                valid_type=Str, required=False,
                help='The command used to execute the job.')

        # set default values for AiiDA options
        # TODO: something changed about withmpi in aiida-2.4.0, needs investigation.
        spec.inputs['metadata']['options']['withmpi'].default = False
        spec.inputs['metadata']['options']['resources'].default = {
            'num_machines': 1,
            'num_mpiprocs_per_machine': 1,
        }

        # Required inputs.
        spec.inputs['metadata']['options']['parser_name'].default = 'gromacs.genion'
        spec.input('metadata.options.output_filename', valid_type=str, default='genion.out')
        spec.input('tprfile', valid_type=SinglefileData, help='Input tpr file.')
        spec.input('topfile', valid_type=SinglefileData, help='Input topology file.')
        spec.input('parameters', valid_type=GenionParameters, help='Command line parameters for gmx genion')
        spec.input('metadata.options.output_dir', valid_type=str, default=os.getcwd(),
                help='Directory where output files will be saved when parsed.')

        # Optional inputs.
        spec.input(
            'metadata.options.filename_stdin',
            valid_type=str,
            required=False,
            help='Filename that should be redirected to the shell command using the stdin file descriptor.',
        )
        spec.input('instructions_file', valid_type=SinglefileData, required=False, help='Instructions for generating ' \
        'index file')
        spec.input('metadata.options.stdin_filename', valid_type=str, required=False, help='name of file used in ' \
        'stdin.')
        spec.input('n_file', required=False, valid_type=SinglefileData, help='Index file.')

        # Default outputs.
        spec.output('stdout', valid_type=SinglefileData, help='stdout')
        spec.output('grofile', valid_type=SinglefileData, help='Output gro file with ions added.')
        spec.output('topfile', valid_type=SinglefileData, help='Output topology with ions added.')

        spec.exit_code(300, 'ERROR_MISSING_OUTPUT_FILES', message='Calculation did not produce all expected output ' \
        'files.')

    def prepare_for_submission(self, folder):
        """
        Create input files.

        :param folder: an `aiida.common.folders.Folder` where the plugin should temporarily place all files
            needed by the calculation.
        :return: `aiida.common.datastructures.CalcInfo` instance
        """
        codeinfo = CodeInfo()

        # Setup data structures for files.
        input_options = ["tprfile", "topfile", "n_file", "instructions_file"]
        cmdline_input_files = {}
        input_files = []

        # Map input files to AiiDA plugin data types.
        for item in input_options:
            if item in self.inputs:
                cmdline_input_files[item] = self.inputs[item].filename
                input_files.append(
                    (
                        self.inputs[item].uuid,
                        self.inputs[item].filename,
                        self.inputs[item].filename,
                    )
                )

        # Form the commandline.
        codeinfo.cmdline_params = self.inputs.parameters.cmdline_params(cmdline_input_files)

        # Form stdin file for index instructions
        codeinfo.stdin_name = self.inputs["metadata"]["options"].get("stdin_filename", None)

        codeinfo.code_uuid = self.inputs.code.uuid
        codeinfo.stdout_name = self.metadata.options.output_filename
        codeinfo.withmpi = self.inputs.metadata.options.withmpi

        # Prepare a `CalcInfo` to be returned to the engine
        calcinfo = CalcInfo()
        calcinfo.codes_info = [codeinfo]
        calcinfo.local_copy_list = input_files
        calcinfo.retrieve_list = [
            self.metadata.options.output_filename,
            self.inputs.parameters["o"],
            self.inputs.topfile.filename,
        ]

        return calcinfo
