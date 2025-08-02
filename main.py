import os
from data_scrapers.linkedin import scrape_linkedin
from data_scrapers.yc import scrape_yc_algolia
from utils import normalize_name


import pandas as pd
import plotly.express as px
import streamlit as st
from wordcloud import WordCloud


import re


st.set_page_config(layout="wide")
st.title("Y Combinator Summer 2025 Companies")
with st.spinner("Loading YCombinator data..."):
    yc_data = scrape_yc_algolia()
with st.spinner("Searching LinkedIn..."):
    linkedin_data = scrape_linkedin(os.environ["SEARCHAPI_KEY"])
st.text(f"Found YCombinator: {len(yc_data)}, LinkedIn: {len(linkedin_data)}")

df = pd.DataFrame(
    [
        {
            "Company": x.name,
            "Website": x.website,
            "Batch": x.batch,
            "Industry": ", ".join(x.industries),
            "Description": x.long_description,
            "Hiring?": "✅" if x.isHiring else "❌",
            "Team Size": x.team_size,
            "Regions": x.regions,
            "LinkedIn URL": "",
            "Tags": x.tags,
            "LinkedIn Followers": None,
        }
        for x in yc_data
    ]
)

# Сопоставляем данные
linkedin_urls_map = {
    normalize_name(x["company"]): x["linkedin_url"] for x in linkedin_data
}
df["LinkedIn URL"] = df["Company"].apply(
    lambda x: linkedin_urls_map.get(normalize_name(x), "")
)
linkedin_followers_map = {
    normalize_name(x["company"]): x["linkedin_followers"] for x in linkedin_data
}
df["LinkedIn Followers"] = df["Company"].apply(
    lambda x: linkedin_followers_map.get(normalize_name(x), None)
)

# Добавляем компании только из LinkedIn
linkedin_only = []
for item in linkedin_data:
    norm_name = normalize_name(item["company"])
    if norm_name not in df["Company"].apply(normalize_name).values:
        linkedin_only.append(
            {
                "Company": item["company"],
                "Website": None,
                "Batch": None,
                "Industry": None,
                "Description": item.get("snippet", ""),
                "Hiring?": None,
                "Team Size": None,
                "Tags": None,
                "Regions": [],
                "LinkedIn URL": item["linkedin_url"],
                "LinkedIn Followers": item["linkedin_followers"],
            }
        )

final_df = pd.concat([df, pd.DataFrame(linkedin_only)], ignore_index=True)

st.dataframe(
    final_df,
    column_config={
        "name": "Company",
        "batch": "Batch",
        "url": st.column_config.LinkColumn("Website"),
        "description": "Description",
    },
    hide_index=True,
    use_container_width=True,
)

df_exploded_industries = final_df.assign(
    Industry=final_df["Industry"].str.split(", ")
).explode("Industry")

fig = px.bar(
    df_exploded_industries["Industry"].value_counts().reset_index(),
    x="count",
    y="Industry",
    title="Industry distribution of companies",
    orientation="h",
)
st.plotly_chart(fig, use_container_width=True)

df_exploded_regions = final_df.assign(Regions=final_df["Regions"].to_list()).explode(
    "Regions"
)

fig = px.bar(
    df_exploded_regions["Regions"].value_counts().reset_index(),
    x="count",
    y="Regions",
    title="Regional distribution of companies",
    orientation="h",
)
st.plotly_chart(fig, use_container_width=True)

fig = px.histogram(
    final_df[final_df["Team Size"].notna()],
    x="Team Size",
    nbins=10,
    title="Team size distribution",
    labels={"Team Size": "Number of employees"},
)
st.plotly_chart(fig)

fig = px.histogram(
    final_df[final_df["LinkedIn Followers"].notna()],
    x="LinkedIn Followers",
    nbins=10,
    title="Follower count",
    labels={"LinkedIn Followers": "Follower count"},
)
st.plotly_chart(fig)

tags_wordcloud = WordCloud(width=800, height=400).generate(
    " ".join([" ".join(ts) for ts in final_df["Tags"].dropna()])
)
st.image(
    tags_wordcloud.to_array(),
    caption="Tag cloud",
    use_container_width=True,
)

text = re.sub(
    r"(?i)\b(yc|s25|followers|linkedin)\b",
    "",
    " ".join(final_df["Description"].dropna()),
)
wordcloud = WordCloud(width=800, height=400).generate(text)
st.image(
    wordcloud.to_array(),
    caption="Keywords in company descriptions",
    use_container_width=True,
)
