"""
Calculations provided by aiida_gromacs.

This calculation configures the ability to use the 'gmx make_ndx' executable.
"""

import os

from aiida.common import CalcInfo, CodeInfo
from aiida.engine import CalcJob
from aiida.orm import SinglefileData, Str
from aiida.plugins import DataFactory

Make_ndxParameters = DataFactory("gromacs.make_ndx")


class Make_ndxCalculation(CalcJob):
    """
    AiiDA calculation plugin wrapping the 'gmx make_ndx' executable.

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
        # TODO: remove this for production release.
        spec.inputs['metadata']['options']['max_wallclock_seconds'].default = 86400
        spec.inputs['metadata']['options']['resources'].default = {
            'num_machines': 1,
            'num_mpiprocs_per_machine': 1,
            'num_cores_per_mpiproc': 5,
        }

        # Required inputs.
        spec.inputs['metadata']['options']['parser_name'].default = 'gromacs.make_ndx'
        spec.input('metadata.options.output_filename', valid_type=str, default='make_ndx.out')
        spec.input('parameters', valid_type=Make_ndxParameters, help='Command line parameters for gmx make_ndx')
        spec.input(
            'metadata.options.filename_stdin',
            valid_type=str,
            required=False,
            help='Filename that should be redirected to the shell command using the stdin file descriptor.',
        )
        spec.input('grofile', valid_type=SinglefileData, required=False, help='Structure file: gro g96 pdb brk ent ' \
        'esp tpr')
        spec.input('instructions_file', valid_type=SinglefileData, required=False, help='Instructions for generating ' \
        'index file')
        spec.input('metadata.options.stdin_filename', valid_type=str, help='name of file used in stdin.')
        spec.input('metadata.options.output_dir', valid_type=str, default=os.getcwd(),
                help='Directory where output files will be saved when parsed.')

        # Optional inputs.
        spec.input('n_file', valid_type=SinglefileData, required=False, help='Index file')

        # Required outputs.
        spec.output('stdout', valid_type=SinglefileData, help='stdout')
        spec.output('n_file_out', valid_type=SinglefileData, help='Index file')

        # Include Optional outputs here.

        spec.exit_code(300, 'ERROR_MISSING_OUTPUT_FILES', message='Calculation did not produce all expected ' \
        'output files.')

    def prepare_for_submission(self, folder):
        """
        Create input files.

        :param folder: an `aiida.common.folders.Folder` where the plugin should temporarily place all files
            needed by the calculation.
        :return: `aiida.common.datastructures.CalcInfo` instance
        """
        codeinfo = CodeInfo()

        # Setup data structures for files.
        input_options = ["grofile", "n_file", "instructions_file"]
        output_options = ["o"]
        cmdline_input_files = {}
        input_files = []
        output_files = []

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

        # Add output files to retrieve list.
        output_files.append(self.metadata.options.output_filename)
        for item in output_options:
            if item in self.inputs.parameters:
                output_files.append(self.inputs.parameters[item])

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
        calcinfo.retrieve_list = output_files

        return calcinfo
