"""Methods for extracting and dealing with various types of files that can be
declared within a gromacs topology file."""

import re


def itp_finder(mdpfile, topfile):
    """Extract included files from the topology file.

    This method will grab a list of all includes and then try to sort them
    based on if they are in C directive tags and if flags in the MDP affect
    them.
    """

    # Grab the file contents.
    top = topfile.get_content()
    mdp = mdpfile.get_content()

    # find all include statements in top
    found_include = re.findall(r'#include "([\S\s]*?)"', top, re.DOTALL)

    # find ifdef and define statements in top
    found_ifdef = re.findall(r"#ifdef ([\S\s]*?)\n", top, re.DOTALL)
    defines = re.findall(r"#define ([\S\s]*?)\n", top, re.DOTALL)

    # find defines in mdp file.
    found_def = re.search(r"define([\S\s]*?)\n", mdp, re.DOTALL)
    if found_def is not None:
        found_def = re.findall(r"-D([\S\s]*?) ", found_def.group(), re.DOTALL)
        defines.extend(found_def)

    # find ifndef and undefine statements in top
    found_ifndef = re.findall(r"#ifndef ([\S\s]*?)\n", top, re.DOTALL)
    undefines = re.findall(r"#undef ([\S\s]*?)\n", top, re.DOTALL)

    # Extract includes between ifdefs and tag them against vars.
    for item in found_ifdef:
        # Find the directive
        ifdef_tag = re.search(f"#ifdef {item}([\S\s]*?)#endif", top, re.DOTALL)

        # Find the includes
        if (ifdef_tag is not None) and ((item not in defines) or (item in undefines)):
            ifdef_includes = re.findall(r'#include "([\S\s]*?)"', ifdef_tag.group(), re.DOTALL)
            found_include = list(set(found_include) - set(ifdef_includes))

    # Extract includes between ifndefs and tag them against vars.
    for item in found_ifndef:
        # Find the directive
        ifndef_tag = re.search(f"#ifndef {item}([\S\s]*?)#endif", top, re.DOTALL)

        # Find the includes
        if (ifndef_tag is not None) and ((item in defines) and (item not in undefines)):
            ifndef_includes = re.findall(r'#include "([\S\s]*?)"', ifndef_tag.group(), re.DOTALL)
            found_include = list(set(found_include) - set(ifndef_includes))

    if found_include:
        # First check blacklisted files.
        files = gmx_blacklist(found_include)

        # Now check which ones are in dirs and which are in PWD.
        pwd, subdirs = filepath_check(files)

        return pwd, subdirs
    else:
        return False, False


def filepath_check(files):
    """Seperate files in PWD and those in subdirs."""

    subdirs = []

    # Iterate all found files and check if they are in subdirs.
    for item in files:
        # paths containing dirs will have slashes in them.
        if "/" in item:
            subdirs.append(item)

    # Remove the ones containing dirs from the original list of files
    files = list(set(files) - set(subdirs))

    return files, subdirs


def gmx_blacklist(includes):
    """Remove itp files that are part of gromacs itself."""

    blacklist = [
        "amber03.ff",
        "amber94.ff",
        "oplsaa.ff",
        "gromos53a5.ff",
        "amber96.ff",
        "gromos43a2.ff",
        "amber99sb.ff",
        "amber99.ff",
        "gromos54a7.ff",
        "gromos43a1.ff",
        "amberGS.ff",
        "charmm27.ff",
        "amber99sb-ildn.ff",
        "gromos53a6.ff",
        "gromos45a3.ff",
    ]

    # Remove banned directory substrings
    for banned_ipt in blacklist:
        includes = [x for x in includes if banned_ipt not in x]

    return includes
