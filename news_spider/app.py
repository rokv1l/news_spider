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
        spider_modules.rt.rt_parser, spider_modules.lenta.lenta_parser, spider_modules.aif.aif_parser,
        spider_modules.mk.mk_parser, spider_modules.mbk_news.mbk_parser, spider_modules.kommersant.kommersant_parser,
        spider_modules.regnum.regnum_parser,
    ]
    scheduler = Scheduler()
    for parser in parsers:
        process = Process(target=parser)
        process.start()
        scheduler.add_job(IntervalJob(parser.__name__, parser, delay=config.run_jobs_delay))
    scheduler.run_pending()


if __name__ == '__main__':
    main()
