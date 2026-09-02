"""
Data types provided by plugin

Register data types via the "aiida.data" entry point in setup.json.
"""

# You can directly use or subclass aiida.orm.data.Data
# or any other data type listed under 'verdi data'
from voluptuous import Optional, Required, Schema

from aiida.orm import Dict

# A subset of genion command line options
cmdline_options = {
    Required("o", default="solvated_ions.gro"): str,
    Optional("np"): str,
    Required("pname", default="NA"): str,
    Optional("pq"): str,
    Optional("nn"): str,
    Required("nname", default="CL"): str,
    Optional("nq"): str,
    Optional("rmin"): str,
    Optional("seed"): str,
    Optional("conc"): str,
    Required("neutral", default="true"): str,
}


class GenionParameters(Dict):
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

        Usage: ``GenionParameters(dict{'ignore-case': True})``

        :param parameters_dict: dictionary with commandline parameters
        :param type parameters_dict: dict

        """
        dict = self.validate(dict)
        super().__init__(dict=dict, **kwargs)

    def validate(self, parameters_dict):
        """Validate command line options.

        Uses the voluptuous package for validation. Find out about allowed keys using::

            print(GenionParameters).schema.schema

        :param parameters_dict: dictionary with commandline parameters
        :param type parameters_dict: dict
        :returns: validated dictionary
        """
        return GenionParameters.schema(parameters_dict)

    def cmdline_params(self, input_files):
        """Synthesize command line parameters.

        e.g. [ '--ignore-case', 'filename1', 'filename2']

        :param pdbfile: Name of input pdb file
        :param type pdbfile: str

        """
        parameters = []
        if "instructions_file" in input_files:
            parameters.append("genion")
            parameters.extend(["-s", input_files["tprfile"]])
            parameters.extend(["-p", input_files["topfile"]])
            if "n_file" in input_files: parameters.extend(["-n", input_files["n_file"]])

            parm_dict = self.get_dict()

            for key, value in parm_dict.items():
                parameters.extend(["-" + key, value])

        else:
            # if no instructions given, then default to hard coded genion input
            cmdline = "echo"
            cmdline = cmdline + " " + "SOL"
            cmdline = cmdline + " " + "| gmx genion"
            cmdline = cmdline + " " + " -s " + input_files["tprfile"]
            cmdline = cmdline + " " + " -p " + input_files["topfile"]
            if "n_file" in input_files: cmdline = cmdline + " " + " -n " + input_files["n_file"]

            parm_dict = self.get_dict()

            for key, value in parm_dict.items():
                cmdline = cmdline + " -" + key + " " + value

            parameters.extend(["-c", cmdline])

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
