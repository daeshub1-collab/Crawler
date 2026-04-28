from .base_crawler import BaseCrawler
from .ustr_crawler import USTRCrawler
from .cbp_crawler import CbpCrawler
from .federalregister_crawler import FederalRegisterCrawler
from .plasticsnews_crawler import PlasticsNewsCrawler
from .mexicobusiness_crawler import MexicoBusinessCrawler
from .canplastics_crawler import CanPlasticsCrawler
from .kotra_crawler import KotraCrawler
from .kita_crawler import KitaCrawler

__all__ = [
    "BaseCrawler",
    "USTRCrawler",
    "CbpCrawler",
    "FederalRegisterCrawler",
    "PlasticsNewsCrawler",
    "MexicoBusinessCrawler",
    "CanPlasticsCrawler",
    "KotraCrawler",
    "KitaCrawler",
    "get_all_crawlers",
]

# --site 옵션에서 사용할 코드명 → 클래스 매핑
_CRAWLER_MAP = {
    "ustr":             USTRCrawler,
    "cbp":              CbpCrawler,
    "federalregister":  FederalRegisterCrawler,
    "plasticsnews":     PlasticsNewsCrawler,
    "mexicobusiness":   MexicoBusinessCrawler,
    "canplastics":      CanPlasticsCrawler,
    "kotra":            KotraCrawler,
    "kita":             KitaCrawler,
}


def get_all_crawlers(site: str = None) -> list:
    """
    모든 크롤러 인스턴스 리스트를 반환한다.

    Args:
        site: 특정 크롤러 코드명 (예: 'ustr'). None이면 전체 반환.

    Returns:
        list[BaseCrawler]

    Raises:
        ValueError: 알 수 없는 site 코드
    """
    if site:
        cls = _CRAWLER_MAP.get(site.lower())
        if not cls:
            valid = ", ".join(_CRAWLER_MAP.keys())
            raise ValueError(f"알 수 없는 사이트 코드: '{site}'. 사용 가능: {valid}")
        return [cls()]
    return [cls() for cls in _CRAWLER_MAP.values()]
