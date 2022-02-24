# The Discord Digest Codebase

This discord bot is Team 3's submission for the Fall 2020 Tri-Dev Quarterly Project.

![screenshot](https://raw.githubusercontent.com/Kethan02/TriDev-Discord-Bot/main/Screenshot.png)

Our bot scans messages in a guild and sends you a newsletter with important information on what you missed. The project is written in python and uses discord.py, nltk, and MongoDB Altas for storing messages.

It is hosted on heroku so you can add it to your own guild without having to host it, however, you are also welcome to set it up and host it yourself.

## Adding to a Guild

Documentation can be found [here](https://docs.google.com/document/d/1ZiID0doVBtlxTFAziNYPdXTqEeg-O4z_47q1nKTJ3sA/edit?usp=sharing).

## Developer Instructions

If you don't plan on hosting yourself, the rest of this readme is not for you.

### Cloning the repository

Clone the github repo

```bash
git clone https://github.com/Kethan02/TriDev-Discord-Bot.git
```

cd into the repository

```bash
cd TriDev-Discord-Bot
```

### Managing Dependencies

Install pipenv

```bash
pip install --user pipenv
```

Install required dependencies with pipenv

```bash
pipenv install
```

To add a package to pipenv run this

```bash
pipenv install [package_name]
```

### Usage

Run this command

```bash
pipenv run python bot.py
```

For debugging and testing the database code, open db.py and scroll down to the bottom of the file. There should be a main method commented out. Uncomment it and run this

```bash
pipenv run python db.py
```
