# Subway System Simulator

This is a brief description of your project.

## Installation

To install the necessary packages, you need to have Python and pip installed on your system. If you don't have them, you can download Python [here](https://www.python.org/downloads/) and pip will be installed with it.

### Virtual env (optional)
If you would like to ensure that your dependencies remain isolated, it is recommended to setup a virtual environment.

To set up a virtual environment for your project, follow these steps:

1. Open a terminal or command prompt.
2. Navigate to the root directory of your project.
3. Run the following command to create a virtual environment:

    ```sh
    python -m venv venv
    ```

4. Activate the virtual environment:

    - On Windows:

      ```sh
      venv\Scripts\activate
      ```

    - On macOS and Linux:

      ```sh
      source venv/bin/activate
      ```

Make sure the project is activated before continuing to the next step.

Remember to always activate the virtual environment before working on your project to ensure that you're using the correct dependencies.

### Install dependencies

Once you have Python and pip, you can install the required packages using the following command:

```sh
pip install -r requirements.txt
```

# Usage
Run the program with the following command:
```sh
python main.py
```
## Specifying Start and End Stations from the CLI
Running the program with no command line arguments will result in the user being prompted to select the start and end stations using fuzzy search. Start and end stations can be defined with the following command line arguments:
```sh
# Select only start station (end station will be prompted with fuzzy search)
python main.py --start "<start station name>"
# Select only end station (start station will be prompted with fuzzy search)
python main.py --end "<end station name>"
# Select both start and end station
python main.py --start "<start station name>" --end "<end station name>"
```
## Specifying input file
The default subway layout file is the manhattan.json file. If you would like to use a different one (such as the small_example.json file provided) you can use the --input command line argument
```sh
python main.py --input small_example.json
```
If a station name(s) or the input file provided as command line arguments do not exist, the program will exit early.