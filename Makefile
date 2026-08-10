SHELL := /bin/bash

.PHONY: all setup clean package-skills package-plugins package-all help list validate

PACKAGES_DIR := dist
SKILLS_DIR := skills
PLUGINS_DIR := plugins
SKILL_ARCHIVE_DIR := $(PACKAGES_DIR)/skills
PLUGIN_ARCHIVE_DIR := $(PACKAGES_DIR)/plugins

SKILLS := $(sort $(patsubst $(SKILLS_DIR)/%,%,$(wildcard $(SKILLS_DIR)/nerdynik-*)))
PLUGINS := $(sort $(patsubst $(PLUGINS_DIR)/%,%,$(wildcard $(PLUGINS_DIR)/nerdynik-*)))

SKILL_ARCHIVES := $(addprefix $(SKILL_ARCHIVE_DIR)/,$(addsuffix .zip,$(SKILLS)))
PLUGIN_ARCHIVES := $(addprefix $(PLUGIN_ARCHIVE_DIR)/,$(addsuffix .zip,$(PLUGINS)))

all: package-all

help:
	@echo "Available targets:"
	@echo "  make list             List discovered skills and plugins"
	@echo "  make validate         Validate the marketplace and plugin manifests"
	@echo "  make setup            Create packaging directories"
	@echo "  make package-skills   Build skill archives"
	@echo "  make package-plugins  Build plugin archives"
	@echo "  make package-all      Build all package archives"
	@echo "  make clean            Remove generated archives"

setup:
	mkdir -p $(SKILL_ARCHIVE_DIR) $(PLUGIN_ARCHIVE_DIR)

list:
	@echo "Skills:"
	@for pkg in $(SKILLS); do echo "  - $$pkg"; done
	@echo "Plugins:"
	@for pkg in $(PLUGINS); do echo "  - $$pkg"; done

validate:
	@command -v claude >/dev/null || { echo "claude CLI not found; install Claude Code to validate."; exit 1; }
	claude plugin validate . --strict
	@for pkg in $(PLUGINS); do \
		claude plugin validate "$(PLUGINS_DIR)/$$pkg" --strict || exit 1; \
	done

$(SKILL_ARCHIVE_DIR)/%.zip: $(SKILLS_DIR)/%
	mkdir -p $(SKILL_ARCHIVE_DIR)
	rm -f $@
	cd $(SKILLS_DIR) && zip -rq "$(abspath $@)" "$(notdir $<)"

$(PLUGIN_ARCHIVE_DIR)/%.zip: $(PLUGINS_DIR)/%
	mkdir -p $(PLUGIN_ARCHIVE_DIR)
	rm -f $@
	cd $(PLUGINS_DIR) && zip -rq "$(abspath $@)" "$(notdir $<)"

package-skills: $(SKILL_ARCHIVES)

package-plugins: $(PLUGIN_ARCHIVES)

package-all: package-skills package-plugins

clean:
	rm -rf $(PACKAGES_DIR)
