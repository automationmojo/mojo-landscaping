=======================
python-package-template
=======================
This is a template repository that can be used to quickly create a python package project.

=========================
Features of this Template
=========================
* Machine Setup
* Virtual Environment Setup (Poetry)
* PyPi Publishing
* Sphinx Documentation

========================
How to Use This Template
========================
- Click the 'Use this template' button
- Fill in the information to create your repository
- Checkout your new repository
- Change the following in 'repository-config.ini'

  #. 'PROJECT NAME'
  #. 'REPOSITORY_NAME'

- If you have machine dependencies to add, put them in 'setup-ubuntu-machine'
- Modify the pyproject.toml file with the correct package-name, author, publishing information, etc.
- Rename the VSCODE workspace file 'mv workspaces/default-workspace.template workspaces/(project name).template'
- Replace the README.rst file with your own README
- Update the LICENSE.txt file with your copyright information and license.
- Add your dependencies with python poetry 'poetry add (dependency name)'
- Drop your package code in 'source/packages'
- Modify the name of your package root in 'pyproject.toml'

  #. 'packages = [{include="(root folder name)", from="source/packages"}]'

=================
Code Organization
=================
* .vscode - Common tasks
* development - This is where the runtime environment scripts are located
* repository-setup - Scripts for homing your repository and to your checkout and machine setup
* userguide - Where you put your user guide
* source/packages - Put your root folder here 'source/packages/(root-module-folder)'
* source/sphinx - This is the Sphinx documentation folder
* workspaces - This is where you add VSCode workspaces templates and where workspaces show up when homed.

==========
References
==========

- `User Guide <userguide/userguide.rst>`
- `Coding Standards <userguide/10-00-coding-standards.rst>`
