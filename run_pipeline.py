from pathlib import Path
import pandas as pd
from src.ingestion.loader import load_source
from src.validation.flights import validate_flights
from src.transformation.flights import transform_flights
from src.utils.metrics import quality_metrics, reconcile

ROOT=Path(__file__).resolve().parent
SOURCE=ROOT/"data"/"sample"/"UseCase_-_Airlines_sample.xlsx"
OUT=ROOT/"data"

def main():
    tables=load_source(SOURCE)
    flights=tables["flights"]
    validated=validate_flights(flights)
    quarantine=validated[~validated["is_valid"]].copy()
    curated=transform_flights(validated)

    # Shared dimensions aligned to the keys present in fact_flights.
    dim_airline=(curated[["airline_key","airline"]].drop_duplicates().sort_values("airline_key"))
    dim_route=(curated[["route_key","source","destination","route"]].drop_duplicates().sort_values("route_key"))
    dim_date=pd.DataFrame({"date":pd.to_datetime(curated["departure_time"]).dt.normalize().drop_duplicates().sort_values()})
    dim_date["date_key"]=dim_date["date"].dt.strftime("%Y%m%d")
    dim_date["year"]=dim_date["date"].dt.year
    dim_date["month"]=dim_date["date"].dt.month
    dim_date["month_name"]=dim_date["date"].dt.strftime("%B")
    dim_date["day"]=dim_date["date"].dt.day
    dim_date["day_name"]=dim_date["date"].dt.strftime("%A")
    dim_date["is_weekend"]=dim_date["date"].dt.dayofweek >= 5

    # Quarantine output is intentionally non-PII for flight operations.
    q=quarantine[[c for c in ["row_ref","flight_id","airline","source","destination","departure_time","arrival_time","hard_reasons"] if c in quarantine]].copy()
    if "hard_reasons" in q: q["reason_description"]=q["hard_reasons"].apply(lambda x:"; ".join(x) if isinstance(x,list) else str(x))
    q.drop(columns=["hard_reasons"],errors="ignore").to_csv(OUT/"quarantine"/"flights_quarantine.csv",index=False)

    curated.to_csv(OUT/"curated"/"fact_flights.csv",index=False)
    dim_airline.to_csv(OUT/"curated"/"dim_airline.csv",index=False)
    dim_route.to_csv(OUT/"curated"/"dim_route.csv",index=False)
    dim_date.to_csv(OUT/"curated"/"dim_date.csv",index=False)

    metrics=quality_metrics(flights,curated,quarantine)
    ok=reconcile(len(flights),len(curated),len(quarantine))
    dq=pd.DataFrame([{**metrics,"reconciliation":"PASS" if ok else "FAIL"}])
    dq.to_csv(OUT/"curated"/"dq_metrics.csv",index=False)
    pd.DataFrame([
        {"status":"VALID","record_count":len(curated)},
        {"status":"INVALID","record_count":len(quarantine)},
    ]).to_csv(OUT/"curated"/"record_quality_summary.csv",index=False)

    summary=pd.DataFrame([
        {"kpi":"Input Flights","value":len(flights)},
        {"kpi":"Total Flights","value":len(curated)},
        {"kpi":"Average Flight Duration (min)","value":round(curated["duration_minutes"].mean(),2)},
        {"kpi":"Overnight Flights","value":int(curated["is_overnight"].sum())},
        {"kpi":"Overnight Flight Share (%)","value":round(curated["is_overnight"].mean()*100,2)},
        {"kpi":"Anomalies","value":int(curated["anomaly_flag"].eq("ANOMALY").sum())},
        {"kpi":"Anomaly Rate (%)","value":round(curated["anomaly_flag"].eq("ANOMALY").mean()*100,2)},
        {"kpi":"Quarantined Flights","value":len(quarantine)},
        {"kpi":"Data Quality Score (%)","value":metrics["dq_score"]},
        {"kpi":"Reconciliation","value":"PASS" if ok else "FAIL"},
    ])
    summary.to_csv(OUT/"curated"/"kpi_summary.csv",index=False)

    route_traffic=curated.groupby("route").size().sort_values(ascending=False).reset_index(name="flight_count")
    route_traffic.to_csv(OUT/"curated"/"kpi_route_traffic.csv",index=False)
    airline_dist=curated.groupby("airline").size().sort_values(ascending=False).reset_index(name="flight_count")
    airline_dist.to_csv(OUT/"curated"/"kpi_airline_distribution.csv",index=False)

    print("="*58); print("ASG AIRLINES PIPELINE"); print("="*58)
    print(f"Input records       : {len(flights)}")
    print(f"Curated records     : {len(curated)}")
    print(f"Quarantined records : {len(quarantine)}")
    print(f"Overnight flights   : {int(curated['is_overnight'].sum())}")
    print(f"Anomalies           : {int(curated['anomaly_flag'].eq('ANOMALY').sum())}")
    print(f"DQ score            : {metrics['dq_score']:.2f}%")
    print(f"Reconciliation      : {'PASS' if ok else 'FAIL'}")
    print("Pipeline status     : SUCCESS" if ok else "Pipeline status     : FAILED")
    return 0 if ok else 1

if __name__=="__main__": raise SystemExit(main())
