from spider_modules.mskagency import mskagency_parser
from spider_modules.tass import tass_parser
from spider_modules.vm import vm_parser
from spider_modules.m24 import m24_parser
from spider_modules.icmos import icmos_parser
from spider_modules.mockva import mockva_parser
from src.sсhedule_mp import IntervalJob, Scheduler


def main():
    scheduler = Scheduler()
    scheduler.add_job(IntervalJob('mskagency', mskagency_parser, delay=60*30))
    scheduler.add_job(IntervalJob('tass', tass_parser, delay=60*30))
    scheduler.add_job(IntervalJob('vm', vm_parser, delay=60*30))
    scheduler.add_job(IntervalJob('m24', m24_parser, delay=60*30))
    scheduler.add_job(IntervalJob('icmos', icmos_parser, delay=60*30))
    scheduler.add_job(IntervalJob('mockva', mockva_parser, delay=60*30))
    scheduler.run_pending()


if __name__ == '__main__':
    main()
