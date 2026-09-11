import numpy as np
import pandas as pd

AIRLINE_KEY_MAP = {
    "Air India": "AL001",
    "IndiGo": "AL002",
    "SpiceJet": "AL003",
    "Unknown": "AL004",
    "Vistara": "AL005",
}

def transform_flights(validated: pd.DataFrame, duration_suspicious_minutes: float = 360) -> pd.DataFrame:
    df=validated[validated["is_valid"]].copy()
    df["airline"]=df["airline"].astype("string").str.strip().replace({"":"Unknown","UNKNOWN":"Unknown"}).fillna("Unknown")
    df["airline_quality_flag"]=np.where(df["airline"].eq("Unknown"),"IMPUTED_UNKNOWN_AIRLINE","OK")
    df["source"]=df["source"].astype("string").str.strip().str.upper()
    df["destination"]=df["destination"].astype("string").str.strip().str.upper()
    df["route"]=df["source"]+" -> "+df["destination"]
    df["arrival_time_adjusted"]=df["arrival_time"]
    neg=df["arrival_time_adjusted"] < df["departure_time"]
    df.loc[neg,"arrival_time_adjusted"]=df.loc[neg,"arrival_time_adjusted"]+pd.Timedelta(days=1)
    df["duration_minutes"]=(df["arrival_time_adjusted"]-df["departure_time"]).dt.total_seconds()/60
    df["is_overnight"]=df["departure_time"].dt.date.ne(df["arrival_time_adjusted"].dt.date)
    df["duration_status"]=np.select([df["duration_minutes"].le(0),df["duration_minutes"].gt(duration_suspicious_minutes)], ["INVALID","SUSPICIOUS"],default="VALID")
    df["anomaly_flag"]=np.where((df["duration_status"]!="VALID")|df["airline_quality_flag"].ne("OK"),"ANOMALY","NORMAL")
    df["flight_key"]=[f"FK{i:05d}" for i in range(1,len(df)+1)]
    df["airline_key"]=df["airline"].map(AIRLINE_KEY_MAP)
    route_order=pd.DataFrame({"route": sorted(df["route"].dropna().unique())})
    route_order["route_key"]=[f"RT{i:03d}" for i in range(1,len(route_order)+1)]
    df=df.merge(route_order,on="route",how="left")
    df["date_key"]=pd.to_datetime(df["departure_time"]).dt.strftime("%Y%m%d")
    return df
