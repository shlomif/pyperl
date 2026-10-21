all:

test:
	( cd Python-Object && perl Makefile.PL && make install ) && python3 setup.py install --user && python3 -m unittest discover -s tests -p '*.py' && python3 test.py
