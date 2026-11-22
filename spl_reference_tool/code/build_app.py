"""Inject model.json into the HTML template -> app/index.html (single self-contained file)."""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
APP = os.path.join(HERE, "..", "app")
tpl = open(os.path.join(APP, "template.html"), encoding="utf-8").read()
model = json.load(open(os.path.join(APP, "model.json")))
blob = json.dumps(model, separators=(",", ":")).replace("</", "<\\/")
html = tpl.replace("__MODEL_JSON__", blob)
open(os.path.join(APP, "index.html"), "w", encoding="utf-8").write(html)
print("app/index.html", round(len(html) / 1024), "KB")
