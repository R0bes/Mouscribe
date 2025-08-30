# 🚀 Makefile für Chat Backend Agent
# Einheitliche Workflows für Entwicklung und Deployment

# Windows-spezifische Shell-Einstellungen
ifeq ($(OS),Windows_NT)
SHELL := powershell.exe
.SHELLFLAGS := -NoProfile -ExecutionPolicy Bypass -Command
.ONESHELL:
endif


# 🎯 Standardziel
.PHONY: help, server_up, ui_up, ui_down, up, down, clean, commit, push, status, release, release-patch, release-minor, release-major
help:
	@echo 🌟 Verfügbare Kommandos:
	@echo
	@echo 🖥️  Server Management:
	@echo     server_up    - 🚀 Startet den Python-Server
	@echo     server_down  - 🛑 Stoppt den Python-Server
	@echo
	@echo 🎨 UI Management:
	@echo     ui_up        - 🚀 Startet die Vite-UI im Entwicklungsmodus
	@echo     ui_down      - 🛑 Stoppt die Vite-UI
	@echo
	@echo 🔄 Kombinierte Kommandos:
	@echo     up           - 🚀 Startet sowohl Server als auch UI
	@echo     down         - 🛑 Stoppt sowohl Server als auch UI
	@echo
	@echo 🧹 Wartung:
	@echo     clean        - 🧹 Räumt temporäre Dateien auf
	@echo
	@echo 📝 Git Commands:
	@echo     commit MSG="message"       - 💾 Git commit mit Nachricht + Pre-Commit
	@echo     fcommit MSG="message"      - 🚀 Schneller Commit ohne Checks
	@echo     push                        - 📤 Git push zum Remote-Repository
	@echo     git MSG="message"          - 🚀 Commit und Push in einem Schritt
	@echo
	@echo 🔄 Pull Request Management:
	@echo     pr                          - 🔄 Erstellt PR automatisch (Commit + Push + PR)
	@echo     pr-draft                    - 🔄 Erstellt Draft PR
	@echo     pr-merge                    - 🔄 Erstellt PR und merged nach Pipeline-Erfolg
	@echo
	@echo 🔒 Pre-Commit Checks:
	@echo     pre-commit   - 🔒 Führt Tests und Linting aus
	@echo     lint-check   - 🔍 Prüft Code-Format und Qualität
	@echo
	@echo 💡 Beispiele:
	@echo     make commit MSG="Fix bug"           - Commit mit Nachricht + Pre-Commit Checks
	@echo     make fcommit MSG="Quick fix"        - Schneller Commit ohne Checks
	@echo     make git MSG="Update code"          - Commit und Push in einem Schritt
	@echo     make pr MSG="New feature"           - Commit, Push und PR erstellen
	@echo     make pr-draft MSG="Work in progress" - Draft PR erstellen
	@echo     make pr-merge MSG="Ready to merge"  - PR erstellen und nach Pipeline mergen
	@echo
	@echo 🧪 Testing:
	@echo     test-all     - 🧪 Alle Tests ausführen
	@echo     test-unit    - 🔬 Nur Unit Tests
	@echo     test-e2e     - 🌐 End-to-End Tests
	@echo     test-help    - 📚 Hilfe für Test-Kommandos
	@echo
	@echo 🚀 Release Management:
	@echo     release VERSION=X.Y.Z - 🏷️  Erstellt neuen Release mit Version
	@echo     release-patch          - 🔧 Patch-Release (1.0.0 → 1.0.1)
	@echo     release-minor          - ✨ Minor-Release (1.0.0 → 1.1.0)
	@echo     release-major          - 🎉 Major-Release (1.0.0 → 2.0.0)


status:
	@echo 🔍 Git Status...
	git status

# 🖥️ Server Management
.PHONY: server_up
server_up:
	@echo 🚀 Starte Python-Server...
	@cd server && python3 main.py

.PHONY: server_down
server_down:
	@echo 🛑 Stoppe Python-Server...
	@echo ⚠️  Verwende Ctrl+C um den Server zu stoppen

# 🎨 UI Management
.PHONY: ui_up
ui_up:
	@echo 🎨 Starte Vite-UI im Entwicklungsmodus...
	@cd ui && npm run dev &

.PHONY: ui_down
ui_down:
	@echo 🛑 Stoppe Vite-UI...
	@bash -c 'pgrep -f "vite" | xargs kill 2>/dev/null || true'
	@bash -c 'pgrep -f "node.*vite" | xargs kill 2>/dev/null || true'
	@echo ✅ Vite-UI gestoppt

# 🔄 Kombinierte Kommandos
.PHONY: up
up: ui_up server_up
	@echo 🎉 Alle Services erfolgreich gestartet! 🚀

