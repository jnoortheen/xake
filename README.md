# xake
It is a build tool that can be used and distributed with projects. This tool does automatic discovery of tasks. Task definitions are parsed by [Fire](https://github.com/google/python-fire) and the commands are ran using [xonsh](https://github.com/xonsh/xonsh). 
All the heavy liftings are done by these libraries. 
# Overview

This project was generated with [cookiecutter](https://github.com/audreyr/cookiecutter) using [jacebrowning/template-python](https://github.com/jacebrowning/template-python).

[![Unix Build Status](https://img.shields.io/travis/jnoortheen/xake/master.svg?label=unix)](https://travis-ci.org/jnoortheen/xake)
[![Windows Build Status](https://img.shields.io/appveyor/ci/jnoortheen/xake/master.svg?label=windows)](https://ci.appveyor.com/project/jnoortheen/xake)
[![Coverage Status](https://img.shields.io/coveralls/jnoortheen/xake/master.svg)](https://coveralls.io/r/jnoortheen/xake)
[![Scrutinizer Code Quality](https://img.shields.io/scrutinizer/g/jnoortheen/xake.svg)](https://scrutinizer-ci.com/g/jnoortheen/xake/?branch=master)
[![PyPI Version](https://img.shields.io/pypi/v/xake.svg)](https://pypi.org/project/xake)
[![PyPI License](https://img.shields.io/pypi/l/xake.svg)](https://pypi.org/project/xake)

# Setup

## Requirements

* Python 3.6+

## Installation

Install it directly into an activated virtual environment:

```text
$ pip install xake
```

or add it to your [Poetry](https://poetry.eustace.io/) project:

```text
$ poetry add xake
```

# Usage

After installation, the package can imported:

```text
$ python
>>> import xake
>>> xake.__version__
```
