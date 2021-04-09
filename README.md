# Automation of Plots for Reports
This is the main repository for the Lowe Institute's Automation of data processing and plot creation. The goal is to be able to pull data automatically, process it, and create plots at the beginning of each report-writing cycle. This will make our lives a lot easier and free up time to do fun stuff!

## Prerequisites

- Late model Python 3
- Late model R and RStudio
- Git

## Which Prerequisites do I Care About?

If you are unfamiliar with either Python or R (or both), you are welcome to learn it (resources are listed at the bottom of the README). However, if you do not want to learn them, that's okay as well. You are still required to learn how to use Git and GitHub, since all files (including non-code files) will be placed here. You will need the following languages for the following tasks:

- Python: Pulling data from APIs, preliminary processing of data (getting rid of stuff we obviously don't want), preliminary data cleaning, creating CSV files that can be pulled and processed in R.
- R: Plot-specific data processing (i.e., rearranging a dataframe to get what you want), plotting in ```ggplot2```.

If you don't learn how to use one of these languages, you won't be able to contribute for those particular tasks. But, there will still be plenty more you can do!

## Project Conventions
We define some basic conventions to streamline our workflow and make things easier to organize. If you take issue with any of these, please let us know! We're more than willing to change things that don't work for you all :)

#### Main Branch
The main branch for this repository is called ```master```. This is where we will do most of our work. However, if you are making changes to an **existing** code file, then create a new branch for it. More details on branches blow.

#### Work Tickets and Branches
We will be using GitHub Issues (the issues tab on the repository) to track work and give assignments. If the assignment requires you to heavily modify existing code, make a new branch for working on this issue. If not, you can push directly to the ```master``` branch. 

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

When you are done working on this branch, create a pull request and we will review it before merging it to the ```master``` branch.

Remember, it is only **required** that you create a branch when you are instructed to make **major changes** to an existing file, like ```README.md```. If not, you are still free to make your own branch, but it is not required and you can just push to ```master```. If all you are doing is adding stuff (like additional helper functions), and not modifying what already exists, there is no need to create a new branch. Just to minimize merge conflicts :)

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
Corey Schafer has a great introduction to Python on [this](https://www.youtube.com/watch?v=YYXdXT2l-Gg&list=PL-osiE80TeTskrapNbzXhwoFUiLCjGgY7) YouTube playlist. For our purposes, you'll need to know the contents of about the first 9 videos (basic data types and control flow that we'll work with a lot, as well as functions and modules). We'll teach you the basics of how to use the packages we'll be working with in workshops and all (I want to commit to recording a mini-lecture series, but no promises). Here's the link to the playlist: https://www.youtube.com/watch?v=YYXdXT2l-Gg&list=PL-osiE80TeTskrapNbzXhwoFUiLCjGgY7

#### R

CodeCademy has a free course: https://www.codecademy.com/learn/learn-r

The first 4 modules will be essential to what we do, and going through the rest may be useful for learning some of the data processing. But you can go through that stuff as you need it.
