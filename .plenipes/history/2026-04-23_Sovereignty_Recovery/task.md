# Task List: Sovereignty Recovery & Logic Hardening

- [ ] **Phase 1: Logic Restoration**
    - [ ] Restore `generate_slug` and `generate_seo_metadata` in `ai_base.py`
    - [ ] Restore full implementation in `ai_openai.py`
    - [ ] Update specialized adapters with stubs if needed
- [ ] **Phase 2: Configuration Expansion**
    - [ ] Add `custom_prompts` and `global_proxy` to `config.yaml`
    - [ ] Update `configs/ai_providers.yaml` with proxy examples
    - [ ] Add `watchdog_settings` to `config.yaml`
- [ ] **Phase 3: Governance & Guarding**
    - [ ] Add Rule 12.8 to `rules.md`
    - [ ] Implement `check_mandatory_logic` in `code_checks.py`
    - [ ] Run `governance_audit.py` to verify the guard
- [ ] **Phase 4: Verification**
    - [ ] Run `autonomous_simulation.py`
    - [ ] Final compliance check
