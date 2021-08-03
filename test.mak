all:

test:
	( cd Python-Object && perl Makefile.PL && make install ) && python3 setup.py install --user && python3 tests/__init__.py
