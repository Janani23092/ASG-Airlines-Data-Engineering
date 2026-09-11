import pandas as pd

def quality_metrics(raw: pd.DataFrame, curated: pd.DataFrame, quarantined: pd.DataFrame):
    required=["flight_id","airline","source","destination","departure_time","arrival_time"]
    completeness=((raw[required].notna()) & raw[required].ne("UNKNOWN")).mean().mean()*100
    validity=(len(raw)-len(quarantined))/len(raw)*100 if len(raw) else 0
    uniqueness=(1-raw.duplicated(subset=["flight_id","airline","source","destination","departure_time","arrival_time"]).mean())*100 if len(raw) else 0
    consistency=curated["duration_status"].eq("VALID").mean()*100 if len(curated) else 0
    score=0.30*completeness+0.30*validity+0.20*uniqueness+0.20*consistency
    return {"completeness":round(completeness,2),"validity":round(validity,2),"uniqueness":round(uniqueness,2),"consistency":round(consistency,2),"dq_score":round(score,2)}

def reconcile(input_count:int, curated_count:int, quarantine_count:int):
    return input_count == curated_count + quarantine_count
