from multiprocessing import Process, freeze_support

import config
from spider_modules import aif, bfm, echo, icmos, kommersant, kp, lenta, m24, mbk_news, mk, mockva, moslenta, mskagency
from spider_modules import novayagazeta, pravda, rbc, regnum, ria, riamo, rt, tass, vm, interfax, rg
from src.sсhedule_mp import IntervalJob, Scheduler

freeze_support()


def main():
    parsers = [
        mskagency.mskagency_parser, tass.tass_parser, vm.vm_parser, m24.m24_parser, icmos.icmos_parser,
        mockva.mockva_parser, riamo.riamo_parser, ria.ria_parser, moslenta.moslenta_parser, kp.kp_parser,
        echo.echo_parser, rbc.rbc_parser, rt.rt_parser, lenta.lenta_parser, aif.aif_parser, mk.mk_parser,
        mbk_news.mbk_parser, kommersant.kommersant_parser, regnum.regnum_parser, novayagazeta.novayagazeta_parser,
        pravda.pravda_parser, bfm.bfm_parser, interfax.interfax_parser, rg.rg_parser,
    ]
    scheduler = Scheduler()
    for parser in parsers:
        process = Process(target=parser)
        process.start()
        scheduler.add_job(IntervalJob(parser.__name__, parser, delay=config.run_jobs_delay))
    scheduler.run_pending()


if __name__ == '__main__':
    main()
