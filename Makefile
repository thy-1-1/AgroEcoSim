PYTHON ?= python
export PYTHONPATH := src

.PHONY: demo data scenarios figures test clean

demo:
	$(PYTHON) scripts/run_pipeline.py

data:
	$(PYTHON) scripts/generate_demo_data.py

scenarios:
	$(PYTHON) scripts/run_scenarios.py

figures:
	$(PYTHON) scripts/generate_figures.py

test:
	$(PYTHON) -m unittest discover -s tests -v

clean:
	rm -rf results/trajectories
	rm -f results/tables/indicator_scores.csv
	rm -f results/figures/*_generated.svg
