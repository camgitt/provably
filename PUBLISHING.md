# Publishing to PyPI

## Steps

1. Create an account at https://pypi.org/account/register/

2. Create an API token at https://pypi.org/manage/account/token/

3. Create `~/.pypirc` with your token:

```ini
[pypi]
username = __token__
password = pypi-<your-token-here>
```

4. Build and upload:

```
python -m build
twine upload dist/*
```

5. Verify the published package:

```
pip install provably
```