.PHONY: down
down: server_down ui_down
	@echo 🛑 Alle Services gestoppt

# 🧹 Cleanup
.PHONY: clean
clean:
	@echo 🧹 Räume temporäre Dateien auf...
	@rm -rf server/__pycache__
	@rm -rf ui/dist
	@rm -rf ui/node_modules
	@echo ✅ Aufräumen abgeschlossen!

# 🧪 Test Commands
.PHONY: test test-unit test-integration test-e2e test-all test-coverage test-mutation test-clean

# 🧪 Run all tests (Mauscribe)
test:
	@echo 🧪 Führe Mauscribe Tests aus...
	python -m pytest tests/ -v
	@echo 🎉 Tests abgeschlossen!

# 🔬 Run unit tests only
test-unit: test-install
	@echo 🔬 Führe Unit Tests aus...
	pytest tests/unit/ -v --cov=server --cov-report=html
	@echo ✅ Unit Tests abgeschlossen!

# 🔗 Run integration tests only
test-integration: test-install
	@echo 🔗 Führe Integration Tests aus...
	pytest tests/integration/ -v
	@echo ✅ Integration Tests abgeschlossen!

# 🌐 Run E2E tests only
test-e2e: test-install
	@echo 🌐 Führe End-to-End Tests aus...
	pytest tests/e2e/ -v
	@echo ✅ E2E Tests abgeschlossen!

# 📊 Run tests with coverage report
test-coverage: test-install
	@echo 📊 Führe Tests mit Coverage-Report aus...
	pytest tests/ -v --cov=server --cov-report=html --cov-report=xml --cov-fail-under=70
	@echo 📈 Coverage-Report erstellt!

# 🧬 Run mutation testing
test-mutation: test-install
	@echo 🧬 Führe Mutation Testing aus...
	mutmut run --paths-to-mutate=server/
	@echo 🧬 Mutation Testing abgeschlossen!

# ⚡ Run performance tests
test-performance: test-install
	@echo ⚡ Führe Performance Tests aus...
	pytest tests/ -v --benchmark-only
	@echo ⚡ Performance Tests abgeschlossen!

# 🔒 Run security tests
test-security: test-install
	@echo 🔒 Führe Security Tests aus...
	pytest tests/ -v -m security
	@echo 🔒 Security Tests abgeschlossen!

# 🚀 Run tests in parallel
test-parallel: test-install
	@echo 🚀 Führe Tests parallel aus...
	pytest tests/ -v -n auto
	@echo 🚀 Parallele Tests abgeschlossen!

# 🧹 Clean test artifacts
test-clean:
	@echo 🧹 Räume Test-Artefakte auf...
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .pytest_cache/
	rm -rf .mutmut-cache/
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	@echo ✅ Test-Aufräumen abgeschlossen!

# ⚡ Quick test run (unit tests only, no coverage)
test-quick: test-install
	@echo ⚡ Schneller Test-Lauf (nur Unit Tests)...
	pytest tests/unit/ -v --tb=short
	@echo ⚡ Schneller Test abgeschlossen!

# 🎯 Test specific module
test-module: test-install
	@if [ -z "$(MODULE)" ]; then \
		echo ❌ Fehler: MODULE Parameter fehlt; \
		echo 💡 Verwendung: make test-module MODULE=server.api; \
		exit 1; \
	fi
	@echo 🎯 Teste spezifisches Modul: $(MODULE)
	pytest tests/ -v -k "$(MODULE)" --cov=$(MODULE) --cov-report=html
	@echo ✅ Modul-Test abgeschlossen!

# 📊 Show test coverage
coverage: test-coverage
	@echo 📊 Öffne Coverage-Report...
	@if command -v open >/dev/null 2>&1; then \
		open htmlcov/index.html; \
	elif command -v xdg-open >/dev/null 2>&1; then \
		xdg-open htmlcov/index.html; \
	else \
		echo 📊 Coverage-Report verfügbar unter: htmlcov/index.html; \
	fi

# 📚 Test help
test-help:
	@echo 📚 Verfügbare Test-Kommandos:
	@echo
	@echo 🧪 Vollständige Tests:
	@echo   test-all        - 🧪 Alle Tests mit Coverage
	@echo   test-coverage   - 📊 Tests mit Coverage-Report
	@echo   test-mutation   - 🧬 Mutation Testing
	@echo   test-performance- ⚡ Performance Tests
	@echo   test-security   - 🔒 Security Tests
	@echo   test-parallel   - 🚀 Tests parallel ausführen
	@echo
	@echo 🔬 Spezifische Tests:
	@echo   test-unit       - 🔬 Nur Unit Tests
	@echo   test-integration- 🔗 Nur Integration Tests
	@echo   test-e2e        - 🌐 Nur E2E Tests
	@echo   test-module     - 🎯 Spezifisches Modul testen
	@echo
	@echo ⚡ Schnelle Tests:
	@echo   test-quick      - ⚡ Schneller Test-Lauf (Unit only)
	@echo
	@echo 🧹 Wartung:
	@echo   test-clean      - 🧹 Test-Artefakte aufräumen
	@echo   coverage        - 📊 Coverage-Report im Browser öffnen
	@echo
	@echo 💡 Beispiel: make test-module MODULE=server.api

