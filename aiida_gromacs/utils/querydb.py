#!/usr/bin/env python
"""
Sandbox for querying AiiDA databases.
"""

import subprocess

from aiida import load_profile
from aiida.orm.querybuilder import QueryBuilder
from aiida.plugins import CalculationFactory

profile = load_profile()

output_file = "test.aiida"

# Run the `verdi export` command using subprocess
subprocess.run(["verdi", "archive", "create", "--all", output_file])


MyAppCalculation = CalculationFactory("gromacs.genericMD")

qb = QueryBuilder()
qb.append(MyAppCalculation)  # , tag="calcjob")
first_row = qb.first()
all_results_d = qb.dict()
print(all_results_d)

node_uuids = [node[0].uuid for node in qb.all()]
print(node_uuids)

first_row[0].get_incoming()


# archive = Archive()
# archive.add_nodes(node_uuids)
# archive.archive('aiida-data.zip')
