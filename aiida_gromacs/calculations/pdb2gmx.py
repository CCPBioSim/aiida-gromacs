"""
Calculations provided by aiida_gromacs.

This calculation configures the ability to use the 'gmx pdb2gmx' executable.
"""

import os

from aiida.common import CalcInfo, CodeInfo
from aiida.engine import CalcJob
from aiida.orm import SinglefileData, Str
from aiida.plugins import DataFactory

Pdb2gmxParameters = DataFactory("gromacs.pdb2gmx")


class Pdb2gmxCalculation(CalcJob):
    """
    AiiDA calculation plugin wrapping the 'gmx pdb2gmx' executable.

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
        spec.inputs['metadata']['options']['parser_name'].default = 'gromacs.pdb2gmx'
        spec.input('metadata.options.output_filename', valid_type=str, default='pdb2gmx.out')
        spec.input('pdbfile', valid_type=SinglefileData, help='Input structure.')
        spec.input('parameters', valid_type=Pdb2gmxParameters, help='Command line parameters for gmx pdb2gmx')
        spec.input('metadata.options.output_dir', valid_type=str, default=os.getcwd(),
                help='Directory where output files will be saved when parsed.')

        # Default outputs.
        spec.output('stdout', valid_type=SinglefileData, help='stdout')
        spec.output('grofile', valid_type=SinglefileData, help='Output forcefield compliant file.')
        spec.output('topfile', valid_type=SinglefileData, help='Output forcefield compliant file.')
        spec.output('itpfile', valid_type=SinglefileData, help='Output forcefield compliant file.')

        # Optional outputs.
        spec.output('n_file', required=False, valid_type=SinglefileData, help='Output index file')
        spec.output('q_file', required=False, valid_type=SinglefileData, help='Output Structure file')

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
        output_options = ["o", "p", "i", "n", "q"]
        output_files = []

        # Add output files to retrieve list.
        output_files.append(self.metadata.options.output_filename)
        for item in output_options:
            if item in self.inputs.parameters:
                output_files.append(self.inputs.parameters[item])

        codeinfo.cmdline_params = self.inputs.parameters.cmdline_params(pdbfile=self.inputs.pdbfile.filename)
        codeinfo.code_uuid = self.inputs.code.uuid
        codeinfo.stdout_name = self.metadata.options.output_filename
        codeinfo.withmpi = self.inputs.metadata.options.withmpi

        # Prepare a `CalcInfo` to be returned to the engine
        calcinfo = CalcInfo()
        calcinfo.codes_info = [codeinfo]
        calcinfo.local_copy_list = [
            (
                self.inputs.pdbfile.uuid,
                self.inputs.pdbfile.filename,
                self.inputs.pdbfile.filename,
            ),
        ]
        calcinfo.retrieve_list = output_files

        return calcinfo
