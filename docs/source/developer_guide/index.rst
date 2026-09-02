===============
Developer guide
===============

As a project we are open to contributions from the wider community to help us add new features. To get up and running as a developer contributing to this plugin, you will need to have a working installation of AiiDA installed on your computer. You should follow the steps to install AiiDA on the following page, but don't run the pip install of the aiida-gromacs plugin :doc:`../user_guide/installation` you will also need to have the conda environment activated and the verdi daemon running :doc:`../user_guide/aiida_sessions`.

Clone the repository
++++++++++++++++++++

The first step in getting going as a developer is to clone our git repository by either

#. HTTPS::

        git clone https://github.com/CCPBioSim/aiida-gromacs.git

#. SSH::

        git clone git@github.com:CCPBioSim/aiida-gromacs.git

Running the tests
+++++++++++++++++

To run our test suite, in addition to having AiiDA installed, you should also have the daemon running, which will include the full AiiDA startup steps for the database and an initial user profile to be setup.

The following will discover and run all unit test::

    pip install -e .[testing]
    pytest -v

Automatic coding style checks
+++++++++++++++++++++++++++++

We are implemting automated coding style checks, so that we are all commiting code to similar code quality standards.

Enable enable automatic checks of code sanity and coding style::

    pip install -e .[pre-commit]
    pre-commit install

If you ever need to skip these pre-commit hooks, just use::

    git commit -n

Though, for pull requests to be accepted, we will expect these to have been resolved before pulling.


Continuous integration
++++++++++++++++++++++

``aiida-gromacs`` comes with a ``.github`` folder that contains continuous integration tests on every commit using `GitHub Actions <https://github.com/features/actions>`_. It will:

#. run all tests including against several package dependencies and their versions.
#. build the documentation.
#. check coding style and version number (not required to pass by default).

We have these activated on github via the github actions platform. When version numbers are tagged, we will also automatically push a version to pypi.

Building the documentation
++++++++++++++++++++++++++

 #. Install the ``docs`` extra::

        pip install -e .[docs]

 #. Edit the individual documentation pages in::

        docs/source/user_guide/
        or
        docs/source/developer_guide/

 #. Use `Sphinx`_ to generate the html documentation::

        cd docs
        make

Check the result by opening ``build/html/index.html`` in your browser.

Putting it all together
+++++++++++++++++++++++

Putting all of the above together into the following install commands::

        git clone git@github.com:CCPBioSim/aiida-gromacs.git
        cd aiida-gromacs
        pip install -e .[docs,pre-commit,testing]
        pre-commit install

Will install the plugin from the git repository with all of the above features activated.

Sending code contributions
++++++++++++++++++++++++++

We will always welcome code contributions for new features, but these should always be via the submission of a pull request. Upon receiving a PR, the CI workflow will automatically run our test suite, buld the docs and run the pre-commit checks. One of the core developers will review the code submitted and make a decision based upon the fit of the PR with the project goals and make an assessment of the quality of the contribution.

We would always recommend reporting problems/bugs via the issue tracker even if you intend to attempt a fix, likewise we would recommend contacting a member of the core team if developing features of your own so they can advise on the direction of the project.

Version Numbering
+++++++++++++++++

We will align our version numbering against the AiiDA major series that the plugin release supports. So our first release will be v2.0.0, where the X in vX.Y.Z corresponds to the AiiDA major series that the plugin is supporting. So v2.0.0 will support AiiDA 2.x.x. The remaining two numbers in our versioning will represent major and minor changes to the plugin respectively. A minor release can be expected to be version compatible with no breaking changes, whilst a major release will be expected to cause changes that are breaking in nature.

To make and release a new version of the plugin, update the version in ``__init__.py`` and then add the "tag-release" label to the PR. This will trigger the CI to automate tagging a release, make a new release on github and then push the new version to PyPI. This should be done after all relevant PRs for a particular release have been reviewed and merged to main and all the CI tests have completed and passed. You should make sure the version in ``__init__.py`` contains the following format vX.Y.Z, the "v" is important for CI automation. Upon merging the PR, actions will be triggered to auto make a github release with a full changelog, tests will run against the updated version and then a new version will be sent to PyPI for users to download.

Happy coding!

.. _Sphinx: https://www.sphinx-doc.org/en/main/
