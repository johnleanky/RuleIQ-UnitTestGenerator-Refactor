# Fresh source revision 1.4 fixtures

These are new synthetic Author materializations, built by scripts/s6_fixtures.py
using reviewed assertion facts plus newly acquired normalized Data Page evidence.
The fixture builder is test-only and never accepts a stored Memory payload for
upgrade. Historical fixtures/s2 and fixtures/s3 remain byte-identical.

Run `.venv-s6/Scripts/python.exe -B scripts/validate_s6_parameters.py` from the
repository root. `--write-fixtures` deliberately rebuilds only these fresh fixture
files; the ordinary gate checks reproducibility. `--historical` runs the unchanged
S5 gate at the fixed baseline with the same interpreter and isolated LF checkout.

Additional full source variants and adversarial normalized evidence cases are
generated in memory by the gate. Evidence categories are repository-static,
connected Memory doubles, and labeled GetCaseData simulation expectations.
None establishes Pega runtime behavior or a general metadata extractor.
