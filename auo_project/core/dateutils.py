from datetime import datetime, timedelta
from typing import Optional

from dateutil.relativedelta import relativedelta
from fastapi import Query


class DateUtils:
    def __init__(
        self,
        time_unit: Optional[str] = Query(
            None,
            regex="1w|1m|3m|6m|12m|custom",
            title="檢測時間",
        ),
        start_date: Optional[str] = Query(None, title="開始時間"),
        end_date: Optional[str] = Query(None, title="結束時間"),
    ) -> None:
        if not (time_unit or start_date or end_date):
            time_unit = "1w"
        self.time_unit = time_unit
        self.start_date = start_date
        self.end_date = end_date

    def get_dates_by_time_unit(self, time_unit):
        today = datetime.utcnow() + timedelta(hours=8)
        if time_unit == "1w":
            return today - relativedelta(weeks=1), today
        elif time_unit == "1m":
            return today - relativedelta(months=1), today
        elif time_unit == "3m":
            return today - relativedelta(months=3), today
        elif time_unit == "6m":
            return today - relativedelta(months=6), today
        elif time_unit == "12m":
            return today - relativedelta(months=12), today
        else:
            raise Exception("Only accept 1w|1m|3m|6m|12m")

    def get_dates(self):
        if self.time_unit and self.time_unit != "custom":
            return self.get_dates_by_time_unit(self.time_unit)
        else:
            start_date = None
            end_date = None
            try:
                start_date = datetime.strptime(self.start_date, "%Y/%m/%d")
            except:
                pass
            try:
                end_date = datetime.strptime(self.end_date, "%Y/%m/%d")
            except:
                pass
            return start_date, end_date
