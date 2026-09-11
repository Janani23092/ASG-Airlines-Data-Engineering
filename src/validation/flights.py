import re
import numpy as np
import pandas as pd

HARD_REASONS = {
    "MISSING_FLIGHT_ID", "INVALID_FLIGHT_ID_FORMAT", "MISSING_SOURCE",
    "MISSING_DESTINATION", "SOURCE_EQUALS_DESTINATION",
    "MISSING_DEPARTURE_TIME", "MISSING_ARRIVAL_TIME", "CORRUPTED_TIMESTAMP",
    "DUPLICATE_RECORD"
}

def validate_flights(df: pd.DataFrame) -> pd.DataFrame:
    df=df.copy()
    df["departure_time"]=pd.to_datetime(df["departure_time"],errors="coerce")
    df["arrival_time"]=pd.to_datetime(df["arrival_time"],errors="coerce")
    df["row_ref"]=df.index
    reasons=[]
    for _,r in df.iterrows():
        rr=[]
        fid=str(r.get("flight_id","")).strip() if pd.notna(r.get("flight_id")) else ""
        if not fid: rr.append("MISSING_FLIGHT_ID")
        elif not re.match(r"^[A-Z0-9]{2,3}\d{3}$",fid): rr.append("INVALID_FLIGHT_ID_FORMAT")
        for c,code in [("source","MISSING_SOURCE"),("destination","MISSING_DESTINATION")]:
            if pd.isna(r.get(c)) or str(r.get(c)).strip()=="": rr.append(code)
        if pd.notna(r.get("source")) and pd.notna(r.get("destination")) and str(r["source"]).strip().upper()==str(r["destination"]).strip().upper():
            rr.append("SOURCE_EQUALS_DESTINATION")
        if pd.isna(r.get("departure_time")): rr.append("MISSING_DEPARTURE_TIME")
        if pd.isna(r.get("arrival_time")): rr.append("MISSING_ARRIVAL_TIME")
        if pd.notna(r.get("departure_time")) and pd.notna(r.get("arrival_time")):
            gap=(r["arrival_time"]-r["departure_time"]).total_seconds()/60
            if gap < -720: rr.append("CORRUPTED_TIMESTAMP")
        reasons.append(rr)
    df["reason_codes"]=reasons
    dupe=df.duplicated(subset=["flight_id","airline","source","destination","departure_time","arrival_time"],keep="first")
    df.loc[dupe,"reason_codes"]=df.loc[dupe,"reason_codes"].apply(lambda x:x+["DUPLICATE_RECORD"])
    df["hard_reasons"]=df["reason_codes"].apply(lambda x:[r for r in x if r in HARD_REASONS])
    df["is_valid"]=df["hard_reasons"].str.len().eq(0)
    df["validation_status"]=np.where(df["is_valid"],"VALID","INVALID")
    return df
