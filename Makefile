.PHONY: help clean install setup lint format test typecheck check build package new-deployment new-template aws-state-bootstrap terraform-fmt terraform-validate terraform-plan terraform-apply

PYTHON ?= python
PIP ?= $(PYTHON) -m pip
BUILD_DIR ?= build
TERRAFORM_DIR ?= terraform
WEBSITE ?= demo-hotel
REGION ?= ap-south-1
SUBDOMAIN ?= www
STATE_BUCKET ?= ms92-tf-states
STATE_TABLE ?= ms92-tf-states
TEMPLATE_ID ?= contact-v1
TEMPLATE_PRESET ?= contact
TFVARS ?= values/$(WEBSITE)/$(REGION)/$(SUBDOMAIN).tfvars
BACKEND_CONFIG ?= values/$(WEBSITE)/$(REGION)/$(SUBDOMAIN).backend.hcl
TF_INLINE_VARS ?= -var website_name=$(WEBSITE) -var aws_region=$(REGION) -var subdomain=$(SUBDOMAIN)

help:
	@echo "Targets:"
	@echo "  make install"
	@echo "  make setup"
	@echo "  make lint"
	@echo "  make format"
	@echo "  make test"
	@echo "  make typecheck"
	@echo "  make check"
	@echo "  make build"
	@echo "  make new-deployment WEBSITE=demo-hotel REGION=ap-south-1 SUBDOMAIN=contact"
	@echo "  make new-template WEBSITE=demo-hotel TEMPLATE_ID=contact-v1 TEMPLATE_PRESET=contact"
	@echo "  make aws-state-bootstrap REGION=ap-south-1 STATE_BUCKET=ms92-tf-states STATE_TABLE=ms92-tf-states"
	@echo "  make terraform-fmt"
	@echo "  make terraform-validate"
	@echo "  make terraform-plan WEBSITE=demo-hotel REGION=ap-south-1 SUBDOMAIN=www"
	@echo "  make terraform-apply WEBSITE=demo-hotel REGION=ap-south-1 SUBDOMAIN=www"
	@echo "  make clean"

install:
	$(PIP) install -e ".[dev]"

setup:
	$(PYTHON) scripts/setup.py

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
	$(PYTHON) scripts/build_lambda.py

package: build

new-deployment:
	$(PYTHON) scripts/new_deployment.py --website $(WEBSITE) --region $(REGION) --subdomain $(SUBDOMAIN) --state-bucket $(STATE_BUCKET) --state-table $(STATE_TABLE)

new-template:
	$(PYTHON) scripts/new_template.py --website $(WEBSITE) --template-id $(TEMPLATE_ID) --preset $(TEMPLATE_PRESET)

aws-state-bootstrap:
	$(PYTHON) scripts/aws_manual_setup.py state --bucket $(STATE_BUCKET) --table $(STATE_TABLE) --region $(REGION)

terraform-fmt:
	terraform fmt -recursive $(TERRAFORM_DIR)

terraform-validate:
	cd $(TERRAFORM_DIR) && terraform init -backend=false && terraform validate

terraform-plan:
	$(PYTHON) scripts/terraform_deploy.py plan --website $(WEBSITE) --region $(REGION) --subdomain $(SUBDOMAIN)

terraform-apply:
	$(PYTHON) scripts/terraform_deploy.py apply --website $(WEBSITE) --region $(REGION) --subdomain $(SUBDOMAIN)

clean:
	$(PYTHON) scripts/clean.py
