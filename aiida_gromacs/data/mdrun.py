"""
Data types provided by plugin

Register data types via the "aiida.data" entry point in setup.json.
"""

# You can directly use or subclass aiida.orm.data.Data
# or any other data type listed under 'verdi data'
from aiida.orm import Dict
from voluptuous import Optional, Required, Schema

# A subset of mdrun command line options
cmdline_options = {
    Required("c", default="confout.gro"): str,
    Required("e", default="energy.edr"): str,
    Required("g", default="md.log"): str,
    Required("o", default="trajectory.trr"): str,
    Optional("x"): str,
    Optional("cpo"): str,
    Optional("dhdl"): str,
    Optional("field"): str,
    Optional("tpi"): str,
    Optional("tpid"): str,
    Optional("eo"): str,
    Optional("px"): str,
    Optional("pf"): str,
    Optional("ro"): str,
    Optional("ra"): str,
    Optional("rs"): str,
    Optional("rt"): str,
    Optional("mtx"): str,
    Optional("if"): str,
    Optional("swap"): str,
    Optional("xvg"): str,
    Optional("dd"): str,
    Optional("ddorder"): str,
    Optional("npme"): str,
    Optional("nt"): str,
    Optional("ntmpi"): str,
    Optional("ntomp"): str,
    Optional("ntomp_pme"): str,
    Optional("pin"): str,
    Optional("pinoffset"): str,
    Optional("pinstride"): str,
    Optional("gpu_id"): str,
    Optional("gputasks"): str,
    Optional("ddcheck"): str,
    Optional("rdd"): str,
    Optional("rcon"): str,
    Optional("dlb"): str,
    Optional("dds"): str,
    Optional("nb"): str,
    Optional("nstlist"): str,
    Optional("tunepme"): str,
    Optional("pme"): str,
    Optional("pmefft"): str,
    Optional("bonded"): str,
    Optional("update"): str,
    Optional("v"): str,
    Optional("pforce"): str,
    Optional("reprod"): str,
    Optional("cpt"): str,
    Optional("cpnum"): str,
    Optional("append"): str,
    Optional("nsteps"): str,
    Optional("maxh"): str,
    Optional("replex"): str,
    Optional("nex"): str,
    Optional("reseed"): str,
}


class MdrunParameters(Dict):
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

        Usage: ``MdrunParameters(dict{'ignore-case': True})``

        :param parameters_dict: dictionary with commandline parameters
        :param type parameters_dict: dict

        """
        dict = self.validate(dict)
        super().__init__(dict=dict, **kwargs)

    def validate(self, parameters_dict):
        """Validate command line options.

        Uses the voluptuous package for validation. Find out about allowed keys using::

            print(MdrunParameters).schema.schema

        :param parameters_dict: dictionary with commandline parameters
        :param type parameters_dict: dict
        :returns: validated dictionary
        """
        return MdrunParameters.schema(parameters_dict)

    def cmdline_params(self, input_files):
        """Synthesize command line parameters.

        e.g. [ '--ignore-case', 'filename1', 'filename2']

        :param pdbfile: Name of input pdb file
        :param type pdbfile: str

        """
        parameters = []

        parameters.append("mdrun")
        parameters.extend(["-s", input_files["tprfile"]])
        if "cpi_file" in input_files:
            parameters.extend(["-cpi", input_files["cpi_file"]])
        if "table_file" in input_files:
            parameters.extend(["-table", input_files["table_file"]])
        if "tableb_file" in input_files:
            parameters.extend(["-tableb", input_files["tableb_file"]])
        if "tablep_file" in input_files:
            parameters.extend(["-tablep", input_files["tablep_file"]])
        if "rerun_file" in input_files:
            parameters.extend(["-rerun", input_files["rerun_file"]])
        if "ei_file" in input_files:
            parameters.extend(["-ei", input_files["ei_file"]])
        if "multidir_file" in input_files:
            parameters.extend(["-multidir", input_files["multidir_file"]])
        if "awh_file" in input_files:
            parameters.extend(["-awh", input_files["awh_file"]])
        if "membed_file" in input_files:
            parameters.extend(["-membed", input_files["membed_file"]])
        if "mp_file" in input_files:
            parameters.extend(["-mp", input_files["mp_file"]])
        if "mn_file" in input_files:
            parameters.extend(["-mn", input_files["mn_file"]])
        if "plumed_file" in input_files:
            parameters.extend(["-plumed", input_files["plumed_file"]])

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
