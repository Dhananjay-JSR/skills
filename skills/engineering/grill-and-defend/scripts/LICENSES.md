# Libraries the workspace downloads

`session.py serve` downloads these pinned files from jsDelivr on first run (URLs and SHA-256 in `vendor.json`) and caches them in `~/.cache/grill-workspace`, so the page then works offline. The board's files (React, Excalidraw) are only downloaded when the board is turned on.

| Library | Version | Licence |
|---|---|---|
| React, ReactDOM (UMD) | 18.3.1 | MIT |
| Excalidraw (UMD + assets) | 0.17.6 | MIT (see `excalidraw-assets/vendor-*.LICENSE.txt`) |
| CodeMirror + markdown mode | 5.65.16 | MIT |
| Source Serif 4, Hanken Grotesk, JetBrains Mono (latin woff2) | Fontsource 5.1.0 | SIL Open Font License 1.1 |
| Mermaid (`mermaid.min.js`) | 11.4.1 | MIT |
| marked | 12.0.2 | MIT |
