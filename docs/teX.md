# teX.md — LaTeX / MacTeX reference

A pragmatic cheat-sheet for writing formal documents (manuscripts, supplements, figures) in this repo. Opinionated; modern best practices only. Five sections:

1. [Toolchain (MacTeX)](#toolchain-mactex)
2. [Document structure & formatting](#document-structure--formatting)
3. [Math, figures, and tables](#math-figures-and-tables)
4. [Bibliography & citations](#bibliography--citations)
5. [Errors, pitfalls, and debugging](#errors-pitfalls-and-debugging)

---

## Toolchain (MacTeX)

### What MacTeX is

MacTeX is the macOS distribution of **TeX Live** (the upstream cross-platform TeX system) packaged as a `.pkg` installer with Mac-native GUI apps (TeXShop, BibDesk, LaTeXiT, TeX Live Utility). MacTeX = TeX Live + GUI extras. **BasicTeX** is the slim variant (~100 MB vs ~7 GB) — just the engines and `tlmgr`; you install the rest of CTAN on demand.

### Install / update

Direct `.pkg` from tug.org/mactex is canonical. Homebrew works too:

```sh
brew install --cask mactex            # full distribution, with GUI apps
brew install --cask mactex-no-gui     # full TeX Live, no TeXShop/BibDesk
brew install --cask basictex          # minimal; install packages via tlmgr
```

To update year-over-year, reinstall the cask or `.pkg`. For package-level updates within a release, use `tlmgr`.

### PATH gotcha

MacTeX installs binaries to `/Library/TeX/texbin` (a symlink to the active TeX Live year). The installer adds this to `/etc/paths.d/TeX`, but **already-open shells will not see it** — open a new terminal, or:

```sh
eval "$(/usr/libexec/path_helper)"
which pdflatex   # should print /Library/TeX/texbin/pdflatex
```

### `tlmgr` — the TeX Live package manager

On macOS the system-wide tree is owned by root, so installs/updates need `sudo`. (BasicTeX in particular ships almost nothing.)

```sh
sudo tlmgr update --self --all        # update tlmgr itself, then all packages
sudo tlmgr install latexmk siunitx    # install named packages
tlmgr search --global --file foo.sty  # which package provides foo.sty?
tlmgr info <pkg>                      # description, dependencies, install status
```

If `tlmgr` errors with "cannot setup TLPDB," the mirror is stale: `sudo tlmgr option repository ctan` then retry.

### Engines: pdflatex vs xelatex vs lualatex

| Engine | Use when |
|---|---|
| **pdflatex** | Default. Fastest. Legacy `.tfm` fonts (Computer Modern, Latin Modern). Full `microtype` (protrusion + font expansion). No system fonts, no native UTF-8 input beyond `inputenc`. |
| **xelatex** | You need **system fonts** (`\setmainfont{...}` via `fontspec`) or non-Latin scripts. Native UTF-8. `microtype` works but **font expansion is unavailable** — protrusion only. |
| **lualatex** | Same Unicode + `fontspec` benefits as XeLaTeX, plus embedded Lua. Full `microtype`. Slower than pdflatex. Pick this for new projects needing modern fonts. |

Rule of thumb: stay on pdflatex unless a font or Unicode requirement forces you off. If forced off, prefer lualatex over xelatex for the better microtype support.

### Building from the terminal

`latexmk` is the standard one-shot tool — handles the multi-pass dance (LaTeX → BibTeX/Biber → LaTeX → LaTeX) automatically.

```sh
latexmk -pdf foo.tex          # build PDF via pdflatex
latexmk -xelatex foo.tex      # use xelatex
latexmk -lualatex foo.tex     # use lualatex
latexmk -pdf -pvc foo.tex     # watch mode: rebuild + refresh viewer on save
latexmk -c                    # clean aux files (keep PDF)
latexmk -C                    # clean everything including PDF
```

Project defaults live in `./.latexmkrc` (or `~/.latexmkrc`):

```perl
$pdf_mode = 1;          # 1=pdflatex, 4=lualatex, 5=xelatex
$pdflatex = 'pdflatex -synctex=1 -interaction=nonstopmode -file-line-error %O %S';
$bibtex_use = 2;        # run biber/bibtex as needed
```

### Editors

- **TeXShop** — ships with MacTeX. Lightweight, Mac-native, good default.
- **TeXworks** — also bundled; cross-platform, minimal.
- **VS Code + LaTeX Workshop extension** — best modern option; reuses `latexmk`, gives live preview, SyncTeX, snippets, linting.
- **Overleaf** — browser; useful for collaboration or when you don't want a local toolchain.

### Quick recipe: build a paper from the terminal

```sh
# one-time
brew install --cask mactex-no-gui
sudo tlmgr update --self --all

# per project
cd paper/
printf '$pdf_mode = 1;\n$bibtex_use = 2;\n' > .latexmkrc
latexmk -pdf -pvc main.tex     # leave running; edits rebuild automatically
# when done:
latexmk -c
```

---

## Document structure & formatting

### Minimal skeleton

```latex
\documentclass[11pt]{article}
\usepackage[T1]{fontenc}      % proper hyphenation, copy-paste-safe PDFs
\usepackage{microtype}        % subtle but always-on quality boost
\usepackage[margin=1in]{geometry}
\usepackage{hyperref}         % load last (or near-last)

\title{A Title}
\author{Author Name}
\date{\today}

\begin{document}
\maketitle
% content
\end{document}
```

That is the entire viable starting point. Add packages only when you need them.

### Document classes — when to use which

- `article` — papers, short reports, anything < ~30 pages. No `\chapter`. Default for journal-style work.
- `report` — long single-author documents with chapters but no front/back-matter ceremony (e.g. theses where the school provides no class).
- `book` — full books; defines front/main/backmatter, two-sided by default.
- `amsart` — AMS article class. Use for math journals and any submission with AMS-style theorems; nicer top-matter than `article`.
- `memoir` — kitchen-sink class that absorbs `book` + many packages (chapter styles, page layout, TOC tweaks). Best when you want one class to control everything.
- `scrartcl` / `scrreprt` / `scrbook` (KOMA-Script) — European-style typography, far more configurable than the standards. Preferred by many for serious typesetting; integrates with `scrlayer-scrpage` for headers.

Rule of thumb: `article` for papers, `scrartcl` or `memoir` when you want control, `amsart` for math.

### Essential packages

- `fontenc` (T1) — switches to 8-bit font encoding; required for accents, hyphenation, searchable PDFs. Skip on XeLaTeX/LuaLaTeX.
- `inputenc` (utf8) — only needed on legacy pdfLaTeX; modern (TeX Live ≥ 2018) defaults to UTF-8.
- `geometry` — sane page margins in one line.
- `microtype` — character protrusion + font expansion; always load it.
- `csquotes` — context-aware quotes via `\enquote{...}`; required by `biblatex`.
- `babel` (pdfLaTeX/LuaLaTeX) or `polyglossia` (Xe/LuaLaTeX) — language rules, hyphenation, date formats.
- `hyperref` — clickable refs and PDF metadata. **Load last** (or just before `cleveref`) because it redefines many internal commands.
- `cleveref` — load *after* `hyperref`. Provides `\cref{fig:x}` that auto-inserts "Figure" / "Figures" / ranges.

### Sectioning

`\part` > `\chapter` (book/report only) > `\section` > `\subsection` > `\subsubsection` > `\paragraph` > `\subparagraph`. Starred forms (`\section*`) omit numbering and TOC entry. Avoid going deeper than `\subsubsection` — restructure instead.

### Front matter

```latex
\title{...}\author{A \and B}\date{\today}
\maketitle
\begin{abstract} ... \end{abstract}
```

For multiple affiliations use `authblk` or the class-native commands (`amsart`, KOMA).

### Cross-references — use cleveref

```latex
\usepackage{hyperref}
\usepackage[capitalize,noabbrev]{cleveref}
...
See \cref{fig:topology} and \cref{sec:method,sec:results}.
At the start of a sentence: \Cref{tab:cohort} shows...
```

Avoid hand-typing "Figure~\ref{...}"; `\cref` keeps prefixes consistent and handles ranges.

### Lists

```latex
\begin{itemize}\item ... \end{itemize}
\begin{enumerate}\item ... \end{enumerate}
\begin{description}\item[Term] ... \end{description}
```

Load `enumitem` to customize: `\begin{enumerate}[label=(\alph*), leftmargin=*, itemsep=2pt]`.

### Fonts

Default Computer Modern looks dated. Drop-in upgrades for pdfLaTeX:

- `\usepackage{lmodern}` — Latin Modern, near-identical metrics, scalable.
- `\usepackage{newtxtext,newtxmath}` — Times-like with matching math.
- `\usepackage{libertine}\usepackage[libertine]{newtxmath}` — readable serif + math.

For system fonts (Helvetica, Minion, Source Serif, anything installed), compile with **XeLaTeX** or **LuaLaTeX** and use `fontspec`:

```latex
\usepackage{fontspec}
\setmainfont{EB Garamond}
\setsansfont{Inter}
\setmonofont{JetBrains Mono}
```

### Page layout

```latex
\usepackage[a4paper,margin=1in,headheight=14pt]{geometry}
\usepackage{fancyhdr}
\pagestyle{fancy}
\fancyhf{}
\fancyhead[L]{\nouppercase{\leftmark}}
\fancyhead[R]{\thepage}
\renewcommand{\headrulewidth}{0.4pt}
```

Built-in `\pagestyle` options: `plain` (page number only), `empty`, `headings`. Use `\thispagestyle{empty}` on title pages.

### Typography micro-rules

- `Dr.~Smith`, `Fig.~\ref{...}` — `~` is a non-breaking space; use it to glue titles, initials, references.
- `\,` — thin space (e.g. `100\,mg`, `p\,<\,0.05`).
- `---` em-dash, `--` en-dash (ranges: `pp.~10--12`), `-` hyphen.
- `` `single' `` and ` ``double'' ` — backticks open, apostrophes close. Or use `\enquote{...}` from `csquotes`.
- `\dots` (or `\ldots`) — proper ellipsis with correct spacing, not three periods.
- End-of-sentence after a capital letter: `et al.\@ ` (or `\ ` after the period) to prevent inflated inter-sentence spacing.

---

## Math, figures, and tables

### Math packages: load these three

```latex
\usepackage{amsmath, amssymb, mathtools}
```

- **amsmath** — alignment environments (`align`, `gather`, `split`), `\text{}`, `\DeclareMathOperator`, smart spacing. Non-negotiable.
- **amssymb** — extra symbols (`\mathbb`, `\lesssim`, `\nleq`, etc.).
- **mathtools** — superset of `amsmath`: fixes `\overbrace` bugs, adds `\coloneqq` (`:=`), `\DeclarePairedDelimiter`, better `cases` variants (`dcases`, `rcases`). Always prefer it over plain amsmath.

### Inline vs display

```latex
Inline: $E = mc^2$.
Display unnumbered: \[ E = mc^2 \]
Numbered:
\begin{equation}\label{eq:einstein}
  E = mc^2
\end{equation}
Unnumbered display block: equation*
```

**Never use `$$...$$`.** It's plain TeX, not LaTeX — ignores `\displaystyle` spacing rules, breaks `fleqn`, produces inconsistent vertical skips. Use `\[ ... \]` or `equation*`.

### Multi-line and aligned math

```latex
\begin{align}                 % numbered, aligned on &
  a &= b + c \\
  d &= e
\end{align}

\begin{equation}              % one number for the whole block
\begin{aligned}
  f(x) &= x^2 + 2x \\
       &= (x+1)^2 - 1
\end{aligned}
\end{equation}

\begin{gather} a = b \\ c = d \end{gather}   % centered, no alignment

f(x) = \begin{cases}
  x^2 & x \geq 0 \\
  -x  & x < 0
\end{cases}
```

Rule of thumb: `align` for separate equations sharing alignment; `aligned` when you want a single equation number for a multi-line derivation.

### Theorems and proofs

```latex
\usepackage{amsthm}
\newtheorem{thm}{Theorem}[section]
\newtheorem{lem}[thm]{Lemma}
\theoremstyle{definition}\newtheorem{defn}{Definition}

\begin{thm}[Pythagoras]\label{thm:pyth} ... \end{thm}
\begin{proof} ... \end{proof}   % auto QED box
```

### Units and numbers — siunitx

Essential for any scientific document. Handles spacing, decimal/uncertainty formatting, consistent unit rendering.

```latex
\usepackage{siunitx}
\sisetup{detect-all, separate-uncertainty=true}

\SI{5}{\milli\second}          % 5 ms
\SI{1.2(3)e-4}{\joule}          % 1.2(3) x 10^-4 J
\num{1.234e6}                   % 1.234 x 10^6
\si{\ohm\meter}                 % just the unit
```

### Math pitfalls

- Use `\text{...}` (amsmath) for prose inside math; it inherits surrounding font/size. `\mathrm{...}` is for upright *math* symbols (operators, multi-letter variables), not English words.
- Differentials should be upright: `\mathrm{d}x`, or load `physics` and write `\dd x`. Italic `d` reads as "d times x".
- Declare custom operators: `\DeclareMathOperator{\Tr}{Tr}` — gives correct spacing and upright font.

### Figures

```latex
\usepackage{graphicx}

\begin{figure}[htbp]
  \centering
  \includegraphics[width=0.8\linewidth]{fig/circuit.pdf}
  \caption{Rescuer in series with pads.}
  \label{fig:circuit}
\end{figure}
```

Convention: **caption below figures, above tables.** Place `\label` *after* `\caption` or refs break. Use `\linewidth` (column-aware in two-column layouts), not `\textwidth`.

With `pdflatex`, embed **PDF (vector) or PNG (raster)**. EPS requires `epstopdf` or a switch to `latexmk`/`lualatex`. JPEG only for photos.

**Subfigures** — use `subcaption`, not deprecated `subfig`/`subfigure`:

```latex
\usepackage{subcaption}
\begin{figure}
  \begin{subfigure}{0.48\linewidth}
    \includegraphics[width=\linewidth]{a.pdf}\caption{}\label{fig:a}
  \end{subfigure}\hfill
  \begin{subfigure}{0.48\linewidth}
    \includegraphics[width=\linewidth]{b.pdf}\caption{}\label{fig:b}
  \end{subfigure}
  \caption{Two panels.}
\end{figure}
```

### Tables — booktabs, always

```latex
\usepackage{booktabs, tabularx, threeparttable, siunitx}

\begin{table}[htbp]
  \centering
  \caption{Rescuer current by scenario.}
  \label{tab:current}
  \begin{tabular}{l S[table-format=3.1] S[table-format=1.2]}
    \toprule
    Scenario & {Current (\si{\milli\ampere})} & {Energy (\si{\joule})} \\
    \midrule
    Dry hands     &  12.3 & 0.05 \\
    Wet contact   & 234.5 & 1.20 \\
    \bottomrule
  \end{tabular}
\end{table}
```

**Never use `\hline` and vertical bars (`|`) in serious work.** Cramped rules, double lines at page breaks, visually noisy. `booktabs`' three rule weights (`\toprule`, `\midrule`, `\bottomrule`) are the typographic standard.

When to use which tabular:
- `tabular` — fixed-width columns, you control sizing.
- `tabularx` — you want the table to fill a target width; one or more `X` columns absorb slack.
- `tabular*` — same idea but spaces columns rather than stretching one. Rarely the right choice; prefer `tabularx`.

**siunitx `S` column** aligns numbers on the decimal point — use for any numeric column.

**threeparttable** for proper table notes:

```latex
\begin{threeparttable}
  \begin{tabular}{...} ... \end{tabular}
  \begin{tablenotes}\footnotesize
    \item[a] Measured at 200 J.
  \end{tablenotes}
\end{threeparttable}
```

**Wide tables** — don't squeeze. Rotate the page:

```latex
\usepackage{pdflscape}        % or 'rotating' for sideways within portrait
\begin{landscape} ... \end{landscape}
```

### TikZ / pgfplots (brief)

For vector diagrams and data plots authored in-document, `\usepackage{tikz, pgfplots}` with `\pgfplotsset{compat=1.18}`. Produces crisp, font-consistent figures, but compile times grow fast — externalize (`\usetikzlibrary{external}`) for large documents. Pre-rendered PDFs from Python/R via `matplotlib`'s PGF backend or `tikzplotlib` are often the pragmatic choice.

---

## Bibliography & citations

### The three systems

LaTeX has three competing bibliography stacks. Pick one and don't mix them:

- **Legacy BibTeX** — original. `\bibliographystyle{...}` + `\bibliography{...}` + `\cite{...}`. ASCII-only, limited styles (`plain`, `unsrt`, `alpha`, `abbrv`), brittle with non-English names and Unicode. Avoid for new work.
- **natbib** — a BibTeX-era package that adds author-year commands (`\citep`, `\citet`) on top of legacy BibTeX. Still ubiquitous because many journal `.cls` files load it.
- **biblatex + biber** — modern stack. Native UTF-8, dozens of styles, configurable, handles complex names, supports `@online`. **Use this for new work** unless a journal template forces otherwise.

### Backend confusion

`bibtex` and `biber` are two different external programs. `biblatex` *can* use either, but **biber is the default and the only one that supports the full feature set** (Unicode, advanced sorting, name disambiguation). If you see `Package biblatex Warning: '...' not found`, you probably ran `bibtex` when biber was expected — or vice versa. Match the `backend=` option to the program you run.

### Minimal biblatex setup

```latex
\usepackage[style=numeric-comp,backend=biber,sorting=none]{biblatex}
\addbibresource{bibliography/references.bib}

\begin{document}
... \autocite{lemkin2014} ...
\printbibliography
\end{document}
```

`sorting=none` makes citations appear in order of first use (typical for numeric biomedical styles). Drop it for author-year.

### Citation commands (biblatex)

| Command | Renders as | Use when |
|---|---|---|
| `\cite{key}` | bare — style-dependent | rarely; prefer explicit forms below |
| `\parencite{key}` | `(Lemkin 2014)` or `[3]` | citation in parentheses, mid-sentence |
| `\textcite{key}` | `Lemkin (2014)` | author is the subject of your sentence |
| `\autocite{key}` | whatever `autocite=` is set to | default workhorse — set once, use everywhere |
| `\footcite{key}` | footnote citation | humanities styles; rare in biomed |
| `\citeauthor{key}` | `Lemkin` | author name only |
| `\citeyear{key}` | `2014` | year only |

Multiple keys: `\autocite{lemkin2014,kerber1993,cheskes2011}` — numeric-comp will compress to `[1-3]`.

### Biomedical styles

- `numeric` / `numeric-comp` — `[1]` / `[1-3,7]`. Default for most medical journals.
- `authoryear` — `(Lemkin, 2014)`.
- `vancouver` (biblatex package: `biblatex-vancouver`) — required by ICMJE-style journals (NEJM, Lancet, JAMA, Resuscitation, Circulation).
- `nature`, `science` — provided by `biblatex-publication-list` / `biblatex-nature` packages.

Journals almost always mandate a style — check the author guide before composing.

### .bib file format

```bibtex
@article{lemkin2014,
  author  = {Lemkin, Daniel L. and Witting, Michael D. and Allison, Michael G.
             and Farzad, Ali and Bond, Michael C. and Lemkin, Mark A.},
  title   = {Electrical exposure risk associated with hands-on defibrillation},
  journal = {Resuscitation},
  year    = {2014},
  volume  = {85},
  number  = {10},
  pages   = {1330--1336},
  doi     = {10.1016/j.resuscitation.2014.06.026},
}

@book{...}        % whole book — needs publisher
@incollection{...}% chapter in edited volume — needs booktitle, editor
@misc{...}        % anything else — preprints, datasets, software
@online{...}      % web resources — needs url and urldate (biblatex only)
```

Always include `doi` when available; biblatex hyperlinks it automatically. Use `url` + `urldate` only when there is no DOI.

### Common pitfalls

- **Capitalisation.** BibTeX/biber lowercases title words by default. Protect proper nouns with braces: `title = {Defibrillation thresholds in the {Lloyd} cohort and the {AED}}`.
- **Particle names.** Use `last, first` form so the parser sees the particle: `author = {van der Werf, Christian}`, not `Christian van der Werf` (which gets split on the last space).
- **Stale .bbl.** After editing `.bib`, re-run biber. Symptom: "`?`" or "`[??]`" in the PDF.
- **Compile sequence.** `pdflatex → biber → pdflatex → pdflatex`. Use `latexmk -pdf` and forget about it.

### Tools

- **JabRef** — cross-platform, BibTeX-native, good search and grouping.
- **BibDesk** — macOS only, Spotlight + Finder integration, attaches PDFs by drag-and-drop. Best fit on macOS.
- **Zotero + Better BibTeX** — recommended if you also need browser-capture and PDF library management. Better BibTeX gives stable citekeys (e.g., `lemkin2014`) and auto-exports to a `.bib` file your LaTeX project watches.

### Journal submission

Most biomedical journals want **Vancouver-style numeric citations** in submission order. Many accept (or require) a compiled `.bbl` bundled with your `.tex`, since they can't run biber on their end. If a journal supplies a `.cls`, it usually pulls in `natbib` with a numeric style — adapt rather than fight it.

---

## Errors, pitfalls, and debugging

### Common errors (read these first)

```
! Undefined control sequence.
l.42 \includegraphis
                    {fig1.pdf}
```
Typo in a command, or the defining package isn't loaded. Check spelling, then `\usepackage{...}` (e.g., `graphicx` for `\includegraphics`, `amsmath` for `\eqref`, `siunitx` for `\SI`).

```
! Missing $ inserted.
```
A math-only character escaped into text mode — almost always `_` or `^` in a filename, label, or author name. Wrap in math (`$x_1$`) or escape (`file\_name`). Subscripts in `\section{}` and captions are frequent offenders.

```
Runaway argument?
! Paragraph ended before \foo was complete.
```
or
```
! File ended while scanning use of \foo.
```
Unclosed `{`, missing `}`, or an environment whose `\end{...}` is missing/misspelled. Bisect by commenting halves of the document; check every `\begin{X}` has a matching `\end{X}`.

```
! LaTeX Error: Environment tikzpicture undefined.
```
Missing `\usepackage{...}`. Map environment → package (`tikzpicture` → `tikz`, `algorithmic` → `algpseudocode`, `tabularx` → `tabularx`, `subfigure` → `subcaption`).

```
Overfull \hbox (12.3pt too wide) in paragraph at lines 88--92
```
A line couldn't break cleanly. Fixes, in order: `\usepackage{microtype}` (cures most cases), hyphenation hints `com\-pli\-cat\-ed`, rewrite the sentence, or wrap the section in `{\sloppy ...}` as a last resort. Don't ship `\sloppy` document-wide.

```
Underfull \hbox (badness 10000) ...
Underfull \vbox ...
```
Cosmetic — TeX stretched glue more than it liked. Ignore unless visibly ugly.

```
! LaTeX Error: Float too large for page.
```
Figure or table exceeds the text block. Shrink with `\includegraphics[width=\linewidth]{...}` or use `[p]` placement to give it its own page.

```
! LaTeX Error: Too many unprocessed floats.
```
You queued 18+ figures without flushing. Insert `\clearpage` at a natural break, or `\usepackage{placeins}` and `\FloatBarrier` at section boundaries.

```
LaTeX Warning: There were undefined references.
LaTeX Warning: Label(s) may have changed. Rerun to get cross-references right.
```
Run the build twice (or three times with TOC / `cleveref` / bibliography). If it persists, the `\label{...}` is missing, misspelled, or sits inside a non-numbered context.

### Pitfalls

**Special characters.** Ten need escaping in text mode: `% $ & # _ { } ^ ~ \`. First seven take a leading backslash (`\%`, `\&`, ...). Last three: `\textasciicircum`, `\textasciitilde`, `\textbackslash`.

**Spaces eaten after commands.** `\LaTeX is great` renders as "LaTeXis great". Use `\LaTeX{} is great` or `\LaTeX\ is great`. The `xspace` package fixes this for your own macros.

**`\\` vs `\par`.** `\\` forces a line break without ending the paragraph and is correct only inside tables, `tabular`, `align`, or addresses. For paragraph breaks in body text, use a blank line (which is `\par`). Stray `\\` between paragraphs produces "There's no line here to end" errors and ugly spacing.

**Package load order.** `hyperref` must come near the *end* of the preamble — after almost everything except `cleveref`, which must come *after* `hyperref`. `biblatex` loads before `hyperref`. `microtype` last, after `hyperref`.

**Input encoding.** With `xelatex`/`lualatex`, drop `inputenc` and `fontenc` — UTF-8 native (use `\usepackage{fontspec}` instead). With `pdflatex`, you need `\usepackage[utf8]{inputenc}` and `\usepackage[T1]{fontenc}`.

**Stale aux files.** Mysterious "undefined references" that don't go away, or a TOC stuck on an old structure, usually mean corrupted auxiliaries. Delete `*.aux *.log *.toc *.out *.bbl *.blg` and rebuild. `latexmk -C` does this.

**Microtype quirks.** `microtype` is pdflatex-native; works with lualatex with reduced features; historically rough on xelatex (much improved). If font-expansion errors, try `\usepackage[protrusion=true,expansion=false]{microtype}`.

### Debugging workflow

1. **Read the first error only.** Everything after is cascade noise. Jump to the reported line; check the *previous* few lines too.
2. **`\listfiles`** at the top of the preamble dumps every package + version into the `.log` — essential for "works on my machine" reports.
3. **Bisect.** Comment out the second half with `\end{document}`; if it compiles, bug is in the omitted half. Halve again.
4. **Interaction modes.** `pdflatex -interaction=nonstopmode file.tex` for CI/batch; `-interaction=errorstopmode` to drop into the prompt and inspect `\show\foo`.
5. **Linters.** `chktex file.tex` catches style and many silent mistakes (missing `~` before citations, mismatched quotes); `lacheck` is older but complementary.

### Journal submission

- **Class file.** Most journals ship one: `elsarticle` (Elsevier), `IEEEtran` (IEEE), `revtex4-2` (APS/AIP), `acmart` (ACM), Springer's `sn-jnl`. Use it from day one — switching late breaks floats, references, section numbering.
- **arXiv.** Must build with stock TeX Live (no exotic local packages). Bundle the `.bbl` file; arXiv won't run BibTeX. Flatten `\input`/`\include` if structure is fragile.
- **Common journal asks.** Line numbers via `\usepackage{lineno}` + `\linenumbers`; double-spacing via `\usepackage{setspace}` + `\doublespacing`; figures as separate files (often EPS or high-DPI TIFF) rather than embedded; "highlights" or "graphical abstract" file; blinded vs unblinded versions.
- **Medical/scientific specifics.** ICMJE-style author lists, CONSORT/PRISMA flow diagrams (often a single figure), structured abstracts with fixed headings. Vancouver numeric citations are standard — `biblatex` with `style=numeric-comp` or `natbib` with `\citep`/`\citet` and a journal-supplied `.bst` (e.g., `vancouver.bst`, `unsrtnat`).
