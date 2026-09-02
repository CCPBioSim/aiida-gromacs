"""Sub class of `Data` to handle inputs used and outputs that will be produced
from commands in the plumed input file.
"""

import os
import re
import sys

from aiida.orm import FolderData, List, SinglefileData

from aiida_gromacs.utils import inputFile_utils

INPUT_KEYWORDS = {
    "READ_DISSIMILARITY_MATRIX": ["FILE"],
    "EXTERNAL": ["FILE"],
    "METAD": ["GRID_RFILE", "ACCELERATION_RFILE"],
    "PBMETAD": ["GRID_WFILES"],
}

OUTPUT_KEYWORDS = {
    "COMMITTOR": ["FILE"],
    "DUMPATOMS": ["FILE"],
    "DUMPCUBE": ["FILE"],
    "DUMPDERIVATIVES": ["FILE"],
    "DUMPFORCES": ["FILE"],
    "DUMPGRID": ["FILE"],
    "DUMPMASSCHARGE": ["FILE"],
    "DUMPMULTICOLVAR": ["FILE"],
    "DUMPPROJECTIONS": ["FILE"],
    "PRINT": ["FILE"],
    "GRID_TO_XYZ": ["FILE"],  # default=density
    "FIND_CONTOUR": ["FILE"],
    "PRINT_DISSIMILARITY_MATRIX": ["FILE"],
    "OUTPUT_PCA_PROJECTION": ["FILE"],
    "OUTPUT_ANALYSIS_DATA_TO_COLVAR": ["FILE"],
    "OUTPUT_ANALYSIS_DATA_TO_PDB": ["FILE"],
    "MAXENT": ["FILE"],  # default=label name followed by the string .LAGMULT
    "METAD": ["FILE", "GRID_WFILE"],
    "PBMETAD": ["FILE", "GRID_WFILES"],
}


class PlumedInputData(SinglefileData):
    """Class to find the inputs used and outputs produced from
    the commands in the plumed input file"""

    def set_file(self, file, filename=None, **kwargs):
        """Add a file to the node, parse it and set the attributes found.

        :param file: absolute path to the file or a filelike object
        :param filename: specify filename to use (defaults to name of provided file).
        """
        super().set_file(file, filename, **kwargs)

        # Parse the plumed file
        parsed_info = parse_plumed_input_file(self.get_content().splitlines())

        # Add all other attributes found in the parsed dictionary
        for key, value in parsed_info.items():
            self.base.attributes.set(key, value)

    @property
    def inpfile_list(self):
        """Return the list input files used in the plumed script"""
        return self.base.attributes.get("input_files")

    @property
    def outfile_list(self):
        """Return the list output files to be produced from the plumed script"""
        return self.base.attributes.get("output_files")

    @property
    def calculation_inputs_outputs(self):
        """Return the inputs for the plumed calculation job"""
        input_files = self.inpfile_list
        subdirs, files = inputFile_utils.check_filepath(input_files)
        calc_inputs = add_calculation_inputs(subdirs, files)
        output_files = self.outfile_list
        calc_outputs = add_calculation_outputs(output_files)
        return calc_inputs, calc_outputs


def find_filename_from_string(head, values, filenames):
    """
    Find any filenames that are in a line of the plumed input file. Some keyword
    arguments allow for multiple filenames, which are comma separated.
    Each argument has an '=' after it.

    :param head: line of plumed input file that doesn't start with '#'
    :param values: list of arguments for a plumed keyword that would produce a file
    :param filenames: list of input/output filenames to append to, that are found in the plumed input
    :returns: list of filenames found in parsed plumed input file
    :rtype: list
    """
    split_line = head.split("=")
    if len(split_line) > 0:
        for s, split in enumerate(split_line):
            for value in values:
                filename = None
                if re.search(value, split, re.IGNORECASE):
                    filename = split_line[s + 1]
                if filename:
                    # consider all ways spaces could be in comma separation
                    # between filenames
                    if "," in filename:
                        split_filenames = filename.split(",")
                        for split_filename in split_filenames:
                            if " " not in split_filename:
                                filenames.append(split_filename)
                            else:
                                # split the string to remove any whitespaces
                                # and save string only, ignore any strings that
                                # are not separated by a comma
                                split_f = split_filename.split()
                                filenames.append(split_f[0])
                    else:
                        # if no comma, then only one file to find
                        split_filename = filename.split()
                        filenames.append(split_filename[0])

    return filenames


def find_plumed_filenames(keywords, i, line, lines):
    """
    Find lines that contain a plumed keyword that would require an input/output
    file

    :param keywords: dictionary of plumed keywords and their arguments that require
        an input/output file
    :param i: the parsed line number
    :param line: the currently parsed line
    :param lines: all the lines in the plumed input file
    :returns: list of filenames found in parsed plumed input file
    :rtype: list
    """
    filenames = []
    # only find lines that don't start with '#'
    head, sep, tail = line.partition("#")
    if len(head.split()) > 0:
        for keyword, values in keywords.items():
            # find the keyword in the first word in the line
            if re.search(keyword, head.split()[0], re.IGNORECASE):
                if "..." in head:
                    # parse lines after '...' where variables are defined
                    for line2 in lines[i + 1 :]:
                        head2, sep2, tail2 = line2.partition("#")
                        if "..." not in line2:
                            find_filename_from_string(head2, values, filenames)
                        else:
                            break
                else:
                    # find filename in the same line as the where the keyword was found
                    find_filename_from_string(head, values, filenames)
            else:
                continue

    return filenames


