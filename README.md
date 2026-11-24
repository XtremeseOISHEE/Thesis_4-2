# Multi-Hop Explainable AI for Clinical Decision Support

Research prototype exploring clinical reasoning with retrieval-augmented generation and guideline verification at each reasoning step.

**[Live Streamlit demo](https://thesis4-2git-bdtpsgjip26eytq4wfqwbf.streamlit.app/)** · [Frontend notes](FRONTEND_README.md)

## What it does

- Routes a clinical case to a condition-specific reasoning pipeline.
- Retrieves guideline passages from ChromaDB.
- Produces identification, diagnostic-confirmation and management reasoning hops.
- Assigns SUPPORTED, PARTIAL or UNSUPPORTED verdicts with verification explanations.
- Displays cached showcase cases and a live note-analysis interface in Streamlit.

The repository also contains comparison systems and scripts for routing, out-of-scope behavior, evidence support and reasoning-depth experiments. A guideline-support verdict is not proof that a diagnosis or treatment is correct.

## Research status

Student researcher and primary prototype developer: **Asma-Ul-Husna Oishee**, Jahangirnagar University. Supervisor: **Dr. Md. Ezharul Islam**.

**Ongoing research prototype — further system, evaluation and documentation updates are planned.** A first-author journal manuscript is in preparation. This is an experimental research system, not a clinically validated tool or a substitute for clinical judgment. Do not submit identifiable patient notes to the public demo.

## Repository map

| Path | Purpose |
| --- | --- |
| `App/app.py` | Streamlit interface |
| `App/showcase_cache.json` | Cached showcase traces |
| `system_c/` | Retrieval, LLM connector, reasoning and verification |
| `system_c/system_a.py`, `system_b.py`, `system_c.py` | Comparison pipelines |
| `system_c/run_experiment_e*.py` | Experiment scripts |
| `build_knowledge_base.py` | Builds the guideline collection |
| `cases/`, `cases_v2/`, `cases_oos/` | Case collections |
| `results_*.csv` | Saved experimental outputs |

## Local setup — current portability limitations

Setup below is a starting point based on source inspection, not a freshly reproduced installation. No pinned dependency file is currently supplied.

1. Clone this repository and create a Python virtual environment.
2. Install the main dependencies:

   ```powershell
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   python -m pip install streamlit openai chromadb sentence-transformers pandas
   ```

   Some exploratory/provider-specific scripts may need additional packages. Record tested package versions before claiming reproducibility.

3. Adapt the existing machine-specific paths before running. In particular:
   - `system_c/llm_connector.py`: the constructor defaults to a local `openrouter_key.txt` file.
   - `system_c/knowledge_base.py` and `build_knowledge_base.py`: ChromaDB directory.
   - `system_c/data_loader.py`: default case directory.
   - `system_c/system_c.py` and experiment scripts: local import/data paths.

   Keep the API key outside version control. Merely defining an environment variable will not replace the current key-file code; adjust the connector if adopting environment variables or Streamlit secrets.

4. Configure your own OpenRouter access. The inspected connector uses the OpenAI-compatible OpenRouter endpoint with `openai/gpt-oss-120b`; provider availability, cost and quotas may change.
5. If a fresh evidence store is needed, review `build_knowledge_base.py`, update its destination and run it. **It deletes/recreates the `clinical_guidelines` collection at that destination**; do not point it at a store you need to preserve.
6. Start from the repository root:

   ```powershell
   streamlit run App/app.py
   ```

The app derives its root from its own location. The older frontend notes describe a root-level app file; the current tracked entry point is `App/app.py`.

## Evaluation and evidence limits

- Saved outputs are research artifacts, not independent replication.
- Cached showcases demonstrate saved behavior; they are not new live evaluation results.
- Case-source permissions, redistribution rights and guideline attribution/versioning need explicit documentation.
- Model behavior and automatic evidence verification can be wrong.
- Data/model paths, dependency pinning and a reproducible experiment guide remain follow-up work.

This README documents the current prototype; it does not claim that the portability issues above have been fixed.
