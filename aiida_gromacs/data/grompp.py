"""
Data types provided by plugin

Register data types via the "aiida.data" entry point in setup.json.
"""

# You can directly use or subclass aiida.orm.data.Data
# or any other data type listed under 'verdi data'
from aiida.orm import Dict
from voluptuous import Optional, Required, Schema

# A subset of grompp command line options
cmdline_options = {
    Required("o", default="ions.tpr"): str,
    Optional("po"): str,
    Optional("pp"): str,
    Optional("imd"): str,
    Optional("r"): str,
    Optional("v"): str,
    Optional("time"): str,
    Optional("rmvsbds"): str,
    Optional("maxwarn"): str,
    Optional("zero"): str,
    Optional("renum"): str,
}


class GromppParameters(Dict):
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

        Usage: ``GromppParameters(dict{'ignore-case': True})``

        :param parameters_dict: dictionary with commandline parameters
        :param type parameters_dict: dict

        """
        dict = self.validate(dict)
        super().__init__(dict=dict, **kwargs)

    def validate(self, parameters_dict):
        """Validate command line options.

        Uses the voluptuous package for validation. Find out about allowed keys using::

            print(GromppParameters).schema.schema

        :param parameters_dict: dictionary with commandline parameters
        :param type parameters_dict: dict
        :returns: validated dictionary
        """
        return GromppParameters.schema(parameters_dict)

    def cmdline_params(self, input_files):
        """Synthesize command line parameters.

        e.g. [ '--ignore-case', 'filename1', 'filename2']

        :param pdbfile: Name of input pdb file
        :param type pdbfile: str

        """
        parameters = []

        parameters.append("grompp")
        parameters.extend(["-f", input_files["mdpfile"]])
        parameters.extend(["-c", input_files["grofile"]])
        parameters.extend(["-p", input_files["topfile"]])
        if "r_file" in input_files:
            parameters.extend(["-r", input_files["r_file"]])
        if "rb_file" in input_files:
            parameters.extend(["-rb", input_files["rb_file"]])
        if "n_file" in input_files:
            parameters.extend(["-n", input_files["n_file"]])
        if "t_file" in input_files:
            parameters.extend(["-t", input_files["t_file"]])
        if "e_file" in input_files:
            parameters.extend(["-e", input_files["e_file"]])
        if "qmi_file" in input_files:
            parameters.extend(["-qmi", input_files["qmi_file"]])
        if "ref_file" in input_files:
            parameters.extend(["-ref", input_files["ref_file"]])

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
