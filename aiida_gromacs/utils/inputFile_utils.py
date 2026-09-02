"""Methods for dealing with various types of files and
directories that are used in processes and add them to aiida nodes"""

import os
import re

from aiida.orm import FolderData


def format_link_label(filename: str) -> str:
    """
    Modified from: https://github.com/sphuber/aiida-shell/blob/main/src/aiida_shell/parsers/shell.py
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


def check_filepath(input_files: list):
    """Check if an input is a file or a path.

    :param input_files: The list of inputs to check
    :returns: List of files and list of subdirs
    """
    subdirs = []
    files = []
    # Iterate all found files and check if they are in subdirs.
    for i in input_files:
        # paths containing dirs will have slashes in them,
        # otherwise they will be files
        if "/" in i:
            subdirs.append(i)
        else:
            files.append(i)
    return subdirs, files


def add_subdir_to_node(dict_info, subdir):
    """Add a subdir to a node."""
    # Create a folder that is empty.
    if subdir.split("/")[0] not in dict_info.keys():
        dict_info[subdir.split("/")[0]] = FolderData()
    # Now fill it with subdir and file.
    dict_info[subdir.split("/")[0]].put_object_from_file(os.path.join(os.getcwd(), subdir), path=subdir.split("/")[-1])
    return dict_info
