from spider_modules.mskagency import mskagency_parser
from src.sсhedule_mp import IntervalJob, Scheduler


def main():
    scheduler = Scheduler()
    scheduler.add_job(IntervalJob('mskagency', mskagency_parser, delay=120))
    scheduler.run_pending()


if __name__ == '__main__':
    main()