def parse_plumed_input_file(lines):
    """Parse plumed input file and find any instances of reading input files
    and writing output files. Find the lines that contain the keyword and
    then find the FILE keyword in the subsequent lines, onces this is found,
    then stop and carry on with outer loop. If the FILE keyword does not exist,
    there may be a default filename for some keywords.

    :param lines: parsed lines from the plumed input file
    """

    input_files = []
    output_files = []
    # iterate through plumed lines and find input and output files
    for i, line in enumerate(lines):
        input_files += find_plumed_filenames(INPUT_KEYWORDS, i, line, lines)
        output_files += find_plumed_filenames(OUTPUT_KEYWORDS, i, line, lines)

    parsed_info = {}
    parsed_info["input_files"] = input_files
    parsed_info["output_files"] = output_files

    return parsed_info


def add_calculation_inputs(subdirs, files):
    """If they exist, add input files for plumed and dirs into the calcjob
    inputs directory

    :param subdirs: list of subdirectories that contain input files
    :param files: list of input files
    """
    calc_inputs = {}
    input_list = []
    # If we have plumed input files then tag them.
    if files:
        calc_inputs["plumed_inpfiles"] = {}
        # Iterate files to assemble a dict of names and paths.
        for file in files:
            formatted_filename = inputFile_utils.format_link_label(file)
            if os.path.isfile(file):
                input_list.append(file)
                calc_inputs["plumed_inpfiles"][formatted_filename] = SinglefileData(
                    file=os.path.join(os.getcwd(), file)
                )

            elif "PYTEST_CURRENT_TEST" in os.environ:
                test_path = os.path.join(os.getcwd(), "tests/input_files", file)
                if os.path.isfile(test_path):
                    calc_inputs["plumed_inpfiles"][formatted_filename] = SinglefileData(file=test_path)
                else:
                    sys.exit(f"Error: Input file {file} referenced in plumed file does not exist")

            else:
                sys.exit(f"Error: Input file {file} referenced in plumed file does not exist")

    # If we have included files in subdirs then process these.

    if subdirs:
        calc_inputs["plumed_dirs"] = {}
        # for each entry establish dir path and build file tree.
        for subdir in subdirs:
            if os.path.isfile(subdir):
                # add file to input list
                input_list.append(subdir.split("/")[-1])
                frst_dir = subdir.split("/")[0]
                # Create a folder that is empty.
                if frst_dir not in calc_inputs["plumed_dirs"].keys():
                    calc_inputs["plumed_dirs"][frst_dir] = FolderData()
                # Now fill it with files referenced in the plumed inputfile.
                # need to make sure to include any nested dirs in the path
                calc_inputs["plumed_dirs"][frst_dir].put_object_from_file(
                    os.path.join(os.getcwd(), subdir),
                    path="/".join(subdir.split("/")[1:]),  # remove the first dir
                )

            # For tests
            elif "PYTEST_CURRENT_TEST" in os.environ:
                if os.path.isfile(os.path.join(os.getcwd(), "tests", subdir)):
                    # Create a folder that is empty.
                    if "tests" not in calc_inputs["plumed_dirs"].keys():
                        calc_inputs["plumed_dirs"]["tests"] = FolderData()
                    # Now fill it with files referenced in the plumed inputfile.
                    calc_inputs["plumed_dirs"]["tests"].put_object_from_file(
                        os.path.join(os.getcwd(), "tests", subdir), path=subdir
                    )

            else:
                sys.exit(f"Error: subdir {subdir} referenced in plumed file does not exist")

    # NOTE: this list is not used at the moment, might use for searchprevious
    # calc_inputs["input_list"] = List(input_list)

    return calc_inputs


def add_calculation_outputs(files):
    """Add outputs from plumed script

    :param files: list of output files
    """
    calc_outputs = {}
    # If we have plumed output files then tag them.
    if files:
        output_list = []
        # Iterate files to assemble a dict of names and paths.
        for file in files:
            if "/" in file:
                file = file.split("/")[-1]
            output_list.append(file)
        calc_outputs["plumed_outfiles"] = List(output_list)
    return calc_outputs


def populate_plumed_files_to_inputs(inputs, plumed_filename):
    """Populate the plumed input files and directories into the inputs

    :param inputs: dictionary of inputs for the calculation
    :param plumed_filename: name of the plumed input file
    """
    # Prepare input parameters in AiiDA formats.
    # Set the plumed script as a PlumedInputData type node
    inputs["plumed_file"] = PlumedInputData(file=os.path.join(os.getcwd(), plumed_filename))
    # Find the inputs and outputs referenced in the plumed script
    calc_inputs, calc_outputs = inputs["plumed_file"].calculation_inputs_outputs
    # add input files and dirs referenced in plumed file into inputs
    inputs.update(calc_inputs)
    inputs.update(calc_outputs)
    return inputs
