"""
Data types provided by plugin

Register data types via the "aiida.data" entry point in setup.json.
"""

# You can directly use or subclass aiida.orm.data.Data
# or any other data type listed under 'verdi data'
from aiida.orm import Dict
from voluptuous import Optional, Required, Schema

# A subset of make_ndx command line options
cmdline_options = {
    Required("o", default="index.ndx"): str,
    Optional("natoms"): str,
    Optional("notwin"): str,
    Optional("twin"): str,
}


class Make_ndxParameters(Dict):
    """
    Command line options for diff.

    This class represents a python dictionary used to
    pass command line options to the executable.
    """

    # "voluptuous" schema  to add automatic validation
    schema = Schema(cmdline_options)

    def __init__(self, dict=None, **kwargs):
        """
        Constructor for the data class

        Usage: ``Make_ndxParameters(dict{'ignore-case': True})``

        :param parameters_dict: dictionary with commandline parameters
        :param type parameters_dict: dict

        """
        dict = self.validate(dict)
        super().__init__(dict=dict, **kwargs)

    def validate(self, parameters_dict):
        """Validate command line options.

        Uses the voluptuous package for validation. Find out about allowed keys using::

            print(Make_ndxParameters).schema.schema

        :param parameters_dict: dictionary with commandline parameters
        :param type parameters_dict: dict
        :returns: validated dictionary
        """
        return Make_ndxParameters.schema(parameters_dict)

    def cmdline_params(self, input_files):
        """Synthesize command line parameters.

        e.g. [ '--ignore-case', 'filename1', 'filename2']

        :param pdbfile: Name of input pdb file
        :param type pdbfile: str

        """
        parameters = []

        parameters.append("make_ndx")
        if "grofile" in input_files:
            parameters.extend(["-f", input_files["grofile"]])
        if "n_file" in input_files:
            parameters.extend(["-n", input_files["n_file"]])

        parm_dict = self.get_dict()

        for key, value in parm_dict.items():
            parameters.extend(["-" + key, value])

        return [str(p) for p in parameters]

    def __str__(self):
        """String representation of node.

        Append values of dictionary to usual representation. E.g.::

            uuid: b416cbee-24e8-47a8-8c11-6d668770158b (pk: 590)
            {'ignore-case': True}

        """
        string = super().__str__()
        string += "\n" + str(self.get_dict())
        return string
