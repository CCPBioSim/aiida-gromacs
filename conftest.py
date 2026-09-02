"""pytest fixtures for simplified testing."""

import pytest

pytest_plugins = "aiida.tools.pytest_fixtures"


@pytest.fixture(scope="function", autouse=True)
def clear_database_auto(aiida_profile_clean):
    """Automatically clear database in between tests."""


@pytest.fixture(scope="function")
def gromacs_code(aiida_code, aiida_localhost):
    """Get a gromacs code."""
    return aiida_code(
        "core.code.installed",
        label="gromacs",
        computer=aiida_localhost,
        filepath_executable="gmx",
    )


@pytest.fixture(scope="function")
def bash_code(aiida_code, aiida_localhost):
    """Get a bash code."""
    return aiida_code(
        "core.code.installed",
        label="bash",
        computer=aiida_localhost,
        filepath_executable="bash",
    )
