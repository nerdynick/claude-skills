SHELL := /bin/bash

.PHONY: all setup clean package-skills package-plugins package-all help list

PACKAGES_DIR := dist
SKILLS_DIR := skills
PLUGINS_DIR := plugins
SKILL_ARCHIVE_DIR := $(PACKAGES_DIR)/skills
PLUGIN_ARCHIVE_DIR := $(PACKAGES_DIR)/plugins

SKILLS := $(sort $(patsubst $(SKILLS_DIR)/%,%,$(wildcard $(SKILLS_DIR)/nerdynik-*)))
PLUGINS := $(sort $(patsubst $(PLUGINS_DIR)/%,%,$(wildcard $(PLUGINS_DIR)/nerdynik-*)))

SKILL_ARCHIVES := $(addprefix $(SKILL_ARCHIVE_DIR)/,$(addsuffix .tar.gz,$(SKILLS)))
PLUGIN_ARCHIVES := $(addprefix $(PLUGIN_ARCHIVE_DIR)/,$(addsuffix .tar.gz,$(PLUGINS)))

all: package-all

help:
	@echo "Available targets:"
	@echo "  make setup            Create packaging directories"
	@echo "  make package-skills   Build skill archives"
	@echo "  make package-plugins  Build plugin archives"
	@echo "  make package-all      Build all package archives"
	@echo "  make clean            Remove generated archives"
	@echo "  make list             List discovered skills and plugins"

setup:
	mkdir -p $(SKILL_ARCHIVE_DIR) $(PLUGIN_ARCHIVE_DIR)

list:
	@echo "Skills:"
	@for pkg in $(SKILLS); do echo "  - $$pkg"; done
	@echo "Plugins:"
	@for pkg in $(PLUGINS); do echo "  - $$pkg"; done

$(SKILL_ARCHIVE_DIR)/%.tar.gz: $(SKILLS_DIR)/%
	mkdir -p $(SKILL_ARCHIVE_DIR)
	tar -czf $@ -C $(SKILLS_DIR) $(notdir $<)

$(PLUGIN_ARCHIVE_DIR)/%.tar.gz: $(PLUGINS_DIR)/%
	mkdir -p $(PLUGIN_ARCHIVE_DIR)
	tar -czf $@ -C $(PLUGINS_DIR) $(notdir $<)

package-skills: $(SKILL_ARCHIVES)

package-plugins: $(PLUGIN_ARCHIVES)

package-all: package-skills package-plugins

clean:
	rm -rf $(PACKAGES_DIR)
