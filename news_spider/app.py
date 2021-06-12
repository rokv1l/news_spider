from multiprocessing import Process, freeze_support

import config
import spider_modules
from src.sсhedule_mp import IntervalJob, Scheduler

freeze_support()


def main():
    parsers = [
        spider_modules.mskagency.mskagency_parser, spider_modules.tass.tass_parser, spider_modules.vm.vm_parser,
        spider_modules.m24.m24_parser, spider_modules.icmos.icmos_parser, spider_modules.mockva.mockva_parser,
        spider_modules.riamo.riamo_parser, spider_modules.ria.ria_parser, spider_modules.moslenta.moslenta_parser,
        spider_modules.kp.kp_parser, spider_modules.echo.echo_parser, spider_modules.rbc.rbc_parser,
        spider_modules.rt.rt_parser, spider_modules.lenta.lenta_parser
    ]
    for parser in parsers:
        process = Process(target=parser)
        process.start()
    scheduler = Scheduler()
    scheduler.add_job(IntervalJob('mskagency', spider_modules.mskagency.mskagency_parser, delay=config.run_jobs_delay))
    scheduler.add_job(IntervalJob('tass', spider_modules.tass.tass_parser, delay=config.run_jobs_delay))
    scheduler.add_job(IntervalJob('vm', spider_modules.vm.vm_parser, delay=config.run_jobs_delay))
    scheduler.add_job(IntervalJob('m24', spider_modules.m24.m24_parser, delay=config.run_jobs_delay))
    scheduler.add_job(IntervalJob('icmos', spider_modules.icmos.icmos_parser, delay=config.run_jobs_delay))
    scheduler.add_job(IntervalJob('mockva', spider_modules.mockva.mockva_parser, delay=config.run_jobs_delay))
    scheduler.add_job(IntervalJob('riamo', spider_modules.riamo.riamo_parser, delay=config.run_jobs_delay))
    scheduler.add_job(IntervalJob('ria', spider_modules.ria.ria_parser, delay=config.run_jobs_delay))
    scheduler.add_job(IntervalJob('moslenta', spider_modules.moslenta.moslenta_parser, delay=config.run_jobs_delay))
    scheduler.add_job(IntervalJob('kp', spider_modules.kp.kp_parser, delay=config.run_jobs_delay))
    scheduler.add_job(IntervalJob('echo', spider_modules.echo.echo_parser, delay=config.run_jobs_delay))
    scheduler.add_job(IntervalJob('rbc', spider_modules.rbc.rbc_parser, delay=config.run_jobs_delay))
    scheduler.add_job(IntervalJob('rt', spider_modules.rt.rt_parser, delay=config.run_jobs_delay))
    scheduler.add_job(IntervalJob('lenta', spider_modules.lenta.lenta_parser, delay=config.run_jobs_delay))
    scheduler.run_pending()


if __name__ == '__main__':
    main()
