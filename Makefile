TAGS_FILE = .tags
COMPOSE_RUN = docker compose run --rm -it --quiet-build

bash: 					# Run bash inside `main` container
	$(COMPOSE_RUN) main bash

build: 					# Build containers
	docker compose build

clean:					# Remove build/dist files
	rm -rf build dist

cloc:					# Count lines of code
	cloc .

container-clean: 		# Clean orphan containers
	docker compose down -v --remove-orphans

help:					# List all make commands
	@awk -F ':.*#' '/^[a-zA-Z_ -]+:.*?#/ { printf "\033[36m%-15s\033[0m %s\n", $$1, $$2 }' $(MAKEFILE_LIST) | sort

kill:					# Force stop (kill) and remove containers
	docker compose kill
	docker compose rm --force

lint:					# Run linter script inside `main` container
	$(COMPOSE_RUN) main /app/scripts/lint.sh

shell:					# Execute IPython inside `main` container
	$(COMPOSE_RUN) main ipython

tags:					# Generate tags file for the entire project (requires universal-ctags)
	@git ls-files | ctags -L - --tag-relative=yes --quiet --append -f "$(TAGS_FILE)"

test:					# Execute `pytest` inside `main` container
	$(COMPOSE_RUN) main pytest --doctest-modules $(TEST_ARGS) .

.PHONY:	bash build clean cloc container-clean help kill lint shell tags test
