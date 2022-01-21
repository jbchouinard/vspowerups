default: dist/vsoptimizer

dist/vsoptimizer: venv
	venv/bin/pyinstaller -F --windowed vsoptimizer.py

venv:
	python -m venv venv
	venv/bin/pip install pyinstaller

clean:
	rm -rf venv build dist

.PHONY: default extension clean
