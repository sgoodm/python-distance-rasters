# distance-rasters

[![build badge](https://github.com/sgoodm/python-distance-rasters/actions/workflows/test-with-coverage.yml/badge.svg)](https://github.com/sgoodm/python-distance-rasters/actions/workflows/test-and-coverage.yml)
[![Coverage Status](https://coveralls.io/repos/github/sgoodm/python-distance-rasters/badge.svg?branch=master)](https://coveralls.io/github/sgoodm/python-distance-rasters?branch=master)
[![Downloads](https://static.pepy.tech/personalized-badge/distancerasters?period=total&units=international_system&left_color=black&right_color=green&left_text=Downloads)](https://pepy.tech/project/distancerasters)

Generate distance raster using arbitrary sets of spatial features

## Install

### Using pip

The latest version of distance-rasters is [available on PyPi](https://pypi.org/project/distancerasters/), so you can install it with pip:
```
pip install distancerasters
```

If you'd like to install the latest development (alpha) release, there may be a newer version on [TestPyPi](https://test.pypi.org/project/distancerasters/):
```
pip install -i https://test.pypi.org/simple/ distancerasters
```

### From source

To install this package from source, first clone this repository, then use pip to install it:
```
git clone git@github.com:sgoodm/python-distance-rasters.git
cd python-distance-rasters
pip install .
```

## Contribute

Issues and pull requests are welcome!

### Testing
If you submit code, please make sure it passes our pytest tests:
```
pip install pytest shapely
pytest
```

### Code Coverage

We use Coveralls to track the code coverage of our tests.
If you clone this repository, you can sign in to Coveralls with your GitHub account, and see code coverage reports for your own copy.
To do this, you'll need to add the repository's token to your repository as a GitHub Secret (see below).

### GitHub Secrets

In a cloned repository, there are three GitHub Secrets required to enable all of our GitHub Actions:
1. COVERALLS_REPO_TOKEN - this is the API token for Coveralls, used for publishing code coverage reports
2. TEST_PYPI_API_TOKEN - this is the API token for TestPyPi, needed for publishing alpha releases
3. PYPI_API_TOKEN - this is the API token for PyPi, needed for publishing releases
