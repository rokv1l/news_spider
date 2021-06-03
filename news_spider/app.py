import config
from spider_modules.mskagency import mskagency_parser
from spider_modules.tass import tass_parser
from spider_modules.vm import vm_parser
from spider_modules.m24 import m24_parser
from spider_modules.icmos import icmos_parser
from spider_modules.mockva import mockva_parser
from spider_modules.riamo import riamo_parser
from spider_modules.ria import ria_parser
from spider_modules.moslenta import moslenta_parser
from src.sсhedule_mp import IntervalJob, Scheduler


def main():
    mskagency_parser()
    tass_parser()
    vm_parser()
    m24_parser()
    icmos_parser()
    mockva_parser()
    riamo_parser()
    ria_parser()
    moslenta_parser()
    scheduler = Scheduler()
    scheduler.add_job(IntervalJob('mskagency', mskagency_parser, delay=config.run_jobs_delay))
    scheduler.add_job(IntervalJob('tass', tass_parser, delay=config.run_jobs_delay))
    scheduler.add_job(IntervalJob('vm', vm_parser, delay=config.run_jobs_delay))
    scheduler.add_job(IntervalJob('m24', m24_parser, delay=config.run_jobs_delay))
    scheduler.add_job(IntervalJob('icmos', icmos_parser, delay=config.run_jobs_delay))
    scheduler.add_job(IntervalJob('mockva', mockva_parser, delay=config.run_jobs_delay))
    scheduler.add_job(IntervalJob('riamo', riamo_parser, delay=config.run_jobs_delay))
    scheduler.add_job(IntervalJob('ria', ria_parser, delay=config.run_jobs_delay))
    scheduler.add_job(IntervalJob('moslenta', moslenta_parser, delay=config.run_jobs_delay))
    scheduler.run_pending()


if __name__ == '__main__':
    main()
