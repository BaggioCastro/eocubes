pydocstyle *.py && \
isort eocube setup.py --check-only --diff && \
check-manifest && \
pytest && \
sphinx-build -qnW --color -b doctest help/source help/_build && \
sphinx-build -b html -d _build/doctrees help/source docs