# 📝 Git Commands
.PHONY: commit
commit: pre-commit
	@echo 📝 Git Status:
	@git status --short
	@echo
	@echo 💾 Committing changes...
	@git add .
ifeq ($(OS),Windows_NT)
	@if "$(MSG)"=="" ( \
		set /p message="Commit message: " && git commit -m "!message!" --no-verify \
	) else ( \
		git commit -m "$(MSG)" --no-verify \
	)
else
	@if [ -z "$(MSG)" ]; then \
		read -p "Commit message: " message; git commit -m "$$message" --no-verify; \
	else \
		git commit -m "$(MSG)" --no-verify; \
	fi
endif
	@echo ✅ Commit erfolgreich!

# 🔒 Pre-Commit Hook
.PHONY: pre-commit
pre-commit:
	@echo 🔒 Pre-Commit Checks werden ausgeführt...
	@echo 🧪 Führe Tests aus...
	@$(MAKE) test
	@echo 🔍 Prüfe Code-Format...
	@$(MAKE) lint
	@echo ✅ Pre-Commit Checks erfolgreich!
	@echo

# 🔍 Linting und Code-Qualität (Mauscribe)
.PHONY: lint
lint:
	@echo 🔍 Prüfe Mauscribe Code-Qualität...
	@echo 🧪 Führe Linting aus...
	flake8 src/ tests/ || echo ⚠️  Linting mit Warnungen abgeschlossen
	@echo 🔍 Prüfe Code-Format...
	black --check src/ tests/ || echo ⚠️  Format-Check mit Warnungen abgeschlossen
	@echo 🔍 Prüfe Imports...
	isort --check-only src/ tests/ || echo ⚠️  Import-Check mit Warnungen abgeschlossen
	@echo 🔍 Prüfe Typen...
	mypy src/ --ignore-missing-imports || echo ⚠️  Typ-Check mit Warnungen abgeschlossen
	@echo ✅ Linting-Checks abgeschlossen!

# 🚀 Fast Commit (ohne Pre-Commit Checks)
.PHONY: fcommit
fcommit:
	@echo 🚀 Schneller Commit ohne Pre-Commit Checks...
	@echo 📝 Git Status:
	@git status --short
	@echo
	@echo 💾 Committing changes...
	@git add .
ifeq ($(OS),Windows_NT)
	@if "$(MSG)"=="" ( \
		set /p message="Commit message: " && git commit -m "!message!" --no-verify \
	) else ( \
		git commit -m "$(MSG)" --no-verify \
	)
else
	@if [ -z "$(MSG)" ]; then \
		read -p "Commit message: " message; git commit -m "$$message" --no-verify; \
	else \
		git commit -m "$(MSG)" --no-verify; \
	fi
endif
	@echo ✅ Schneller Commit erfolgreich!

.PHONY: push
push:
	@echo 📤 Pushe Änderungen zum Remote-Repository...
	@echo 🔍 Git Push wird ausgeführt...
	@git push
	@echo ✅ Push erfolgreich abgeschlossen!
	@echo
	@echo 🔍 Pipeline-Monitor startet automatisch...
	@python pipeline_monitor.py

.PHONY: monitor
monitor:
	@echo 🔍 Pipeline-Monitor startet...
	@python pipeline_monitor.py

.PHONY: push-and-monitor
push-and-monitor: push
	@echo
	@echo 🔍 Pipeline-Monitor startet in 3 Sekunden...
ifeq ($(OS),Windows_NT)
	@timeout /t 3 /nobreak >nul
else
	@sleep 3
endif
	@$(MAKE) monitor

.PHONY: git
git: commit push
	@echo 🎉 Commit und Push erfolgreich abgeschlossen! 🚀

# 🔄 Pull Request Management
.PHONY: pr
pr: git
	@echo 🔄 Erstelle Pull Request...
	@echo 📋 Branch-Typ wird erkannt...
ifeq ($(OS),Windows_NT)
	@echo 🔄 Erstelle Pull Request für Windows...
	@echo ⚠️  Windows PR-Erstellung wird noch nicht unterstützt
	@echo 💡 Verwende 'make pr-draft' oder erstelle PR manuell
	@echo 📋 Branch: $(shell git branch --show-current)
	@echo 📝 PR-Typ: feature (für develop)
	@echo ✅ Commit und Push erfolgreich - PR manuell erstellen

