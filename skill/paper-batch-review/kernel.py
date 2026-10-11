
import os

def pbr_bundle(key, paper_files, data_dir, outdir="bundles", skip_dirs=None):
    """Build one self-contained review bundle: paper/ + data/ in a single zip.

    key: short paper identifier used in filenames ("forman").
    paper_files: list of paths to the paper text and/or PDF.
    data_dir: directory holding the authors' deposited data and code (may be None).
    Returns the zip path. save_artifacts it, then put the literal {{artifact:VID}}
    marker in the sub-agent's task -- sub-agents cannot read your paths.
    """
    import zipfile
    if skip_dirs is None:
        skip_dirs = ("__MACOSX",)
    os.makedirs(outdir, exist_ok=True)
    zp = os.path.join(outdir, "%s_bundle.zip" % key)
    with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
        for f in paper_files:
            z.write(f, "paper/" + os.path.basename(f))
        if data_dir and os.path.isdir(data_dir):
            for root, _, names in os.walk(data_dir):
                for n in names:
                    p = os.path.join(root, n)
                    rel = os.path.relpath(p, data_dir).replace("\\", "/")
                    if any(s in rel for s in skip_dirs):
                        continue
                    z.write(p, "data/" + rel)
    return zp


def pbr_rewrite_markers(md_text, vmap):
    """Rewrite {{artifact:VERSION_ID}} markers to repo-relative filenames.

    vmap: {version_id: filename}. Platform markers render as broken text outside
    the app, so run this before publishing anywhere else.
    Returns (rewritten_text, unresolved_version_ids). Assert the list is empty.
    """
    import re
    pat = re.compile(r"\{\{artifact:([0-9a-fA-F-]{36})\}\}")
    out = pat.sub(lambda m: vmap.get(m.group(1), m.group(0)), md_text)
    return out, sorted(set(pat.findall(out)))


def pbr_verdict_summary(csv_paths, verdict_col="verdict", severity_col="severity",
                        verdicts=None):
    """Cross-paper verdict counts computed from the committed claim tables.

    csv_paths: {paper_key: path_to_claims_csv}. Never build this summary from the
    sub-agents' prose -- read the tables they committed.
    Returns a DataFrame indexed by paper with a 'total' row; unrecognised verdict
    labels are collected in the 'unmapped' column rather than silently dropped.
    """
    import pandas as pd
    if verdicts is None:
        verdicts = ["Supported", "Supported, overstated", "Mis-specified",
                    "Not assessable", "Contradicted"]
    rows = []
    for key, path in csv_paths.items():
        df = pd.read_csv(path)
        df.columns = [c.strip().lower() for c in df.columns]
        v = df[verdict_col].astype(str).str.strip()
        rec = {"paper": key, "n_claims": len(df)}
        rec.update({x: int((v == x).sum()) for x in verdicts})
        if severity_col in df.columns:
            s = df[severity_col].astype(str).str.strip().str.upper()
            rec.update({"sev" + g: int((s == g).sum()) for g in ("A", "B", "C")})
        rec["unmapped"] = "; ".join(sorted(set(v) - set(verdicts)))
        rows.append(rec)
    out = pd.DataFrame(rows).set_index("paper")
    num = [c for c in out.columns if c != "unmapped"]
    out.loc["total", num] = out[num].sum()
    out.loc["total", "unmapped"] = ""
    return out.astype({c: int for c in num})


def pbr_github_put(repo, relpath, data, message, token, branch=None):
    """Create or update one file via the GitHub Contents API.

    repo: "owner/name". data: bytes. Fetches the current blob sha when the file
    already exists, so the call works for both create and update.
    A read-scoped token returns 403 'Resource not accessible by personal access
    token'; the response header x-accepted-github-permissions names what is missing.
    Returns (status_code, response_or_error_text).
    """
    import base64, json, urllib.request, urllib.error
    hdr = {"Authorization": "Bearer " + token,
           "Accept": "application/vnd.github+json",
           "X-GitHub-Api-Version": "2022-11-28",
           "Content-Type": "application/json"}
    url = "https://api.github.com/repos/%s/contents/%s" % (repo, relpath)

    def call(method, payload=None):
        req = urllib.request.Request(
            url, data=json.dumps(payload).encode() if payload is not None else None,
            method=method, headers=hdr)
        try:
            r = urllib.request.urlopen(req, timeout=120)
            return r.status, json.loads(r.read() or b"{}")
        except urllib.error.HTTPError as e:
            return e.code, e.read(400).decode("utf-8", "replace")

    body = {"message": message, "content": base64.b64encode(data).decode()}
    if branch:
        body["branch"] = branch
    status, cur = call("GET")
    if status == 200 and isinstance(cur, dict) and "sha" in cur:
        body["sha"] = cur["sha"]
    return call("PUT", body)
