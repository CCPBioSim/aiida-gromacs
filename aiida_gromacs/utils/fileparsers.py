#!/usr/bin/env python
"""
Functions for parsing various gromacs input/output files and extracting
metadata into a dictionary.
"""

import os
import re


def parse_process_files(self, files_retrieved, output_dir):
    """
    Parse the retrieved files from an aiida process and save them in the
    directory from which the process command was run

    :param self: parser instance
    :param files_retrieved: list of files retrieved from process
    :param output_dir: path of directory where parsed files shoud be saved
    """
    # parse retrieved files and write them to where command was run
    for thing in files_retrieved:
        self.logger.info(f"Parsing '{thing}'")
        file_path = os.path.join(output_dir, thing)
        try:
            with self.retrieved.open(thing, "rb") as handle:
                with open(file_path, "wb") as f_out:
                    while True:
                        chunk = handle.read(1024)
                        if not chunk:
                            break
                        f_out.write(chunk)

        except UnicodeDecodeError:
            with self.retrieved.open(thing, "r") as handle:
                with open(file_path, "w", encoding="utf-8") as f_out:
                    for line in handle.read():
                        f_out.write(line)


def extract_nested_dict(i, j, lines, input_dict, split_with, leading_space, leading_space_check_list):
    """
    For each of the input parameers defined in the gromacs log file, output
    each indented section into dictionary format.

    :param i: line number in file
    :param j: line number from line i in file
    :param lines: lines in file
    :param input_dict: dictionary for storing parsed data
    :param split_with: the delimiter used to split contents in a file
    :param leading_space: the number of spaces at the start of a line
    :param leading_space_check_list: list of acceptable number of starting spaces in a line
    """
    for _, line3 in enumerate(lines[i + j + 1 :]):
        if line3 == "\n":
            break
        leading_space_check = re.search(r"\S", line3).start()
        if ":" in line3 and leading_space_check in leading_space_check_list:
            break
        if split_with in line3:
            stripped_line = line3.strip().split(split_with)
            if leading_space_check > leading_space:
                input_dict[stripped_line[0].strip()] = stripped_line[1].strip()
    return input_dict


