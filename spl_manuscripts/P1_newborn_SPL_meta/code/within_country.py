"""Variance decomposition: how much between-study heterogeneity in mean newborn SPL
lies WITHIN countries (method/observer) versus BETWEEN countries (population)?"""
import json, os, sys
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "common"))
import meta
D = os.path.join(HERE, "..", "data")
u = pd.read_csv(os.path.join(D, "analysis_dataset.csv"))
u["country0"] = u["country"].str.split("(").str[0].str.strip()
res = {}
cnt = u.groupby("country0")["study_id"].nunique()
multi = cnt[cnt >= 2].index.tolist()
res["countries_with_ge2_studies"] = {c: int(cnt[c]) for c in multi}
per = {}
for c in multi:
    g = u[u.country0 == c]
    r = meta.random_effects(g["mean"], g["sd"] ** 2 / g["n"], "REML", hksj=True)
    per[c] = dict(k=r.k, studies=int(g.study_id.nunique()), mu=r.mu, tau=r.tau, I2=r.I2,
                  range=[float(g["mean"].min()), float(g["mean"].max())])
res["within_country_RE"] = per
# Meta-regression with country fixed effects (only countries with >=2 studies, others pooled as 'other')
u["cgrp"] = np.where(u.country0.isin(multi), u.country0, "_other")
levels = sorted(u.cgrp.unique())
ref = "_other"
X = np.column_stack([(u.cgrp == l).astype(float) for l in levels if l != ref])
mr = meta.meta_regression(u["mean"], u["sd"] ** 2 / u["n"], X, [l for l in levels if l != ref])
tot = meta.random_effects(u["mean"], u["sd"] ** 2 / u["n"], "REML", hksj=True)
# Residual tau^2 among multi-study countries only (pure within-country variance)
m = u[u.country0.isin(multi)]
Xm = np.column_stack([(m.country0 == l).astype(float) for l in multi[1:]])
mrm = meta.meta_regression(m["mean"], m["sd"] ** 2 / m["n"], Xm, multi[1:])
tot_m = meta.random_effects(m["mean"], m["sd"] ** 2 / m["n"], "REML", hksj=True)
res["total_tau_all"] = tot.tau
res["multi_country_subset"] = dict(k=int(len(m)), tau_total=tot_m.tau, tau_within_country=float(np.sqrt(mrm["tau2_resid"])),
                                   share_within=float(mrm["tau2_resid"] / tot_m.tau2), R2_country=mrm["R2"])
json.dump(res, open(os.path.join(D, "within_country_results.json"), "w"), indent=2, default=float)
print(json.dumps(res, indent=1, default=lambda x: round(float(x), 3)))
