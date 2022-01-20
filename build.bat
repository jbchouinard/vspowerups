python -m venv winvenv
.\winvenv\Scripts\pip.exe install cython pyinstaller
.\winvenv\Scripts\python.exe setup.py build_ext --inplace
.\winvenv\Scripts\pyinstaller.exe -F --windowed vsoptimizer.py
