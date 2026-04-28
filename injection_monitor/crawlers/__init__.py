from crawlers.ustr_crawler import UstrCrawler
from crawlers.cbp_crawler import CbpCrawler
from crawlers.federalregister_crawler import FederalRegisterCrawler
from crawlers.plasticsnews_crawler import PlasticsNewsCrawler
from crawlers.mexicobusiness_crawler import MexicoBusinessCrawler
from crawlers.canplastics_crawler import CanPlasticsCrawler
from crawlers.kotra_crawler import KotraCrawler
from crawlers.kita_crawler import KitaCrawler

ALL_CRAWLERS = [
    UstrCrawler,
    CbpCrawler,
    FederalRegisterCrawler,
    PlasticsNewsCrawler,
    MexicoBusinessCrawler,
    CanPlasticsCrawler,
    KotraCrawler,
    KitaCrawler,
]