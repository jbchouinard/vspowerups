default: dist/vsoptimizer

dist/vsoptimizer: extension
	venv/bin/pyinstaller -F --windowed vsoptimizer.py

extension: venv
	venv/bin/python setup.py build_ext --inplace

venv:
	python -m venv venv
	venv/bin/pip install cython pyinstaller

clean:
	rm -rf venv

.PHONY: default extension clean
