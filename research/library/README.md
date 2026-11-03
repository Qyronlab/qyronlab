# Library — who downloaded what (both arms, 2026-10-23)

Set up at the owner's request so that no source is fetched twice and both arms can see what the other already holds.
Arm A is the lab's own arm, Arm B the independent arm. Both may write here.

## The one rule
1. **Before downloading** anything, look it up: `python3 -I library.py find <url-or-title-fragment>`.
   If it is here with status `ok`, ask the holding arm for the bytes (channel) instead of fetching again.
2. **After downloading**, add exactly one row: `python3 -I library.py add --arm A|B --url URL --file PATH --title "..."`.
   The script computes sha256 and byte count from the file and refuses a duplicate sha256 or url.
3. A failed attempt is also a row (`--fail --bytes N --note "what came back"`), so the other arm does not repeat it.
4. Rows are append-only. Never edit another arm's row; if something is wrong, add a row with status `fix`, the same sha256 as
   the existing row and the corrected fields (not a download, exempt from the duplicate check), and say so in `note`.
   `check` refuses a `fix` that has no EARLIER `ok` row with that sha256, or that changes nothing against the effective row;
   `bytes` must be a positive integer or `-`; url uniqueness is enforced on the effective view, so a `fix` cannot move a row
   onto another row's url. `find` shows the
   **effective view** (the `ok` row with its later fixes applied, tagged with the line numbers); `find --raw` shows every row.
   One exception: a placeholder row Arm A entered on Arm B's behalf is Arm A's row; Arm A completes its `-` fields in place
   from B's later data and says so in `note` (git history keeps the earlier state).
5. The bytes themselves stay with the arm that fetched them (or in this repo where a licence allows). The registry holds
   only url, sha256, byte count, title, note. A row is a claim by the arm that wrote it; the sha256 is what the other arm
   checks when the bytes are handed over.

## Writing here
- An arm with push access commits its own row on `main` (commit message: `library: <title>`).
- An arm without push access sends the finished TSV row on the private channel (topic `library`); Arm A commits it
  verbatim with `note` = "entered by A from B's channel row #<id>" and the sending arm fills in anything missing later.

`downloads.tsv` is tab-separated, header `date_utc arm status sha256 bytes url title note`; `-` marks an unknown field.
`python3 -I library.py check` validates the whole file; run it before every commit.
