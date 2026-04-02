# Impulse Labs Guide

## GitHub Operations

### Pull or Update Code
```bash
git pull
````

### Add and Push Your Changes

```bash
git add -A
git commit -m "Some message"
git push origin main
```

---

## Installation

### Generic Installation

```bash
pip install -r requirements.txt
```

or

```bash
python -m pip install -r requirements.txt
```

### If You Face a PyQt5 Error

Install **PySide6** instead:

```bash
pip install pyside6
```

or

```bash
python -m pip install pyside6
```

This should allow the `run_ui.py` file to work properly.

### Alternative Method

Create an **Anaconda environment with Python ≤ 3.11**, then install the dependencies:

```bash

```

---

## Files to Run

### UI File (Frontend + Backend)

```bash
python run_ui.py
```

### Operations File (Backend Only)

```bash
python main.py
```

---

## License Options

One of the following licenses may be used:

* Apache 2.0 License

