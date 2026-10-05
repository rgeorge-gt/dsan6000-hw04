import os

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import psutil

import duckdb


def compute_memory_usage(filepath=None):
    process = psutil.Process()
    mem_usage_mb = process.memory_info().rss / (1024 ** 2)
    mem_usage_str = f'{mem_usage_mb:.2f} MB'

    if filepath:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as outfile:
            outfile.write(mem_usage_str)

    return mem_usage_mb


if __name__ == "__main__":
    memory_pre = compute_memory_usage('outputs/hw04-2-duckdb-pre.txt')
    print(f'{memory_pre:.2f} MB used pre-computation')

    s3_uri = 's3://dsan6000-data/acled_civilian_events.parquet'

    con = duckdb.connect()
    con.execute("INSTALL httpfs;")
    con.execute("LOAD httpfs;")

    yearly_count_query = f"""
    SELECT
        year,
        SUM(fatalities) AS fatalities
    FROM '{s3_uri}'
    WHERE year BETWEEN 2018 AND 2024
    GROUP BY year
    ORDER BY year
    """

    result_df = con.execute(yearly_count_query).df()

    print(result_df)

    sns.lineplot(
        data=result_df,
        x="year",
        y="fatalities",
        marker="o"
    )

    plt.title("ACLED: Yearly Fatality Counts (DuckDB)")
    plt.tight_layout()
    plt.savefig("images/yearly_fatalities_duckdb.svg")

    memory_post = compute_memory_usage('outputs/hw04-2-duckdb-post.txt')
    print(f'{memory_post:.2f} MB used post-computation')

    memory_diff = memory_post - memory_pre
    print(f'=> {memory_diff:.2f} MB added via DuckDB operation')

    with open('outputs/hw04-2-duckdb-diff.txt', 'w', encoding='utf-8') as outfile:
        outfile.write(f'{memory_diff:.2f} MB')