#!/usr/bin/env python
"""
Display provenance of processes run on current loaded profile
"""

from aiida import load_profile, orm


def show_provenance_text():
    """For a given loaded aiida profile, view the provenance graph on the
    CLI as plain text
    """
    load_profile()
    qb = orm.QueryBuilder()
    # get all processes and order from oldest to newest
    qb.append(orm.ProcessNode, tag="process")
    qb.order_by({orm.ProcessNode: {"ctime": "asc"}})

    output_pks = {}
    for i, entry in enumerate(qb.all(flat=True)):
        # print(list(entry.inputs))
        # print(list(entry.outputs))
        # print(dir(entry))
        # print(entry.label)
        command = ""
        executable = ""
        for link_triple in entry.get_incoming().all():
            # print("A", link_triple.node)
            # print("B", link_triple.link_type)
            # print("C", link_triple.link_label)
            # print("D", type(link_triple.node))
            if link_triple.link_label == "command":
                command = link_triple.node.value

        incoming = entry.get_incoming().all_nodes()
        outgoing = entry.get_outgoing().all_nodes()
        input_files = []
        output_files = []
        for inputs in incoming:
            if isinstance(inputs, orm.InstalledCode):
                executable = inputs.label
            if isinstance(inputs, orm.SinglefileData):
                # file = open_file(inputs)
                input_str = inputs.filename
                if inputs.pk in output_pks:
                    input_str = f"{inputs.filename} <-- from Step {output_pks[inputs.pk]}."
                input_files.append(input_str)
        for outputs in outgoing:
            if outputs.pk not in output_pks:
                output_pks[outputs.pk] = i + 1
            if isinstance(outputs, orm.SinglefileData):
                output_files.append(outputs.filename)

        inputs_str = "\n\t\t".join(input_files)
        outputs_str = "\n\t\t".join(output_files)
        output = (
            f"\nStep {i + 1}."
            f"\n\tcommand: {command}"
            f"\n\texecutable: {executable}"
            f"\n\tinput files: \n\t\t{inputs_str}"
            f"\n\toutput files: \n\t\t{outputs_str}"
        )
        print(output)


def open_file(file):
    """ """
    lines = None
    try:
        with file.open(mode="r") as handle:
            lines = handle.readlines()
    except UnicodeDecodeError:
        pass
    return lines
