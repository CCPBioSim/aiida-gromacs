"""
Data types provided by plugin

Register data types via the "aiida.data" entry point in setup.json.
"""

# You can directly use or subclass aiida.orm.data.Data
# or any other data type listed under 'verdi data'
from voluptuous import Optional, Required, Schema

from aiida.orm import Dict

# A subset of editconf command line options
cmdline_options = {
    Required("o", default="newbox.gro"): str,
    Optional("mead"): str,
    Optional("w"): str,
    Optional("ndef"): str,
    Optional("bt"): str,
    Optional("box"): str,
    Optional("angle"): str,
    Optional("d"): str,
    Optional("c"): str,
    Optional("center", default="0 0 0"): str,
    Optional("aligncenter"): str,
    Optional("align"): str,
    Optional("translate"): str,
    Optional("rotate"): str,
    Optional("princ"): str,
    Optional("scale"): str,
    Optional("density"): str,
    Optional("pbc"): str,
    Optional("resnr"): str,
    Optional("grasp"): str,
    Optional("rvdw"): str,
    Optional("sig56"): str,
    Optional("vdwread"): str,
    Optional("atom"): str,
    Optional("legend"): str,
    Optional("label"): str,
    Optional("conect"): str,
}


class EditconfParameters(Dict):
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

        Usage: ``EditconfParameters(dict{'ignore-case': True})``

        :param parameters_dict: dictionary with commandline parameters
        :param type parameters_dict: dict

        """
        dict = self.validate(dict)
        super().__init__(dict=dict, **kwargs)

    def validate(self, parameters_dict):
        """Validate command line options.

        Uses the voluptuous package for validation. Find out about allowed keys using::

            print(EditconfParameters).schema.schema

        :param parameters_dict: dictionary with commandline parameters
        :param type parameters_dict: dict
        :returns: validated dictionary
        """
        return EditconfParameters.schema(parameters_dict)

    def cmdline_params(self, input_files):
        """Synthesize command line parameters.

        e.g. [ '--ignore-case', 'filename1', 'filename2']

        :param grofile: Name of input gro file
        :param type grofile: str

        """
        parameters = []

        parameters.append("editconf")
        parameters.extend(["-f", input_files["grofile"]])
        if "n_file" in input_files: parameters.extend(["-n", input_files["n_file"]])
        if "bf_file" in input_files: parameters.extend(["-bf", input_files["bf_file"]])

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
