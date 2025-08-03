from fake_useragent import UserAgent
from faker import Faker
import json
import requests
from pydantic import BaseModel
from urllib.parse import urlparse
import streamlit as st


YC_ALGOLIA_URL = f"https://45bwzj1sgc-2.algolianet.com/1/indexes/*/queries?x-algolia-agent=Algolia%20for%20JavaScript%20(3.35.1)%3B%20Browser%3B%20JS%20Helper%20(3.16.1)&x-algolia-application-id=45BWZJ1SGC&x-algolia-api-key=MjBjYjRiMzY0NzdhZWY0NjExY2NhZjYxMGIxYjc2MTAwNWFkNTkwNTc4NjgxYjU0YzFhYTY2ZGQ5OGY5NDMxZnJlc3RyaWN0SW5kaWNlcz0lNUIlMjJZQ0NvbXBhbnlfcHJvZHVjdGlvbiUyMiUyQyUyMllDQ29tcGFueV9CeV9MYXVuY2hfRGF0ZV9wcm9kdWN0aW9uJTIyJTVEJnRhZ0ZpbHRlcnM9JTVCJTIyeWNkY19wdWJsaWMlMjIlNUQmYW5hbHl0aWNzVGFncz0lNUIlMjJ5Y2RjJTIyJTVE"


class YcScrapedCompany(BaseModel):
    id: int
    name: str
    website: str
    all_locations: str
    long_description: str
    team_size: int | None
    industry: str
    tags: list[str]
    top_company: bool = False
    isHiring: bool
    nonprofit: bool = False
    batch: str
    status: str
    industries: list[str]
    regions: list[str]
    stage: str
    one_liner: str


@st.cache_data(ttl=4 * 3600)
def scrape_yc_algolia() -> list[YcScrapedCompany]:
    useragent_faker = UserAgent()
    faker = Faker()
    params = {
        "requests": [
            {
                "indexName": "YCCompany_production",
                "params": 'query=&hitsPerPage=1000&filters=batch:"Summer 2025"&restrictIndices=["YCCompany_production"]&tagFilters=[["ycdc_public"]]&analyticsTags=["ycdc"]',
            }
        ]
    }
    headers = {
        "accept": "application/json",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": faker.language_code()
        + ","
        + ",".join([f"{faker.language_code()};q=0.{i}" for i in range(9, 4, -1)]),
        "connection": "keep-alive",
        "content-type": "application/x-www-form-urlencoded",
        "host": urlparse(YC_ALGOLIA_URL).netloc,
        "origin": "https://www.ycombinator.com",
        "referer": "https://www.ycombinator.com/",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "cross-site",
        "user-agent": useragent_faker.random,
    }
    print(f"Requesting YC")
    response = requests.post(
        url=YC_ALGOLIA_URL,
        headers=headers,
        data=json.dumps(params),
        timeout=10,
    )
    print("Yc requesting ended")
    try:
        response.raise_for_status()
    except:
        print(f"Ошибка при загрузке YC {response.status_code} {response.text}")
        raise
    return [
        YcScrapedCompany.model_validate(c)
        for c in response.json()["results"][0]["hits"]
    ]
