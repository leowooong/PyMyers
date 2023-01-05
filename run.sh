python3 -m pip install --upgrade pip build twine setuptools

# check and format code
pytest
isort ./
mypy ./pymyers/myers.py

# create Source Distributions and wheels
python3 -m build

# upload to pypi
twine upload dist/*

# install editablely
pip install -e ./
# install from source
pip install ./