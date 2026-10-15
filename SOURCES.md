<!-- SPDX-License-Identifier: CC-BY-4.0 -->
<!-- Copyright © 2026 Isto Hunttila -->

# Source Management

Register every research source.

| Field | Description |
|---|---|
| Source ID | Stable unique identifier |
| Publisher | Manufacturer or standards body |
| Product | Product and model, if applicable |
| Document | Exact document title |
| Version | Document revision or issue date |
| URL | Original source address |
| Retrieved | Retrieval date (ISO 8601) |
| SHA-256 | File checksum, if downloaded |
| License | Copyright and permitted reuse |
| Storage | Local path or external reference |

## Source policy
- Prefer official primary sources.
- Preserve document revisions where legally permitted; never silently overwrite.
- Record dead URLs and replacement locations.
- Cite exact pages, tables or sections in derived findings.
- Keep copyrighted or restricted materials outside the public repository unless redistribution is authorized.
- Maintain machine-readable source registry entries under `sources/`.
