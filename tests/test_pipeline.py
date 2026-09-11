import pandas as pd
from src.validation.flights import validate_flights
from src.transformation.flights import transform_flights
from src.utils.metrics import reconcile

def base(dep='2026-01-01 10:00:00', arr='2026-01-01 12:00:00'):
    return pd.DataFrame({'flight_id':['AI999'],'airline':['Air India'],'source':['DEL'],'destination':['BOM'],'departure_time':[pd.Timestamp(dep)],'arrival_time':[pd.Timestamp(arr)]})

def test_same_day_duration():
    r=transform_flights(validate_flights(base())).iloc[0]
    assert r.duration_minutes==120 and not r.is_overnight

def test_overnight_duration():
    r=transform_flights(validate_flights(base('2026-01-01 23:40:00','2026-01-02 01:20:00'))).iloc[0]
    assert r.duration_minutes==100 and r.is_overnight

def test_missing_departure():
    d=base(); d.loc[0,'departure_time']=pd.NaT
    assert 'MISSING_DEPARTURE_TIME' in validate_flights(d).iloc[0].reason_codes

def test_missing_arrival():
    d=base(); d.loc[0,'arrival_time']=pd.NaT
    assert 'MISSING_ARRIVAL_TIME' in validate_flights(d).iloc[0].reason_codes

def test_invalid_id():
    d=base(); d.loc[0,'flight_id']='BAD-ID'
    assert 'INVALID_FLIGHT_ID_FORMAT' in validate_flights(d).iloc[0].reason_codes

def test_duplicate():
    d=pd.concat([base(),base()],ignore_index=True); r=validate_flights(d)
    assert 'DUPLICATE_RECORD' in r.iloc[1].reason_codes

def test_corrupt_timestamp():
    r=validate_flights(base('2026-01-02 18:00:00','2026-01-01 20:00:00')).iloc[0]
    assert 'CORRUPTED_TIMESTAMP' in r.reason_codes

def test_same_airport():
    d=base(); d.loc[0,'destination']='DEL'
    assert 'SOURCE_EQUALS_DESTINATION' in validate_flights(d).iloc[0].reason_codes

def test_reconciliation():
    assert reconcile(100,96,4)
    assert not reconcile(100,95,4)
