from pathlib import Path
import sys, json
import pandas as pd
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root / "src"))
from modeling import build_model_frame, train_and_evaluate
frame=pd.read_csv(root / "data/processed/credit_risk_clean.csv")
results=train_and_evaluate(*build_model_frame(frame))
report={"rows":len(frame), "metrics":results["metrics"], "limitation":"Historical preprocessing precedes splitting; this verifies the saved baseline, not leakage-free performance."}
(root / "reports/business/baseline_verification.json").write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
