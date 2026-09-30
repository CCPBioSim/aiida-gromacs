#!/usr/bin/env python
"""
Functions for parsing various gromacs input/output files and extracting
metadata into a dictionary.
"""

import os

from biosim_schema.utils.paths import engine_mappings_path, schema_yaml_path
from biosim_extractor.metadata.populatemetadata import MetadataPopulator


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


def extract_gromacs_files(top_file, traj_file, log_file):
    """Extract metadata from topology, trajectory, and GROMACS log files."""

    mapping_path = engine_mappings_path()
    biosim_path = schema_yaml_path()

    populator = MetadataPopulator(
        schema_path=mapping_path,
        top_file=top_file,
        traj_file=[traj_file],
        log_file=log_file,
        engine="gromacs",
        store_file_metadata=True,
    )

    result = populator.populate()
    populator.validate(result, biosimschema_path=biosim_path)

    return result
