# VSIX extension packager for Private Gallery

This python program extracts information from a `vsix` file and creates the needed files and folder that allow the creation of a NPM package that can be used with the Private Gallery extension.

## Usage

Put the `vsix` file that you want to package in a subfolder and reference this subfolder in the command line when calling the `repackage.py` script.

```bash
./repackage.py extension-subfolder <URL of the NPM repository where the package will be hosted>
```