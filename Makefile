.PHONY: verify test provenance clean

verify: test
	PYTHONPATH=src python3 -m patternplate kinds >/dev/null
	python3 scripts/check_stats.py

test:
	PYTHONPATH=src python3 -m unittest discover -s tests -p 'test_*.py' -v

provenance:
	PYTHONPATH=src python3 scripts/gen_provenance.py

clean:
	rm -rf build dist *.egg-info src/*.egg-info
