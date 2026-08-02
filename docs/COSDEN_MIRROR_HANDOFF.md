# CosDen Mirror Handoff

## Active goal

```text
goal_id: COSDEN-SINGLE-SCHEDULER-001
goal: make StegVerse-Labs/StegVerse-Healer the sole approved scheduler for CosDen automation while preserving canonical CosDen ownership in StegDB and preventing obsolete workflow noise
repository: StegVerse-Labs/CosDen
branch: main
state: DISCOVERY_REQUIRED
```

## Authoritative files

```text
README.md
docs/COSDEN_MIRROR_HANDOFF.md
StegVerse-Labs/StegVerse-Healer/docs/HEALER_MIRROR_HANDOFF.md
StegVerse-Labs/StegVerse-Healer/data/orchestrator_targets.json
StegVerse-Labs/StegDB/STEGDB_MIRROR_HANDOFF.md
StegVerse-Labs/StegDB/docs/architecture/decisions/CosDen-Submodule-Retirement-v1.md
StegVerse-Labs/StegDB/tools/export_cosden_canonical.py
StegVerse-Labs/StegDB/canonical/cosden/tools/validate_cosden_structure.py
```

## Current repository classification

- `README.md`: implemented documentation, but not proof of an operating ingestion or synchronization path.
- Repository-local scheduler/orchestrator: not yet verified.
- Repository-local workflow inventory: not yet verified because code search returned no indexed workflow results.
- Canonical CosDen source and export logic: apparently owned by `StegVerse-Labs/StegDB`; this must be confirmed from the StegDB handoff and retirement decision before any duplicate implementation is created.
- Existing Healer target: disabled placeholder pointing to a nonexistent `ingestion-orchestrator.yml`; must remain disabled until a real entrypoint is verified.

## Completed work and evidence

- Repository access and default branch `main` verified through the GitHub repository API.
- Existing README inspected and confirmed to describe a broad product vision rather than a production ingestion contract.
- Repository search found no applicable `*_MIRROR_HANDOFF.md`; this file is therefore the first authoritative CosDen continuation record.
- Organization search found canonical CosDen export and validation ownership in `StegVerse-Labs/StegDB`:
  - `tools/export_cosden_canonical.py`
  - `scripts/export_cosden_canonical.py`
  - `canonical/cosden/tools/validate_cosden_structure.py`
  - `docs/architecture/decisions/CosDen-Submodule-Retirement-v1.md`

## Incomplete work

1. Read `StegVerse-Labs/StegDB/STEGDB_MIRROR_HANDOFF.md` and the CosDen retirement decision.
2. Determine whether CosDen is a retired mirror, a generated destination, or an independently active repository.
3. Enumerate the actual CosDen `.github/workflows/*.yml` and `.yaml` files through repository API-visible paths or exact known paths.
4. Inspect every discovered workflow, script, secret reference, artifact, mutation path, and schedule.
5. Identify the single retained event-driven entrypoint, if one exists.
6. If no repository-local workflow is required, remove CosDen from ordinary dispatch targets and represent it as a StegDB-owned generated destination instead.
7. If a real CosDen entrypoint is required, install or adapt it without duplicating StegDB canonical authority.
8. Add deterministic validation and a machine-readable migration receipt.

## Exact next tasks and locations

```text
StegVerse-Labs/StegDB/STEGDB_MIRROR_HANDOFF.md
  -> confirm canonical ownership and continuation rules

StegVerse-Labs/StegDB/docs/architecture/decisions/CosDen-Submodule-Retirement-v1.md
  -> determine whether repository-local automation is obsolete or retained

StegVerse-Labs/CosDen/.github/workflows/
  -> inventory exact workflow files and local schedules

StegVerse-Labs/StegVerse-Healer/data/orchestrator_targets.json
  -> keep CosDen disabled until a real entrypoint or generated-destination contract is verified

StegVerse-Labs/StegVerse-Healer/data/summary/single_scheduler_migration.json
  -> add CosDen classification and evidence after discovery
```

## Blockers

- Canonical ownership has not yet been reconciled with StegDB.
- No repository-local workflow entrypoint has been directly verified.
- No hosted run, artifact, or synchronization receipt has been inspected.

Machine-observable release condition: the StegDB handoff and retirement decision establish the intended CosDen ownership model, and every active CosDen workflow path is either verified event-driven, centrally scheduled through Healer, or durably classified obsolete/superseded.

## Machine-owned tasks

- Owner: `StegVerse-Labs/StegVerse-Healer` for scheduler policy, audit, and migration receipt.
- Owner: `StegVerse-Labs/StegDB` for canonical CosDen export and structural validation.
- Owner: `StegVerse-Labs/CosDen` for repository-local handoff accuracy and any retained destination workflow.

Automation states must use: `COMPLETE`, `BLOCKED`, `RETRY`, `REVIEW_REQUIRED`, or `FAILED`.

## Cross-repository dependencies

```text
source authority: StegVerse-Labs/StegDB
scheduler authority: StegVerse-Labs/StegVerse-Healer
candidate destination: StegVerse-Labs/CosDen
publication propagation: not authorized or verified
Site propagation: not authorized or verified
Publisher propagation: not authorized or verified
wiki propagation: not authorized or verified
master-records custody: not identified for this migration
```

## Validation commands

```text
python -m json.tool StegVerse-Labs/StegVerse-Healer/data/orchestrator_targets.json
python -m py_compile StegVerse-Labs/StegDB/tools/export_cosden_canonical.py
python StegVerse-Labs/StegDB/canonical/cosden/tools/validate_cosden_structure.py
# YAML parse every discovered CosDen workflow
# Assert no unauthorized `schedule:` remains outside Healer
# Verify any retained dispatch target exists and accepts workflow_dispatch
```

No validation result is claimed until these commands or equivalent hosted checks are directly observed.

## Archive conditions

This task becomes archivable only when canonical ownership, workflow inventory, retained entrypoint or generated-destination posture, schedule migration, validation evidence, and machine-owned continuation state are all durable and no unique session context remains.

## Progress

```text
developed_files: 1/4 required migration records
scaffolding_or_stubs: 1 Healer placeholder target
missing_required_files: 2 (verified destination contract, machine-readable migration receipt)
developed_files_percentage: 25%
goal_activation_percentage: 10%
```
