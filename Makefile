SHELL := /bin/bash

.DEFAULT_GOAL := help
.PHONY: all setup clean package-skills package-plugins package-all package help list \
        validate validate-manifests validate-coverage validate-skills validate-agent-docs \
        test install-hooks uninstall-hooks

# `?=` so the CI collections can override it via the DIST_DIR environment
# variable they all document, without editing this file.
DIST_DIR ?= dist
PACKAGES_DIR := $(DIST_DIR)
SKILLS_DIR := skills
PLUGINS_DIR := plugins
MARKETPLACE_JSON := .claude-plugin/marketplace.json
COVERAGE_SCRIPT := scripts/check-marketplace-coverage.py
FRONTMATTER_SCRIPT := scripts/check-skill-frontmatter.py
AGENT_DOCS_SCRIPT := scripts/check-agent-docs.py
HOOKS_DIR := scripts/hooks
TESTS_DIR := tests
SKILL_ARCHIVE_DIR := $(PACKAGES_DIR)/$(SKILLS_DIR)
PLUGIN_ARCHIVE_DIR := $(PACKAGES_DIR)/${PLUGINS_DIR}

SKILLS := $(sort $(patsubst $(SKILLS_DIR)/%,%,$(wildcard $(SKILLS_DIR)/*)))
PLUGINS := $(sort $(patsubst $(PLUGINS_DIR)/%,%,$(wildcard $(PLUGINS_DIR)/*)))

SKILL_ARCHIVES := $(addprefix $(SKILL_ARCHIVE_DIR)/,$(addsuffix .zip,$(SKILLS)))
PLUGIN_ARCHIVES := $(addprefix $(PLUGIN_ARCHIVE_DIR)/,$(addsuffix .zip,$(PLUGINS)))

# Never ship locally-rendered files or macOS cruft in a distributed bundle.
ZIP_EXCLUDES := -x '*/scripts/build/*' -x '*.DS_Store'

all: validate package

help:
	@echo "Available targets:"
	@echo "  make list                 List discovered skills and plugins"
	@echo "  make validate             Run every validation check"
	@echo "  make validate-manifests   Validate the marketplace and plugin manifests"
	@echo "  make validate-coverage    Check every package is registered in the marketplace"
	@echo "  make validate-skills      Check SKILL.md frontmatter, length and naming"
	@echo "  make validate-agent-docs  Check AGENTS.md still mirrors CLAUDE.md"
	@echo "  make test                 Run the unit tests for the validation scripts"
	@echo "  make install-hooks        Install the git pre-commit hook"
	@echo "  make uninstall-hooks      Remove the git pre-commit hook"
	@echo "  make setup                Create packaging directories"
	@echo "  make package-skills       Build skill archives"
	@echo "  make package-plugins      Build plugin archives"
	@echo "  make package-all          Build all package archives"
	@echo "  make clean                Remove generated archives"
	@echo
	@echo 'Documentation:    README.md'

setup:
	mkdir -p $(SKILL_ARCHIVE_DIR) $(PLUGIN_ARCHIVE_DIR)

list:
	@echo "Skills:"
	@for pkg in $(SKILLS); do echo "  - $$pkg"; done
	@echo "Plugins:"
	@for pkg in $(PLUGINS); do echo "  - $$pkg"; done

validate: validate-manifests validate-coverage validate-skills validate-agent-docs

# `--strict` treats warnings as errors, and "marketplace has no plugins defined"
# is a warning — so an untouched template would fail. Skip the manifest pass only
# when there is genuinely nothing registered anywhere; the moment a package
# exists on disk, validate-coverage fails loudly if it is missing from the JSON.
validate-manifests:
	@command -v claude >/dev/null || { echo "claude CLI not found; install Claude Code to validate."; exit 1; }
	@entries=$$(python3 -c 'import json;print(len(json.load(open("$(MARKETPLACE_JSON)")).get("plugins") or []))'); \
	if [ "$$entries" -eq 0 ] && [ -z "$(strip $(PLUGINS))" ]; then \
		echo "$(MARKETPLACE_JSON) registers no plugins and $(PLUGINS_DIR)/ is empty — skipping strict manifest validation."; \
		exit 0; \
	fi; \
	claude plugin validate . --strict || exit 1; \
	for pkg in $(PLUGINS); do \
		claude plugin validate "$(PLUGINS_DIR)/$$pkg" --strict || exit 1; \
	done

# The manifest validator never touches the filesystem, so it cannot see an
# unregistered package or a `source` path that points nowhere.
validate-coverage:
	@python3 $(COVERAGE_SCRIPT) \
		--manifest $(MARKETPLACE_JSON) \
		--plugins-dir $(PLUGINS_DIR) \
		--skills-dir $(SKILLS_DIR)

# Nothing else opens a SKILL.md. Every failure this catches is silent at
# runtime -- the skill loads with empty metadata, or never fires at all.
validate-skills:
	@python3 $(FRONTMATTER_SCRIPT) \
		--plugins-dir $(PLUGINS_DIR) \
		--skills-dir $(SKILLS_DIR)

# A stale AGENTS.md is worse than a missing one: an assistant reads it and
# follows rules that were revised months ago.
validate-agent-docs:
	@python3 $(AGENT_DOCS_SCRIPT)

# The checks above catch bad content; these catch a check that has stopped
# catching anything. CI runs both.
test:
	@python3 -m unittest discover -s $(TESTS_DIR) -v

# core.hooksPath points git at the tracked hook directory, so the hook updates
# with the repository instead of being a copy in .git/hooks that goes stale.
install-hooks:
	@git rev-parse --git-dir >/dev/null 2>&1 || { echo "Not a git repository."; exit 1; }
	@git config core.hooksPath $(HOOKS_DIR)
	@chmod +x $(HOOKS_DIR)/* 2>/dev/null || true
	@echo "Installed: core.hooksPath -> $(HOOKS_DIR)"
	@echo "Bypass once with 'git commit --no-verify' or SKIP_SKILL_CHECKS=1."

uninstall-hooks:
	@git config --unset core.hooksPath 2>/dev/null || true
	@echo "Removed: core.hooksPath is unset; git uses .git/hooks again."

$(SKILL_ARCHIVE_DIR)/%.zip: $(SKILLS_DIR)/%
	mkdir -p $(SKILL_ARCHIVE_DIR)
	rm -f $@
	cd $(SKILLS_DIR) && zip -rq "$(abspath $@)" "$(notdir $<)"  $(ZIP_EXCLUDES)

$(PLUGIN_ARCHIVE_DIR)/%.zip: $(PLUGINS_DIR)/%
	mkdir -p $(PLUGIN_ARCHIVE_DIR)
	rm -f $@
	cd $(PLUGINS_DIR) && zip -rq "$(abspath $@)" "$(notdir $<)"  $(ZIP_EXCLUDES)

package-skills: $(SKILL_ARCHIVES)

package-plugins: $(PLUGIN_ARCHIVES)

package-all: package-skills package-plugins

package: package-all

clean:
	rm -rf $(PACKAGES_DIR)
