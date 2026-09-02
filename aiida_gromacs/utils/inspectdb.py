#!/usr/bin/env python
"""
Sandbox for inspecting AiiDA databases.
"""

from aiida import manage, orm, profile_context
from aiida.orm import List, Str
from aiida.storage.sqlite_zip.backend import SqliteZipBackend
from aiida.tools.visualization import Graph

# print(help(aiida.storage.sqlite_zip))
# sys.exit()
#  create a profile instance from the archive path
archive_profile = SqliteZipBackend.create_profile("archive.aiida")
# print(archive_profile)

# can load our archive as a profile
# with profile_context(archive_profile):
#     print(manage.get_manager().get_profile())

# directly access the storage backend, and view information about it
# equivalent to: !verdi archive info test.aiida

with profile_context(archive_profile):
    storage = manage.get_manager().get_profile_storage()
    # print(storage)
    # print(json.dumps(storage.get_info(), indent=2))

# once the context manager is exited, the storage is closed,
# and will except on further calls
# print(storage)

# As per a standard profile, we can now use the QueryBuilder,
# to find and query for data
with profile_context(archive_profile):
    process = orm.QueryBuilder().append(orm.ProcessNode).first(flat=True)
    # print(process)

with profile_context(archive_profile):
    processes = orm.QueryBuilder().append(orm.ProcessNode).all(flat=True)
    graph = Graph(graph_attr={"size": "8!,8!", "rankdir": "TB"})
    for process in processes:
        print(f"process node: {process}")
        graph.add_incoming(process, annotate_links="both")
        graph.add_outgoing(process, annotate_links="both")
        # node = load_node(process.uuid)
        # filename = node.filename
        # print(node)
        print("Attributes:")
        for key, value in process.attributes.items():
            print(f"\t{key}: {value}")
        print("Extras:")
        for key, value in process.extras.items():
            print(f"\t{key}: {value}")
        last_job_info = process.get_last_job_info()
        print("Last Job Information:")
        print(last_job_info)
        # for key, value in last_job_info.items():
        #     print(f"\t{key}: {value}")
        print("incoming nodes")
        input_nodes = process.get_incoming().all_nodes()
        for input_node in input_nodes:
            print(f"\tinput: {input_node, input_node.node_type}")
            print()
            if isinstance(input_node, List):
                print(input_node.get_list())
            if isinstance(input_node, Str):
                print(input_node.value)
        print("outgoing nodes")
        output_nodes = process.get_outgoing().all_nodes()
        for output_node in output_nodes:
            print(f"\toutput: {output_node, output_node.node_type}")
            print()
            if output_node in [orm.List, orm.Str]:
                print(output_node.value)


# print(graph)
# #graph.graphviz
# # print(help(graph.graphviz))
# graph.graphviz.render('graph', format='pdf')


# Query DB example below, not used.

# from aiida.orm.querybuilder import QueryBuilder
# from aiida.plugins import CalculationFactory

# MyAppCalculation = CalculationFactory("gromacs.genericMD")

# qb = QueryBuilder()
# qb.append(MyAppCalculation) #, tag="calcjob")
# first_row = qb.first()
# all_results_d = qb.dict()
# print(all_results_d)

# node_uuids = [node[0].uuid for node in qb.all()]
# print(node_uuids)

# first_row[0].get_incoming()
