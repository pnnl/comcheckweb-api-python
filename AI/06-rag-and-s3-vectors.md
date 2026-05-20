# RAG + S3 Vectors: Earlier Discussion

This was the original framing — building an AI tool that uses the
`comcheck_api` package as a knowledge base via RAG, with S3 Vectors as
the store. Captured here for reference. The
[options overview](01-options-overview.md) frames a broader set of
approaches; this document is the deep dive on the RAG-specific path.

## Quick take

Yes, RAG is a reasonable fit, but for **SDK-driven code generation**
the bigger wins come from how the corpus is *structured*, not from the
retriever itself. Pure RAG often returns plausible-looking chunks that
miss the *type contracts* the user needs to compile against. Plan for
a hybrid: a curated "always-in-context" SDK skeleton + RAG for examples
and long-tail details.

## 1. Decide what goes into the knowledge base

Three distinct corpora — chunk and weight each differently:

| Corpus | Source | Purpose | Notes |
|---|---|---|---|
| **Reference (always-on)** | The compact public API surface: `comcheck_api/__init__.py`, `client/`, `project_operations/*`, key types from `types/`, `defaults.py` | Loaded into the system prompt every call | Keep it small (≤ ~10–15k tokens). This is what stops the model from hallucinating method names. |
| **Docs** | `docs_site/**/*.md` + `README.md` + `CHANGELOG.md` | Retrieved on demand | Markdown chunks by `##`/`###` headers. |
| **Examples** | `examples/**/*.py` | Retrieved on demand | Code chunks at function/class granularity — never split mid-function. |

The "reference" corpus is the load-bearing one for code-gen quality.
RAG alone (without it) tends to produce code that uses methods that
don't exist.

## 2. Chunking + embedding

- **Markdown**: split on headings; keep heading path as metadata
  (`# Getting Started > ## Authentication`).
- **Python**: AST-based splitter (e.g., `tree-sitter` or `ast.parse`)
  — one chunk per top-level def/class, with the file's import block
  prepended to each chunk. Don't use a naive character-window splitter
  on code; it cuts method bodies in half and the embeddings come out
  junk.
- **Embedding model**: pick one that's strong on code — Voyage
  `voyage-code-3` is the current best-in-class; OpenAI
  `text-embedding-3-large` is acceptable. Whatever you pick, store the
  model name in metadata so re-indexing on swap is possible.

## 3. S3 Vectors — does it fit?

S3 Vectors is fine for this. The corpus here is small (probably <
5k chunks), so cost/latency aren't the deciding factors. Things to
know:

- **Pros**: cheap at rest, no separate vector DB to operate, ANN built
  in.
- **Cons**: query latency is higher than Pinecone/pgvector (hundreds
  of ms), filtering is more limited than dedicated DBs, and
  re-indexing is your responsibility.
- **Alternative worth a moment's thought**: for a corpus this small,
  embeddings could live in a single Parquet/JSON file and brute-force
  cosine in-process. No infra, faster for < 10k vectors. S3 Vectors
  makes more sense to grow this beyond the SDK (e.g., add
  building-energy-code documents, ASHRAE references, etc.).

If staying with S3 Vectors: one bucket, one index per corpus
(reference/docs/examples), so retrieval can be weighted per corpus.

## 4. Retrieval strategy

- **Hybrid retrieval**: vector + BM25/keyword. Code queries often
  contain exact identifiers ("envelope operation",
  "RunSimulationResponse") that vector search alone underweights.
- **Per-corpus top-k**: e.g., top-3 docs + top-5 example chunks per
  query, rather than top-8 mixed.
- **Re-rank** the merged set with a cross-encoder or with Claude
  itself ("rate these 8 snippets for relevance to the user query")
  before injecting into the final prompt.

## 5. Generation layer

Two architectures, in increasing complexity:

**(a) Single-shot RAG** — query → retrieve → stuff into Claude prompt
→ return code. Simplest. Works if queries are bounded ("build a
project with these 3 envelope assemblies").

**(b) Agentic / tool-using** — Claude gets tools like
`search_docs(query)`, `get_example(name)`, `lookup_type(name)`,
`run_python(code)`. It iterates until the generated code at least
imports cleanly. Higher quality, more complex, more tokens.

For a first version, do (a). Add (b) only if eval shows the model is
missing context it could have fetched.

## 6. Evaluation — don't skip this

Build a small golden set (~20 prompts) like *"Create a project for a
5,000 sqft office in Seattle, WA, with two envelope assemblies and one
HVAC unit"*. For each:

1. Generate code.
2. `python -c` it (no API key needed if the client is mocked).
3. Score: imports succeed → builds object → matches expected
   structure.

This is the only thing that will tell whether the RAG is actually
helping vs. hurting.

## 7. Suggested build order

1. Carve out the "reference" corpus (manually pick which files; ~1
   day).
2. Write the chunker + embedder + S3 Vectors uploader (~1 day).
3. Stand up retrieval + a thin Claude wrapper for generation (~1 day).
4. Build the eval harness with 10–20 prompts (~1 day).
5. Iterate on chunking / retrieval until eval pass-rate plateaus.
