# runner.py

A simple python script for running blocking jobs one after another.

## Installation

To install just run:

```bash
$ make install
```

Works with `python3`. Depends on `arrow` package so before usage run (with `pip` or `pip3`):

```bash
$ pip install arrow
```

## Usage

Run host:

```bash
$ runnery.py run
```

Add jobs:

```bash
$ runner.py add my_job --my --job --arguments
```

List queued jobs:
```bash
$ runnery.py list
```

For additional help:
```bash
$ runnery.py --help
```
