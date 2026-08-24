.PHONY: help clean install lint format test typecheck check build package terraform-fmt terraform-validate

PYTHON ?= python
PIP ?= $(PYTHON) -m pip
BUILD_DIR ?= build
TERRAFORM_DIR ?= terraform
WEBSITE ?= demo-hotel
REGION ?= ap-south-1
SUBDOMAIN ?= www
TFVARS ?= values/$(WEBSITE)/$(REGION)/$(SUBDOMAIN).tfvars
BACKEND_CONFIG ?= values/$(WEBSITE)/$(REGION)/$(SUBDOMAIN).backend.hcl

help:
	@echo "Targets:"
	@echo "  make install"
	@echo "  make lint"
	@echo "  make format"
	@echo "  make test"
	@echo "  make typecheck"
	@echo "  make check"
	@echo "  make build"
	@echo "  make terraform-fmt"
	@echo "  make terraform-validate"
	@echo "  make terraform-plan WEBSITE=demo-hotel REGION=ap-south-1 SUBDOMAIN=www"
	@echo "  make clean"

install:
	$(PIP) install -e ".[dev]"

lint:
	$(PYTHON) -m ruff check .

format:
	$(PYTHON) -m ruff format .

test:
	$(PYTHON) -m pytest

typecheck:
	$(PYTHON) -m mypy

check: lint typecheck test

build:
	mkdir -p $(BUILD_DIR)
	$(PYTHON) scripts/build_lambda.py

package: build

terraform-fmt:
	terraform fmt -recursive $(TERRAFORM_DIR)

terraform-validate:
	cd $(TERRAFORM_DIR) && terraform init -backend=false && terraform validate

terraform-plan:
	cd $(TERRAFORM_DIR) && terraform init -backend-config=$(BACKEND_CONFIG) && terraform plan -var-file=$(TFVARS)

clean:
	rm -rf $(BUILD_DIR)
	rm -rf .pytest_cache .ruff_cache .mypy_cache
