"""
Calculations provided by aiida_gromacs.

This calculation configures the ability to use the 'gmx grompp' executable.
"""

import os

from aiida.common import CalcInfo, CodeInfo
from aiida.engine import CalcJob
from aiida.orm import FolderData, SinglefileData, Str
from aiida.plugins import DataFactory

GromppParameters = DataFactory("gromacs.grompp")


class GromppCalculation(CalcJob):
    """
    AiiDA calculation plugin wrapping the 'gmx grompp' executable.

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
        spec.inputs['metadata']['options']['parser_name'].default = 'gromacs.grompp'
        spec.input('metadata.options.output_filename', valid_type=str, default='grompp.out')
        spec.input('mdpfile', valid_type=SinglefileData, help='grompp run file.')
        spec.input('grofile', valid_type=SinglefileData, help='Input structure')
        spec.input('topfile', valid_type=SinglefileData, help='Input topology')
        spec.input('parameters', valid_type=GromppParameters, help='Command line parameters for gmx grompp')
        spec.input('metadata.options.output_dir', valid_type=str, default=os.getcwd(),
                help='Directory where output files will be saved when parsed.')

        # Optional inputs.
        spec.input_namespace('itp_files', valid_type=SinglefileData, required=False, dynamic=True, 
                             help='Restraint files')
        spec.input_namespace('itp_dirs', valid_type=FolderData, required=False, dynamic=True, 
                             help='Forcefield descriptions')

        spec.input('r_file', valid_type=SinglefileData, required=False, help='Structure file')
        spec.input('rb_file', valid_type=SinglefileData, required=False, help='Structure file')
        spec.input('n_file', valid_type=SinglefileData, required=False, help='Index file')
        spec.input('t_file', valid_type=SinglefileData, required=False, help='Full precision trajectory file')
        spec.input('e_file', valid_type=SinglefileData, required=False, help='Energy file')
        spec.input('qmi_file', valid_type=SinglefileData, required=False, help='QM input file')
        spec.input('ref_file', valid_type=SinglefileData, required=False, help='Full precision trajectory file')

        # Default outputs.
        spec.output('stdout', valid_type=SinglefileData, help='stdout')
        spec.output('tprfile', valid_type=SinglefileData, help='Output gro file ready for adding ions.')

        # Optional outputs.
        spec.output('po_file', required=False, valid_type=SinglefileData, help='grompp input file with MD parameters')
        spec.output('pp_file', required=False, valid_type=SinglefileData, help='Topology file')
        spec.output('imd_file', required=False, valid_type=SinglefileData, help='Coordinate file in Gromos-87 format')

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
        input_options = [
            "mdpfile",
            "grofile",
            "topfile",
            "itp_files",
            "itp_dirs",
            "r_file",
            "rb_file",
            "n_file",
            "t_file",
            "e_file",
            "qmi_file",
            "ref_file",
        ]
        output_options = ["o", "po", "pp", "imd"]
        cmdline_input_files = {}
        input_files = []
        output_files = []

        # Map input files to AiiDA plugin data types.
        for item in input_options:
            if item in self.inputs:
                # If we have a dynamics data type then iterate the dict.
                if item == "itp_files":
                    for _, obj in self.inputs[item].items():
                        input_files.append(
                            (
                                obj.uuid,
                                obj.filename,
                                obj.filename,
                            )
                        )
                elif item == "itp_dirs":
                    for directory, obj in self.inputs[item].items():
                        input_files.append(
                            (
                                obj.uuid,
                                ".",
                                directory,
                            )
                        )
                else:
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

        codeinfo.code_uuid = self.inputs.code.uuid
        codeinfo.stdout_name = self.metadata.options.output_filename
        codeinfo.withmpi = self.inputs.metadata.options.withmpi

        # Prepare a `CalcInfo` to be returned to the engine
        calcinfo = CalcInfo()
        calcinfo.codes_info = [codeinfo]
        calcinfo.local_copy_list = input_files
        calcinfo.retrieve_list = output_files

        return calcinfo