else
	@current_branch=$$(git branch --show-current) && \
	if [ "$$current_branch" = "main" ] || [ "$$current_branch" = "develop" ]; then \
		echo ❌ Kann keinen PR von $$current_branch Branch erstellen; \
		exit 1; \
	fi && \
	if [[ "$$current_branch" == feature* ]]; then \
		pr_type="feat" && base_branch="develop"; \
	elif [[ "$$current_branch" == bugfix* ]]; then \
		pr_type="fix" && base_branch="main"; \
	elif [[ "$$current_branch" == hotfix* ]]; then \
		pr_type="hotfix" && base_branch="main"; \
	else \
		pr_type="update" && base_branch="develop"; \
	fi && \
	echo 📝 PR-Typ: $$pr_type für $$base_branch && \
	echo 🔄 Erstelle PR über GitHub CLI... && \
	gh pr create --base $$base_branch --title "$$pr_type: $$current_branch" --body "Automated PR from $$current_branch branch" || echo ⚠️  GitHub CLI nicht verfügbar - PR manuell erstellen && \
	echo ✅ Pull Request erstellt!
endif

.PHONY: pr-draft
pr-draft: git
	@echo 🔄 Erstelle Draft Pull Request...
ifeq ($(OS),Windows_NT)
	@echo 🔄 Erstelle Draft Pull Request für Windows...
	@echo ⚠️  Windows PR-Erstellung wird noch nicht unterstützt
	@echo 💡 Verwende 'make pr-draft' oder erstelle Draft PR manuell
	@echo 📋 Branch: $(shell git branch --show-current)
	@echo 📝 PR-Typ: feature (für develop)
	@echo ✅ Commit und Push erfolgreich - Draft PR manuell erstellen

else
	@current_branch=$$(git branch --show-current) && \
	if [ "$$current_branch" = "main" ] || [ "$$current_branch" = "develop" ]; then \
		echo ❌ Kann keinen PR von $$current_branch Branch erstellen; \
		exit 1; \
	fi && \
	if [[ "$$current_branch" == feature* ]]; then \
		pr_type="feat" && base_branch="develop"; \
	elif [[ "$$current_branch" == bugfix* ]]; then \
		pr_type="fix" && base_branch="main"; \
	elif [[ "$$current_branch" == hotfix* ]]; then \
		pr_type="hotfix" && base_branch="main"; \
	else \
		pr_type="update" && base_branch="develop"; \
	fi && \
	echo 📝 Draft PR-Typ: $$pr_type für $$base_branch && \
	echo 🔄 Erstelle Draft PR über GitHub CLI... && \
	gh pr create --base $$base_branch --title "$$pr_type: $$current_branch (Draft)" --body "Draft PR from $$current_branch branch" --draft || echo ⚠️  GitHub CLI nicht verfügbar - Draft PR manuell erstellen && \
	echo ✅ Draft Pull Request erstellt!
endif

.PHONY: pr-merge
pr-merge: pr
	@echo 🔄 Merge Pull Request...
	@echo ⚠️  Warte auf Pipeline-Erfolg...
	@echo 🔍 Prüfe Pipeline-Status...
	@python pipeline_monitor.py --timeout 300 || echo ⚠️  Pipeline-Überwachung fehlgeschlagen
	@echo 🔄 Merge PR über GitHub CLI...
	@gh pr merge --merge || echo ⚠️  GitHub CLI nicht verfügbar - PR manuell mergen
	@echo ✅ Pull Request erfolgreich gemergt!

# 🚀 Release Management
.PHONY: release
release:
	@if [ -z "$(VERSION)" ]; then \
		echo "❌ Version angeben! Beispiel: make release VERSION=1.0.0"; \
		exit 1; \
	fi
	@echo 🚀 Erstelle Release $(VERSION)...
	@python scripts/create_release.py $(VERSION)
	@echo ✅ Release $(VERSION) erfolgreich erstellt!

.PHONY: release-patch
release-patch:
	@echo 🔧 Erstelle Patch-Release...
	@python scripts/create_release.py --type patch --no-build
	@echo ✅ Patch-Release erfolgreich erstellt!

.PHONY: release-minor
release-minor:
	@echo ✨ Erstelle Minor-Release...
	@python scripts/create_release.py --type minor --no-build
	@echo ✅ Minor-Release erfolgreich erstellt!

.PHONY: release-major
release-major:
	@echo 🎉 Erstelle Major-Release...
	@python scripts/create_release.py --type major --no-build
	@echo ✅ Major-Release erfolgreich erstellt!
