import logging
import datetime
from multiprocessing import Process, freeze_support
from time import sleep
from typing import Callable, List, Tuple

logging.basicConfig(filename='data.log', filemode='w')
freeze_support()


class ScheduleValueError(Exception):
    pass


class CancelJob(Exception):
    """Если вернуть это исключение из джобы во время работы то она автоматически удалится"""
    pass


class Scheduler:
    def __init__(self):
        self.jobs_queue = list()
    
    def run_pending(self):
        while True:
            runnable_jobs = (job for job in self.jobs_queue if job.should_run)
            for job in sorted(runnable_jobs):
                self._run_job(job)
            sleep(1)

    def add_job(self, job):
        self.jobs_queue.append(job)

    def clear(self, job):
        self.jobs_queue = list()

    def cancel_job(self, job):
        try:
            logging.debug('Cancelling job "%s"', str(job.name))
            self.jobs_queue.remove(job)
        except ValueError:
            logging.debug('Cancelling not-scheduled job "%s"', str(job.name))

    def _run_job(self, job):
        ret = job._run()
        if isinstance(ret, CancelJob) or ret is CancelJob:
            self.cancel_job(job)

    @property
    def next_run(self):
        if not self.jobs_queue:
            return None
        else:
            return min(self.jobs_queue).next_run

    def get_jobs_by_name(self, name):
        return [job for job in self.jobs_queue if job.name == name]


class IntervalJob:
    def __init__(self, name: str, method: Callable, args: Tuple = tuple(), delay: int = 1):
        self.name = name
        self.method_link = method
        self.method_args = args
        self.delay = delay
        self.last_run = None
        self.next_run = datetime.datetime.fromtimestamp(datetime.datetime.now().timestamp() + delay)
        self.status = True

    def __lt__(self, other):
        return self.next_run < other.next_run

    def _run(self):
        try:
            process = Process(target=self.method_link, args=self.method_args)
            process.start()
            self.last_run = self.next_run
            self.next_run = datetime.datetime.fromtimestamp(self.next_run.timestamp() + self.delay)
        except Exception as e:
            logging.warning('An exception in job', exc_info=True)
    
    @property
    def should_run(self):
        assert self.next_run is not None, "must run _schedule_next_run before"
        return datetime.datetime.now() >= self.next_run


class CalendarJob():
    def __init__(self, name: str, method: Callable, args: Tuple, run_weekdays: List):
        self.name = name
        self.method_link = method
        self.method_args = args
        if len(run_weekdays) != 7 or run_weekdays == [None for i in range(7)]:
            raise SсheduleValueError(
                f'Invalid run_weekdays list {run_weekdays}'
            )
        # run_weekdays Должен быть списком из 7 элементов datetime.time или None, где первый обьект соответствует времени запуска
        # в понедельник, второй в вторник и последний в воскресенье. При этом None означает что в этот день недели запуска не будет
        self.run_weekdays = run_weekdays
        self.last_run = None
        self.next_run = None
        self._schedule_next_run()
        self.status = True

    def __lt__(self, other):
        return self.next_run < other.next_run

    def _run(self):
        try:
            process = Process(target=self.method_link, args=self.method_args)
            process.start()
            self.last_run = datetime.datetime.now()
            self._schedule_next_run()
        except Exception as e:
            logging.warning('An exception in job', exc_info=True)

    def _schedule_next_run(self):
        dt_now = datetime.datetime.now()
        days_offset = 0
        while True:
            run_date = dt_now.date() + datetime.timedelta(**{'days': days_offset})
            run_weekday = run_date.weekday()
            run_time = self.run_weekdays[run_weekday]
            if run_time is None:
                days_offset += 1
                continue
            next_run = datetime.datetime(
                year=run_date.year, 
                month=run_date.month,
                day=run_date.day,
                hour=run_time.hour,
                minute=run_time.minute,
                second=run_time.second,
                microsecond=run_time.microsecond
            )
            if next_run < dt_now:
                days_offset += 1
                continue
            self.next_run = next_run
            break

    @property
    def should_run(self):
        assert self.next_run is not None, "must run _schedule_next_run before"
        return datetime.datetime.now() >= self.next_run