def parse_gromacs_logfile(self, f):
    """
    Parse a logfile outputted from the gromacs mdrun command and save data
    into a dictionary

    :param f: name of file in output node
    :return: dictionary of logfile metadata
    """
    input_params = {}
    averages = {}
    with self.retrieved.base.repository.open(f, "r") as handle:
        lines = handle.readlines()
        for i, line in enumerate(lines):
            # find line containing executable and save subsequent lines with
            # zero leading spaces
            if re.match(r"(?i)Executable:", line):
                for _, line2 in enumerate(lines[i:]):
                    if line2 == "\n":
                        break
                    leading_space = re.search(r"\S", line2).start()
                    if ":" in line2 and leading_space == 0:
                        top = line2.strip().split(":")[0].strip()
                        val = line2.strip().split(":")[1].strip()
                        input_params[top] = val
            # find line containing command, assumes the command is on next line
            if "Command line:" in line:
                if i + 1 < len(lines):
                    command = lines[i + 1].strip()
                    input_params["Command line"] = rf"{command}"
            # save subsequent lines with zero leading spaces
            if re.match(r"(?i)GROMACS version:", line):
                for _, line2 in enumerate(lines[i:]):
                    if line2 == "\n":
                        break
                    leading_space = re.search(r"\S", line2).start()
                    if ":" in line2 and leading_space == 0:
                        top = line2.strip().split(":")[0].strip()
                        val = line2.strip().split(":")[1].strip()
                        input_params[top] = val
            # extract compute from line containing "Running"
            if re.match(r"(?i)Running", line):
                compute_info = line.split()
                top = " ".join(compute_info[:2])
                input_params[top] = {}
                input_params[top][compute_info[3]] = compute_info[2]  # nodes
                input_params[top][compute_info[7][:-1]] = compute_info[6]  # cores
                input_params[top][" ".join(compute_info[-2:])] = compute_info[8]  # PUs
            # Extract Hardware info, delimiters are not like input params
            if re.match(r"(?i)Hardware detected:", line):
                for _, line2 in enumerate(lines[i:]):
                    if line2 == "\n":
                        break
                    leading_space = re.search(r"\S", line2).start()
                    if ":" in line2 and leading_space == 0:
                        top = line2.strip().split(":")[0]
                        input_params[top] = {}
                    if ":" in line2 and leading_space == 2:
                        top2 = line2.strip().split(r":")[0]
                        # top2_val = line2.strip().split(r":")[1]
                        input_params[top][top2] = {}
                    if ":" in line2 and leading_space == 4:
                        top3 = line2.strip()
                        top3 = re.split(r"\s{3}", top3)
                        for pair in top3:
                            key_val = pair.split(r":")
                            key = key_val[0].strip()
                            val = key_val[1].strip()
                            if len(key_val) == 2:
                                if val != "":
                                    input_params[top][top2][key] = val
                                else:
                                    input_params[top][top2][key] = {}
                    if ":" in line2 and leading_space == 6:
                        key_val2 = line2.split(r":")
                        key2 = key_val2[0].strip()
                        val2 = key_val2[1].strip()
                        input_params[top][top2][key][key2] = val2
            # extract input params
            if re.match(r"(?i)Input\sParameters", line):
                for j, line2 in enumerate(lines[i:]):
                    if line2 == "\n":
                        break
                    leading_space = re.search(r"\S", line2).start()
                    if ":" in line2 and leading_space == 0:
                        top = line2.strip().split(":")[0]
                        input_params[top] = {}
                        extract_nested_dict(i, j, lines, input_params[top], "=", leading_space, [0, 3])
                    if ":" in line2 and leading_space == 3:
                        top2 = line2.strip().split(":")[0]
                        input_params[top][top2] = {}
                        extract_nested_dict(i, j, lines, input_params[top][top2], "=", leading_space, [3, 5])
                    if ":" in line2 and leading_space == 5:
                        top3 = line2.strip().split(":")[0]
                        input_params[top][top2][top3] = {}
                        extract_nested_dict(i, j, lines, input_params[top][top2][top3], "=", leading_space, [5, 7])
                    if ":" in line2 and leading_space == 7:
                        top4 = line2.strip().split(":")[0]
                        input_params[top][top2][top3][top4] = {}
                        extract_nested_dict(i, j, lines, input_params[top][top2][top3][top4], "=", leading_space, [7])
            # extract ensemble averages
            if "A V E R A G E S" in line:
                for j, line2 in enumerate(lines[i:]):
                    if "Statistics" in line2:
                        stripped_line = line2.strip().split()
                        averages["total-steps"] = stripped_line[2]
                        averages["total-frames"] = stripped_line[5]
                    if "M E G A - F L O P S" in line2:
                        break
                    numbers = re.findall(r"\d+\.\d+e[\+|-]\d+", line2, re.DOTALL)
                    if len(numbers) != 0:
                        possible_header = lines[i + j - 1].strip()  # remove \n
                        if re.match(r"[a-z,A-Z]", possible_header):
                            header = re.split(r"\s{2}+", possible_header)
                            header = list(filter(None, header))  # remove "" entries
                            if len(numbers) == len(header):
                                for hn in range(len(header)):
                                    averages[header[hn].strip()] = numbers[hn]
            if "Time:" in line:
                averages["Time"] = {}
                stripped_line = line.strip().split()[1:]
                head = list(filter(None, lines[i - 1].strip().split("  ")))
                for hn in range(len(head)):
                    averages["Time"][head[hn]] = stripped_line[hn]
            if "Performance:" in line:
                averages["Performance"] = {}
                stripped_line = line.strip().split()[1:]
                # head = list(filter(None, lines[i-1].strip().split("  ")))
                head = list(filter(None, re.split(r"\s{2,}", lines[i - 1].strip())))
                for hn in range(len(head)):
                    averages["Performance"][head[hn]] = stripped_line[hn]

    averages = {"Summary": averages}
    # merge dicts
    all_dict = input_params | averages
    return all_dict
