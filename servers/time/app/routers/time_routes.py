"""Time utilities: UTC/local, format, convert, elapsed, parse, list timezones."""
from datetime import datetime, timezone

import pytz
from dateutil import parser as dateutil_parser
from fastapi import APIRouter, Body, HTTPException

from app.schemas import (
    ConvertTimeInput,
    ElapsedTimeInput,
    FormatTimeInput,
    ParseTimestampInput,
)

router = APIRouter(
    tags=["time"],
    responses={400: {"description": "Invalid input"}},
)


@router.get("/get_current_utc_time", summary="Current UTC time")
def get_current_utc():
    """Returns the current time in UTC in ISO format."""
    return {"utc": datetime.utcnow().replace(tzinfo=timezone.utc).isoformat()}


@router.get("/get_current_local_time", summary="Current Local Time")
def get_current_local():
    """Returns the current time in local timezone in ISO format."""
    return {"local_time": datetime.now().isoformat()}


@router.post("/format_time", summary="Format current time")
def format_current_time(data: FormatTimeInput = Body(...)):
    """Return the current time formatted for a specific timezone and format."""
    try:
        tz = pytz.timezone(data.timezone)
    except Exception:
        raise HTTPException(
            status_code=400, detail=f"Invalid timezone: {data.timezone}"
        )
    now = datetime.now(tz)
    try:
        return {"formatted_time": now.strftime(data.format)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid format string: {e}")


@router.post("/convert_time", summary="Convert between timezones")
def convert_time(data: ConvertTimeInput = Body(...)):
    """Convert a timestamp from one timezone to another."""
    try:
        from_zone = pytz.timezone(data.from_tz)
        to_zone = pytz.timezone(data.to_tz)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid timezone: {e}")

    try:
        dt = dateutil_parser.parse(data.timestamp)
        if dt.tzinfo is None:
            dt = from_zone.localize(dt)
        else:
            dt = dt.astimezone(from_zone)
        converted = dt.astimezone(to_zone)
        return {"converted_time": converted.isoformat()}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid timestamp: {e}")


@router.post("/elapsed_time", summary="Time elapsed between timestamps")
def elapsed_time(data: ElapsedTimeInput = Body(...)):
    """Calculate the difference between two timestamps in chosen units."""
    try:
        start_dt = dateutil_parser.parse(data.start)
        end_dt = dateutil_parser.parse(data.end)
        delta = end_dt - start_dt
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid timestamps: {e}")

    seconds = delta.total_seconds()
    result = {
        "seconds": seconds,
        "minutes": seconds / 60,
        "hours": seconds / 3600,
        "days": seconds / 86400,
    }
    return {"elapsed": result[data.units], "unit": data.units}


@router.post("/parse_timestamp", summary="Parse and normalize timestamps")
def parse_timestamp(data: ParseTimestampInput = Body(...)):
    """Parse human-friendly input timestamp and return standardized UTC ISO time."""
    try:
        tz = pytz.timezone(data.timezone)
        dt = dateutil_parser.parse(data.timestamp)
        if dt.tzinfo is None:
            dt = tz.localize(dt)
        dt_utc = dt.astimezone(pytz.utc)
        return {"utc": dt_utc.isoformat()}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not parse: {e}")


@router.get("/list_time_zones", summary="All valid time zones")
def list_time_zones():
    """Return a list of all valid IANA time zones."""
    return pytz.all_timezones
