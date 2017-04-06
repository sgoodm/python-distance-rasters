rm dist/*
python setup.py sdist --formats=gztar,zip bdist_wheel
twine upload dist/*
