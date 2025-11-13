.PHONY: build develop test lint

develop:
\tpip install --upgrade pip
\tpip install maturin
\tmaturin develop

build:
\tmaturin build

test:
\tpytest -q

lint:
\truff .

