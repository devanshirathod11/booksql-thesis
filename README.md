# Banking Conversational Text-to-SQL Using Open-Source LLMs

> Research project focused on natural-language access to structured banking/enterprise data using open-source large language models. This README is an initial documentation baseline derived from the project owner's resume; implementation details and experimental results must be verified against the repository code and experiment artifacts before being treated as reproducible.

## Problem

Relational databases can be difficult for non-technical users to query directly. Text-to-SQL systems translate natural-language questions into SQL, but accuracy depends on schema understanding, query complexity, data quality, and the model's ability to generate executable SQL.

## Project Scope

The project owner's resume describes work on:

- A Python-based Text-to-SQL system using open-source LLMs, including LLaMA 7B and Mistral 7B.
- Dataset curation and preprocessing, including structured query/SQL pairs and schema consistency.
- Comparison of zero-shot and fine-tuned model performance.
- Evaluation using SQL execution accuracy, schema alignment, and semantic correctness.
- Prompt engineering and instruction-style formatting for structured query generation.
- Retrieval-Augmented Generation (RAG) pipelines for document and tabular data using OCR, embeddings, and vector search, including pgvector and Milvus.
- Database migration and normalization workflows from SQL Server/Azure Data Studio to PostgreSQL.

These bullets describe the reported project scope; the exact mapping of each capability to this repository should be checked against its code before release.

## Intended System Workflow

The following is a conceptual workflow based on the project description, not a verified diagram of the current implementation:

1. **Question input** — receive a natural-language question.
2. **Context preparation** — retrieve or provide relevant schema, column descriptions, and domain terminology where implemented.
3. **SQL generation** — prompt the selected open-source LLM to generate SQL.
4. **Validation** — check SQL syntax and schema references; apply execution safeguards before running queries.
5. **Execution and evaluation** — compare generated queries against a benchmark or expected outputs using the verified evaluation harness.
6. **Error analysis** — categorize failures such as incorrect joins, filters, aggregations, schema references, or invalid SQL.

## Evaluation Plan

Document the exact benchmark, data split, prompt format, model versions, decoding parameters, and execution environment before comparing results.

Recommended metrics, where supported by the implementation:

- **Execution accuracy:** proportion of queries whose execution result matches the reference under the defined evaluator.
- **Schema alignment:** correctness of table and column references.
- **Semantic correctness:** whether the generated SQL answers the intended question.
- **Latency:** time required for generation and evaluation.
- **Failure categories:** invalid SQL, wrong joins, wrong filters, aggregation errors, and other observed failures.

No numerical Text-to-SQL result is asserted in this README because the corresponding experiment outputs were not available during this documentation pass.

## Repository Setup

The current repository tree and dependency files could not be verified through the available file inspection interface. Add the exact environment setup, data preparation steps, model download instructions, and run commands here after confirming the actual scripts and dependencies.

Do not commit credentials, private banking data, proprietary schemas, or datasets without authorization. Keep large datasets and model checkpoints out of Git unless their distribution terms and repository strategy explicitly permit them.

## Reproducibility Checklist

- [ ] Identify the project entry point and module layout.
- [ ] Add pinned dependencies and tested Python/CUDA versions, if applicable.
- [ ] Document benchmark source, dataset version, and split.
- [ ] Document model checkpoints, quantization, and inference settings.
- [ ] Provide a safe example schema and synthetic example question.
- [ ] Add automated tests for SQL generation and validation.
- [ ] Record zero-shot and fine-tuned results with exact evaluation commands.
- [ ] Include limitations, known failure cases, and hardware requirements.

## Research Context

This project is part of the broader goal of building reliable conversational interfaces to structured data. The key engineering challenge is not merely producing SQL-shaped text, but generating queries that are schema-aware, executable, safe, and semantically aligned with the user's intent.
