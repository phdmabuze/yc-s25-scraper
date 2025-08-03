from typing import TypedDict
from utils import google_search_linkedin_followers_to_number
import streamlit as st


import requests


import re


class LinkedInScrapedData(TypedDict):
    company: str
    linkedin_url: str
    snippet: str
    linkedin_followers: int | None


@st.cache_data(ttl=4 * 3600)
def scrape_linkedin(searchapi_key: str) -> list[LinkedInScrapedData]:
    payload = {
        "api_key": searchapi_key,
        "engine": "google",
        "q": 'site:linkedin.com/company/ intitle:"YC S25"',
        "num": 100,
    }
    response = requests.get("https://www.searchapi.io/api/v1/search", params=payload)
    results: list[LinkedInScrapedData] = []
    for item in response.json()["organic_results"]:
        if not (
            "yc s25" in item["title"].lower()
            and "linkedin.com/company" in item["link"].lower()
        ):
            continue
        company = re.sub(r"(?i)\s*\(?YC\s+[A-Z]?\d+\)?.*", "", item["title"])
        results.append(
            {
                "company": company,
                "linkedin_url": item["link"],
                "snippet": item["snippet"],
                "linkedin_followers": google_search_linkedin_followers_to_number(
                    item.get("displayed_link", "")
                ),
            }
        )
    return results
