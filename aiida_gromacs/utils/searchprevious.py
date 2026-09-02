"""Various functions for searching through previous AiiDA processes
and appending nodes from previous processes to current process nodes.
"""

import os
import re
import sys
import time

from aiida import orm
from aiida.orm.nodes.process.process import ProcessState


def format_link_label(filename: str) -> str:
    """
    From https://github.com/sphuber/aiida-shell/blob/master/src/aiida_shell/parsers/shell.py
    Format the link label from a given filename.
    Valid link labels can only contain alphanumeric characters and
    underscores, without consecutive underscores. So all characters
    that are not alphanumeric or an underscore are converted to
    underscores, where consecutive underscores are merged into one.

    :param filename: The filename to convert to a label.
    :returns: The link label used in AiiDA provenance graphs.
    """
    alphanumeric = re.sub("[^0-9a-zA-Z_]+", "_", filename)
    link_label = re.sub("_[_]+", "_", alphanumeric)

    return link_label


def strip_path(input: str) -> str:
    """For a given input, strip the path from the filename

    :param input: path+filename of an input used for an aiida-gromacs input
    """
    return input.split("/")[-1]


def build_query():
    """
    Uses AiiDA querybuilder to find previously run processes and order from
    newest to oldest

    :returns: the query entries
    :rtype: :py:class:`aiida.orm.querybuilder.QueryBuilder`
    """
    qb = orm.QueryBuilder()
    qb.append(orm.ProcessNode, tag="process")
    qb.order_by({orm.ProcessNode: {"ctime": "desc"}})
    return qb


def check_prev_process(qb):
    """Wait for a previous process to finish if it is still running. The
    process state is checked every 10 seconds for up to 5 minutes and stops
    when the process state is set to finished. If a previous processes takes
    longer than 5 minutes, the latest submitted process is exited.

    :param qb: The queries of previous processes in the AiiDA database
    :type qb: :py:class:`aiida.orm.querybuilder.QueryBuilder`
    """
    if qb.count() > 0:
        # Get the most recently process that was already submitted to the
        # daemon and check if it has finished, wait 10s if not.
        prev_calc = qb.first()[0]
        if prev_calc.process_state != ProcessState.EXCEPTED:
            timeout = time.time() + 60 * 5  # 5 minutes from now
            while prev_calc.process_state != ProcessState.FINISHED:
                print(f"Previous process status: {prev_calc.process_state}")
                print("Waiting for previous process to finish...")
                time.sleep(10)
                if time.time() > timeout:
                    sys.exit("Wait time exceeded for previous process to complete")
        else:
            sys.exit("Previous process did not complete successfully, please check")


def find_previous_file_nodes(qb):
    """
    For any previous processes, store nodes that are files into a list

    :param qb: The queries of previous processes in the AiiDA database
    :type qb: :py:class:`aiida.orm.querybuilder.QueryBuilder`
    """
    file_nodes = []
    if qb.count() > 0:
        for entry in qb.all():
            # A previous calculation exists - use its output as input for the
            # current calculation.
            previous_calculation = entry[0]
            for label in previous_calculation.outputs:
                # Get the outputs from a previous process.
                previous_output_node = previous_calculation.outputs[f"{label}"]
                # check if the output node is a file.
                if isinstance(previous_output_node, orm.SinglefileData):
                    file_nodes.append(previous_output_node)
    return file_nodes


def append_prev_nodes(qb, inputs, process_inputs, INPUT_DIR):
    """Checks if previous processes exists for genericMD calcs and links the
    most recent SinglefileData type output nodes from previous processs as
    inputs to the new process if the file names match.

    :param qb: The query entries of previous processes in the AiiDA database
    :type qb: :py:class:`aiida.orm.querybuilder.QueryBuilder`
    :param inputs: Input files for the command to be run via AiiDA
    :type inputs: list
    :param process_inputs: All inputs for the current process to be submitted
    :type process_inputs: dict
    :param INPUT_DIR: base directory where outputted files are stored.
    :returns: Updated inputs for the current process
    :rtype: dict
    """
    file_nodes = find_previous_file_nodes(qb)
    if file_nodes:
        stripped_inputs = []
        prev_files = []  # list of previous files already saved.
        prev = {}  # dict for genericMD inputs
        for inp in inputs:  # strip input file names of any paths.
            stripped_inputs.append(strip_path(inp))
        for prev_file_node in file_nodes:
            prev_output_filename = prev_file_node.base.attributes.get("filename")  # get filename of the node
            # check if output file is an input for new process and
            # hasn't already been included as an input.
            if prev_output_filename in stripped_inputs and prev_output_filename not in prev_files:
                prev_files.append(prev_output_filename)
                prev[format_link_label(prev_output_filename)] = prev_file_node

        # save input files not found in previous nodes too.
        for filename in list(inputs):
            stripped_input = strip_path(filename)
            if stripped_input not in prev_files:
                prev[format_link_label(stripped_input)] = orm.SinglefileData(file=os.path.join(INPUT_DIR, filename))

        # update the calculation inputs dict with new dictionary of
        # input files including nodes from previous processes.
        process_inputs["input_files"] = prev
    return process_inputs


def link_previous_file_nodes(input_file_labels: dict, inputs: dict):
    """
    For an incoming process, check if an input file is an output of a previous
    process. If this is the case, then rename the node with the new label

    :param input_file_labels: dictionary with keys of filenames and values the
        label for the node
    :param inputs: dictionary used for all inputs for
    """
    qb = build_query()
    # if previous processes exist then check if input files are stored as
    # previous nodes and use these nodes as inputs for new process.
    file_nodes = find_previous_file_nodes(qb)
    prev_files = []  # list of previous files already saved.
    if file_nodes:
        for prev_file_node in file_nodes:
            prev_output_filename = prev_file_node.base.attributes.get("filename")  # get filename of the node
            # save previous file nodes if the filenames match with current process
            # input files
            if prev_output_filename in input_file_labels.keys() and prev_output_filename not in prev_files:
                prev_files.append(prev_output_filename)
                label = input_file_labels[prev_output_filename]
                inputs[label] = prev_file_node
    return inputs


def save_command(executable: str, params: dict, inputs: dict):
    """
    For a given cli command run via aiida-gromacs, save this as a string
    and use this as an attribute for the given process
    """

    # save the full command as a string in the inputs dict
    str_params = ""
    for k, v in params.items():
        v_stripped = strip_path(v)
        str_params += f"-{k} {v_stripped} "
    command = f"{executable} {str_params}"
    inputs["command"] = orm.Str(command)
    return inputs
