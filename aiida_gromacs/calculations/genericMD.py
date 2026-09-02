"""
Generic calculation used to track input and output files of a
generic command.
"""

import os

from aiida.common import datastructures
from aiida.engine import CalcJob
from aiida.orm import List, SinglefileData, Str


class GenericCalculation(CalcJob):
    """
    AiiDA calculation plugin wrapping an executable with user defined
    input and output files.
    """

    @classmethod
    def define(cls, spec):
        """
        AiiDA plugin wrapper for running an arbitrary command.
        """
        # yapf: disable

        # defines the inputs and outputs that are common to all CalcJobs.
        super().define(spec) # calls define method of the CalcJob parent class

        # Define inputs and outputs of the calculation.
        spec.input('command',
                valid_type=Str, required=False,
                help='The command used to execute the job.')

        # dynamic dict of inputs instead of specifying each one.
        spec.input_namespace(
            'input_files',
            valid_type=SinglefileData,
            required=False,
            help='Dictionary of input files.',
            dynamic=True, # can take num of values unknown at time of definition
        )


        # set the list of output file names as an input so that it can be
        # iterated over in the parser later.
        spec.input('output_files', valid_type=List, required=False,
                   help='List of output file names.')

        # define the schema for metadata.options
        spec.input('metadata.options.output_filename', valid_type=str,
                default='file.out', help='name of file produced by default.')
        spec.input('metadata.options.output_dir', valid_type=str, 
                default=os.getcwd(),
                help='Directory where output files will be saved '
                    'when parsed.')

        # set the computational resources used for this calculation.
        spec.inputs['metadata']['options']['resources'].default = {
                'num_machines': 1,
                'num_mpiprocs_per_machine': 1,
                }
        # set name of the default parser.
        spec.inputs['metadata']['options']['parser_name'].default = \
                'gromacs.genericMD'
        # spec.input('metadata.options.parser_name',
        #         valid_type=Str, required=False, default=Str('genericMD'),
        #         help='The name of the parser to use.')

        # ensure code is set
        spec.inputs['code'].required = True


        # IMPORTANT:
        # Use spec.outputs.dynamic = True to make the entire output namespace
        # fully dynamic. This means any number of output files
        # can be linked to a node.
        spec.outputs.dynamic = True
        spec.inputs.dynamic = True
        spec.inputs['metadata']['options'].dynamic = True

        # Used by parsers, which communicate errors through exit codes.
        spec.exit_code(300, 'ERROR_MISSING_OUTPUT_FILES',
                message='Calculation did not produce all expected '\
                        'output files.')
        spec.exit_code(301, 'ERROR_UNTRACKED_OUTPUT_FILES',
                message='Specified output file not produced by command.')

    def prepare_for_submission(self, folder):
        """
        Create input files in the format the code external to AiiDA
        expects and return CalcInfo object that contains instructions
        for AiiDA engine on how the code should be run.

        :param folder: an `aiida.common.folders.Folder` where the plugin
            should temporarily place all files needed by the calculation.
        :return: `aiida.common.datastructures.CalcInfo` instance
        """

        # create a CodeInfo object that lets AiiDA know how to run the code
        codeinfo = datastructures.CodeInfo()

        # split strings in command
        codeinfo.cmdline_params = str(self.inputs.command.value).split()
        # if a command uses bash as code, add -c before it to run
        # (allows gmx genion to be run for example)
        if self.inputs.code.label == "bash":
            codeinfo.cmdline_params = ["-c", self.inputs.command.value]
        # If an input redirection is included in the command, then remove
        # this and set the stdin_name as the filename used in the command
        if "<" in self.inputs.command.value:
            stdin_file = self.inputs.command.value.split()[-1]
            codeinfo.stdin_name = stdin_file
            codeinfo.cmdline_params = str(self.inputs.command.value.split("<")[0]).split()
            # codeinfo.cmdline_params = []

        # the UUID of the AbstractCode to run
        codeinfo.code_uuid = self.inputs.code.uuid

        # redirect standard output to the specified output filename.
        codeinfo.stdout_name = self.metadata.options.output_filename

        # create a CalcInfo object that lets AiiDA know which files to
        # copy back and forth.
        calcinfo = datastructures.CalcInfo()
        calcinfo.codes_info = [codeinfo]

        # get a list of input files to be copied to remote.
        copy_list = []
        if "input_files" in self.inputs:
            for _, obj in self.inputs.input_files.items():
                copy_list.append((obj.uuid, obj.filename, obj.filename))

        # input files are already stored in the AiiDA file repository
        # and we can use the local_copy_list to pass them along.
        calcinfo.local_copy_list = copy_list

        # The retrieve_list tells the engine which files to retrieve
        # from the directory where the job ran after it has finished.
        retrieve_list = [self.metadata.options.output_filename]
        if "output_files" in self.inputs:  # check there are output files.
            for name in self.inputs.output_files:
                retrieve_list.append(str(name))  # save output filename to list
        calcinfo.retrieve_list = retrieve_list
        calcinfo.retrieve_temporary_list = retrieve_list

        return calcinfo
