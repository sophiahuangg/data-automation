# Automation of Plots for Reports
This is the main repository for the Lowe Institute's Automation of data processing and plot creation. The goal is to be able to pull data automatically, process it, and create plots at the beginning of each report-writing cycle. This will make our lives a lot easier and free up time to do fun stuff!

Note that this README is heavily biased towards Ubuntu and Mac operating systems. If you are running windows and want to add separate instructions for it to the README, please do :)

## Prerequisites

- Late model Python 3
- Late model R and RStudio
- Git
- [Anaconda](https://repo.anaconda.com/archive/Anaconda3-2020.11-Windows-x86_64.exe)
- Late model [Docker](https://www.docker.com/get-started)

## Which Prerequisites do I Care About?

If you are unfamiliar with either Python or R (or both), you are welcome to learn it (resources are listed at the bottom of the README). However, if you do not want to learn them, that's okay as well. You are still required to learn how to use Git and GitHub, since all files (including non-code files) will be placed here. You will need the following languages for the following tasks:

- Python: Pulling data from APIs, preliminary processing of data (getting rid of stuff we obviously don't want), preliminary data cleaning, creating CSV files that can be pulled and processed in R.
- R: Plot-specific data processing (i.e., rearranging a dataframe to get what you want), plotting in ```ggplot2```.

If you don't learn how to use one of these languages, you won't be able to contribute for those particular tasks. But, there will still be plenty more you can do!

## Conda Environment

We use a conda environment called `lowe` in order to keep our Python version and packages consistent across all of our machines. This helps  (but doesn't completely) solve the "but it builds on my machine!" issue. We have turned the project into a module so we can access the data from anywhere in our repository. To install this environment, make sure you are in the `data-automation/` directory and use the following commands:

```bash
conda create -n lowe python=3.8

conda activate lowe

pip install -e .
```

To activate this environment (must be done in any shell you use to run a script prior to running it), use `conda activate lowe`. To deactivate this environment to return to the `base` environment when you are done working, use `conda deactivate`. 

## Updating the Conda environment

NOTE: this may not work on Windows. Not sure if it will. Let a manager know if it doesn't

Since the project is installed as a Python package, edits should be made to `setup.py`. Check the file and you should see where to add packages. Add any packages you want in alphabetical order and run the following commands to make sure the project can still build:

```bash
# Nuke old conda environment
conda env remove -n lowe

# Create clean conda environment
conda create -n lowe python=3.8

# Add package in alphabetic order to setup.py

# Install the package
pip install -e .

# Assuming it builds, update requirements.txt
pip freeze > requirements.txt

# Update environment.yml without the prefix line which has a path on your machine in it and isn't required
conda env export -n lowe | grep -v prefix > environment.yml
# If you are using Windows, you can just do: conda env export -n lowe > environment.yml 

# Manually inspect both requirements.txt and environment.yml to make sure nothing is broken

git add setup.py requirements.txt environment.yml

git commit -m "+<package-name-1> +<package-name-2> -<package-name-3>"
# Example: if you add pandas and numpy and remove pytest
# git commit -m "+pandas +numpy -pytest"
```

TODO: Write a shell script that does this in one sweep
TODO: Migrate the package to [poetry](https://python-poetry.org/) to make the process way simpler

## Docker

Docker is a software that allows developers to create a lightweight virtual machine (but not really a virtual machine) called an **image**, which is a snapshot of a operating system and its constitutent files. You can build and run this image on your local machine, during which it is called a **container**. The container allows you to develop software in the environment of the image instead of your local machine. This allows you to avoid any problems of the project building on one operating system and not another. 

We will be using docker as an alternative to the conda environment in the case that your code doesn't build on the conda environment, or if you have any other issues.

If you want to learn more about docker, you can look at the documentation [here](https://www.docker.com/resources/what-container).

### Installing Docker

You can download docker from [this](https://docs.docker.com/get-docker/) website. It may ask you to create a free account -- just make one with whatever email you prefer.

### Using Docker Container with Visual Studio Code

We'll be running the containers through VScode's remote container extension. To do this, you can use the VScode "Remote Container" extension from the VScode extensions.

Once installed, you will see the remote explorer icon on the left sidecar of of your VSCode. After clicking it, a sidebar will appear, at the top of which the word `containers` will be displayed. (Note that you must have docker running for this to work.) Then click the + sign and click open folder in container. The folder you open in this container is our github repo that you have on your local machine. It will build a local container for you with our development environment and filesystem built. Any terminal you open while in this session will be run through the container, not your host OS.

In essence, a Docker container is a lot like a lightweight virtual machine. They are very different (as you can see in [this thread](https://stackoverflow.com/questions/16047306/how-is-docker-different-from-a-virtual-machine)). If you're curious for rigorous definitions and the actual differences between containers and VMs, check out the thread :)

## Data Version Control (DVC)

We want to be able to version our datasets and store them remotely (not in the git repository) so as to not violate any of github's file size limits. Luckily, this is what DVC allows us to do. First, install DVC using the instructions for your relevant OS [here](https://dvc.org/doc/install) -- install the version that integrates into your command line (i.e. not the pip one; that will already be installed when you set up your environment). On Mac OSX, this is as simple as running `brew install dvc`. On Ubuntu, use `snap install --classic dvc`. On Windows, if you have the `choco` package manager installed, just use `choco install dvc` in `Cmder` (won't work in a non-elevated environment). You can download `Cmder` if you don't have it. If you don't have `choco` installed, install it.

More Specific Directions for DVC Installation with Windows:
- https://dvc.org/doc/install/windows
- https://dvc.org/doc/user-guide/running-dvc-on-windows

**ALL** datasets we scrape, and those that we clean, will go inside DVC. We do not want to store datasets in the git repository if we can avoid it, except for those directly relevant to our packages.

For more information on how DVC works and a basic tutorial, check out their [docs](https://dvc.org/doc/start/data-and-model-versioning) -- not necessary, but useful if knowing how things works helps you use them.

To set up DVC with our remote storage bucket, you need to add our google drive folder as a remote. **IMPORTANT NOTE** -- when you do this next step, you **need** to be in contact with Abhi. You have to log in to the Lowe Institute Google Drive, which currently only he has Duo access to. If that is the case, then you can do the following:

```bash
dvc remote add --project -d bucket gdrive://1YginFyGcEZu1MpRdmYVZiTAOhTWJV-bV
```

To pull files from DVC, use

```bash
dvc pull
```

To add files to DVC, follow these steps:

```bash
# First make sure you have all the up to date files
dvc pull

# now add the file you want
dvc add path/to/file/example.filetype

# dvc will prompt you to run a command that looks something like
git add path/to/file/example.filetype.dvc path/to/file/.gitignore

# Commit and push
git commit -m "add example dataset to DVC"
git push

# Push to DVC
dvc push
```

## Project Conventions
We define some basic conventions to streamline our workflow and make things easier to organize. If you take issue with any of these, please let us know! We're more than willing to change things that don't work for you all :)

#### Main Branch
The main branch for this repository is called ```master```. This is where we will store our files after they have been developed and tested on different branches.

#### Work Tickets and Branches
We will be using GitHub Issues (the issues tab on the repository) to track work and give assignments. All work must be done on branches (commits to `master` are blocked).

We will keep track of branches with a systematic way of titling them. They should be titled as

```bash
<IssueNumber>-<Short-Description>
```

You can create a branch using 

```bash
git checkout -b branchName
```

For example, if my assignment were to fix this README file, and this assignment was given to me as ticket number 5, I would create a new branch since I am editing an existing file. To do this, I would type

```bash
git checkout -b 5-readme-fix
```

When you are done working on this branch, create a pull request and we will review it before merging it to the ```master``` branch. Pull requests must pass the linting checks (and any other checks we add), and must undergo a review by at least one manager.

Note that a branch will **not** be visible to others until you make a commit and push to it.

#### VSCode Live Share

If you're working with someone concurrently on the same script, it's sometimes helpful to work together on it. Luckily, Visual Studio Code (the text editor / IDE you should use) has a Live Share extension pack. TO install it, search for extensions (there should be an icon on the left-had-side bar). Search "liveshare" and install the Live Share Extension Pack. 

## Coding Conventions

Here we will define coding conventions to ensure proper documentation of our code. By following these conventions, it helps others (and maybe even your future self) understand the code you've written. 

These conventions are highly detailed and specific. If some of these conventions do not work for the code you are writing feel free to use conventions that suit your code and coding style. However, we do ask that your code to be readable and consistent.

### Linting

To standardize our code styling and save a lot of time reviewing PRs, all code included in pull requests **must** pass an automated code styling check for two linters: `black` and `flake8`. Both of these are included in our python environment and are able to be run from the terminal. However, if you want to configure `black` to run whenever you save your file in VS Code, follow [these instructions](https://marcobelo.medium.com/setting-up-python-black-on-visual-studio-code-5318eba4cd00).

In order to run `black`, type in your terminal

```bash
black <path>
```

If you provide a folder, `black` will lint all `.py` files in the folder. `black` will automatically make changes. Provided that you had no staged files prior to running this, do

```bash
# Commit all of the linted files -- be careful if you already staged files earlier. Commit and push those first.
git add .
git commit -m "black compliance fix"
git push
```

Now do the same for `flake8`:

```bash
flake8 <path>
```

Note that `flake8` will not automatically format anything for you. It will tell you the edits that need to be made, and you will have to make them. After you make all edits, run

```bash
git add . #once again, assuming you had no staged files prior to making flake8 edits
git commit -m "flake8 compliance fix"
git push
```

If done correctly, checks should pass on your pull requests now. If not, let an admin / manager know and we will help you fix the issues.
### Docstrings and Function Definitions

#### Function Definitions

Function names must be descriptive, i.e. names such as "function" or "do_something" can NOT be used. For example, if you want to write a function that gets a city name then your function can be named ```get_city_name()```.

To guarantee that we pass in the correct argument type to a function, function parameters should include type hinting. With this method, if an argument with the wrong type is passed in, a type error will be given.

An example of a function definition is 

```python
def get_city_name(geoid: str) -> str:
```

You can also use default arguments for your function parameters to guarantee that an argument is passed into the function even if no argument is given during the function call. For example

```python
def geoid_from_city(city: str = "Rancho Mirage, CA") -> str:
```

will still run even if you call the function ```geoid_from_city()```.

If a function can take multiple arguments, then you can use `typing.Union`:

```python
from typing import Union

def descriptive_function_name(descriptive_arg_name: Union[str, int]) -> float:
    '''Function that does something'''
    pass
```

There are many ways to be specific with the `typing` package. For example, if you want to include a type hint for a list of strings, you can do

```python
from typing import List

def get_nicknames(name: str) -> List[str]:
    '''returns all nicknames for a given name'''
    pass
```

#### Docstrings
Docstrings are a convenient way of documenting the functions we write. Docstrings inclue a description of your function, the arguments it needs, and the output of the function. Docstrings appear right after the function definition and you can create one by using triple quotes ``` """ [docstring here] """ ``` or ``` ''' [docstring here] ''' ```. 

Here is an example docstring from the ```lowe/acs/acs_async.py``` file.

```Python
def _base_uri(
    self,
    year: Union[int, str],
    tabletype: str = "detail",
    estimate: Union[int, str] = "5",
) -> str:
    """_base_uri generates the base URI for the ACS API for each type of table and the 1, 3, and 5 year estimate tables

    Parameters
    ----------
    year : Union[int, str]
        Year we want to pull the data for
    tabletype : str, optional
        Type of table we want to pull, by default "detail"
        Options are:
        - "detail" <--> ACS Detail tables,
        - "subject" <--> Subject Tables,
        - ["profile", "data profile", or "dprofile"] <--> Data Profile Tables,
        - ["comparison profile", "comp profile", "cprofile"] for ACS comparison profiles
    estimate : Union[int,str], optional
        Type of ACS estimate tables we want to pull, by default "5"
        Options are "5", "3", and "1". We typically use 5-year estimates when available.

    NOTE: 1 year estimate URLs will almost definitely not work, but 3- and 5-year estimates will

    Returns
    -------
    str
        Base URL for querying ACS API
    """
```
Docstrings are **required** for all major functions that will be used by others. This is currently our only way of documenting how to use different parts of our packages, and so we have to be as detailed as possible.

In order to generate docstrings in this format, we use the [VS code docstring generator](https://marketplace.visualstudio.com/items?itemName=njpwerner.autodocstring). Once you install the extension, you will need to tweak the settings to use the `numpy` format. To access your settings, use the VS code extensions tab and type `@ext:autodocstring` in the search bar. Click on the extension, and near the top there will be a settings button (you can also click the wheel in the search results and navigate to `Extension Settings`). Here are the complete settings you will need:

- Docstring format: `numpy`
- Generate docstring on enter: `on`
- Guess types: `on`
- Include extended summary: `off`
- Include name: `on`
- Log level: `info`
- Quote style: `"""`
- Start on new line: `off`

If there is something important about the function that you want to convey to readers, use ```NOTE:``` to highlight the important information.

### Comments

Besides docstrings, comments should be written throughout your functions for others to understand your code. Similar to a step-by-step guide you created a function. Addtionally, comments should be written on any code that can be ambiguous to readers. A good way to know when to comment is if you had to think for a while to write the code. However, you do not need to comment everything. For example, variable initialization does not need to be commented since it is pretty straightforward. You can add a comment by using the hash sign ```#```.

If you write code that does not define functions, make sure you write a comment at the top of the code block of what it does. For example:

``` python
#--------
# Script that cleans the geocode csv file to split the city geoid and the state geoid
# And makes it to a new csv file.
#--------
```

Furthermore, if you are unable to finish the code you are working on, make sure to write a ```#TODO:``` comment in the area you need to finish with a description of what needs to be done. This ensures that if other people work on the code, they know what still needs to be done with the code. If there are overall todos, you can leave the code block

```python
# ---------------------------
# THINGS TO DO:
# ---------------------------

# TODO: [description]

```
at the top of the file with the descriptions of the things you need to do. 

Also, if your code can be partitioned into different sections, please leave comment blocks that describe what each section does. For example,

``` python

# ---------------------------
# Utilities
# ---------------------------

# Utility functions that are used as helpers throughout the script

# [insert code here]
# ...

# ---------------------------
# Filtering and Querying
# ---------------------------

# Functions to filter and query datasets

# [insert code here]
# ...
```

### Medallion Tables

We refer to datasets in three tiers:

- **Bronze Tables** (lowest tier): Raw data, pulled directly from APIs with no or minimal transformations applied. Essentially, the easiest but messiest possible dataframes we can construct from the API data.

- **Silver Tables** (middle tier): Data that has been processed to a decent degree. This table is not ready for use in production but is significantly more usable than the bronze tables.

- **Gold Tables** (highest tier): The data has been fully processed for some purpose and is ready to be imported and used. For example, a gold table could be the data we use (and perfectly formatted for) a plot that will go in our final reports.

It is possible in some cases to go straight from bronze --> gold. Though I've personally never seen it happen, it might happen in our case since some of the plots will likely be very simple.

## Helpful Information for Some APIs

#### American Community Survey (ACS)

##### Signing Up for an API Key

1. Go to http://www.census.gov/developers/
2. Click on **REQUEST A KEY** on the left side of the page
3. Fill out the pop-up window form
4. You will get an email with your key code in the message and a link to register it. Enter the organization name as *Lowe Institute of Political Economy*.

Now we need to use the API key in our Python code in order to make certain requests. While you could simply paste in the API key into your file as a variable, we do not recommend this since this is a public repo and any code you push that explicitly mentions your API key will therefore make your API key open to the public. 

Let's make our code more secure by making a file named ".env" in this directory once you've cloned this repo onto your local machine. Because we've added ".env" into our ".gitignore" file, we can each maintain separate ".env" files holding our own API keys. This is useful for us because if we decide to use other API's later, we can use this same codebase and add any additional API keys to this same file. 

In the ".env" file you just created, you only need to add one line: 
```API_KEY_ACS='<your-api-key-goes-here>'```
You don't have to name it "API_KEY_ACS" exactly but if you change that, just make sure you change the reference in the code. 

We can use this file later to add other API keys that we want to keep private. 
In order to use our keys in our scripts, pip install the python-dotenv package then import ```load_dotenv()``` from the ```dotenv``` package. This package will be used in tandem with the ```os``` package to get your environment variable. Note that the dotenv package must be installed with

```bash
pip3 install python-dotenv
```

or

```bash
pip install python-dotenv
```

Then, at the beginning of your script, type in

```python
from dotenv import load_dotenv
load_dotenv()
import os
API_KEY = os.getenv("API_KEY_ACS")
```
If you named your key something else in the .env file just make sure you use that string in the ```os.getenv(<keyname>)``` function. This method is preferred because there's no need to ever directly copy your API key into your code.

##### Other Tips

American Community Survey API documentation for 5-year estimates: https://www.census.gov/data/developers/data-sets/acs-5year.html

Geographic codes for ACS: https://api.census.gov/data/2019/acs/acs5/subject/examples.html

Check out the ```notes.md``` file for some more details and useful links!

## Learning Resources

If you are interested in learning how to use the prerequisite software, we provide some resources here.

#### Git and GitHub

Learn Git in 15 minutes: https://www.youtube.com/watch?v=USjZcfj8yxE
This tutorial will help you understand what Git is, as well as how to install it

Basics of using Git and GitHub together: https://www.youtube.com/watch?v=evgZPMWqpHc&list=PLriKzYyLb28nCh3jJLROcYBvj7ZO0l-3G
The first 5 videos on this playlist are probably all that you will need. There will be some redundant information. If you already know what Git is but don't know how to use it, then just start here!

#### Python 
Corey Schafer has a great introduction to Python on [this](https://www.youtube.com/watch?v=YYXdXT2l-Gg&list=PL-osiE80TeTskrapNbzXhwoFUiLCjGgY7) YouTube playlist. For our purposes, you'll need to know the contents of about the first 9 videos (basic data types and control flow that we'll work with a lot, as well as functions and modules). We'll teach you the basics of how to use the packages we'll be working with in workshops and all (I want to eventually commit to recording a mini-lecture series, but no promises). Here's the link to the playlist: https://www.youtube.com/watch?v=YYXdXT2l-Gg&list=PL-osiE80TeTskrapNbzXhwoFUiLCjGgY7

#### R

CodeCademy has a free course: https://www.codecademy.com/learn/learn-r

The first 4 modules will be essential to what we do, and going through the rest may be useful for learning some of the data processing. But you can go through that stuff as you need it.
