const PREFIX_RE = /^(utm_|mtm_|pk_|vero_|oly_)/i;
const EXACT = new Set([
  "msclkid", "gclid", "gbraid", "wbraid", "dclid", "fbclid", "ttclid",
  "twclid", "li_fat_id", "igshid", "yclid", "epik", "irclickid", "clickid",
  "mc_cid", "mc_eid", "_hsenc", "_hsmi", "mkt_tok", "ref_src",
  "cm_mmc", "cm_sp", "cm_re", "cm_ven", "cm_cat", "cm_pla", "cm_ite",
]);
const DOMAIN_RULES = [
  [/ebay\./i, ["mkevt", "mkcid", "mkrid", "campid", "toolid", "customid", "loc", "amdata", "hash"]],
  [/amazon\./i, ["tag", "linkcode", "ref_", "pd_rd_r", "pd_rd_w", "pd_rd_wg", "pf_rd_p", "pf_rd_r", "crid", "sprefix", "qid", "sr", "keywords"]],
  [/abebooks\./i, ["ref_", "cm_mmc"]],
  [/aliexpress\./i, ["spm", "scm", "aff_fcid", "aff_fsk", "aff_platform", "aff_trace_key", "terminal_id"]],
];

function cleanUrl(href) {
  let url;
  try { url = new URL(href, location.href); } catch { return null; }
  if (!/^https?:$/.test(url.protocol)) return null;

  const domainExtra = new Set(
    DOMAIN_RULES.filter(([re]) => re.test(url.hostname)).flatMap(([, p]) => p)
  );
  let changed = false;
  for (const key of [...url.searchParams.keys()]) {
    const k = key.toLowerCase();
    if (PREFIX_RE.test(k) || EXACT.has(k) || domainExtra.has(k)) {
      url.searchParams.delete(key);
      changed = true;
    }
  }
  return changed ? url.toString() : null;
}

function cleanAnchors(root) {
  const anchors = root.querySelectorAll ? root.querySelectorAll("a[href]") : [];
  for (const a of anchors) {
    const cleaned = cleanUrl(a.getAttribute("href"));
    if (cleaned) a.href = cleaned;
  }
}

cleanAnchors(document);
new MutationObserver((mutations) => {
  for (const m of mutations) {
    for (const node of m.addedNodes) {
      if (node.nodeType === 1) cleanAnchors(node);
    }
  }
}).observe(document.documentElement, { childList: true, subtree: true });
