#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
HDP Bridge v1

Example usage of DatabaseBridge.

This script demonstrates connecting:

    geo.db
        ↕
    hdp_v2.db

without copying any data.
"""

from pathlib import Path
import argparse

from config import GEO_DB, HDP_DB
from database_bridge import DatabaseBridge


def banner():

    print("=" * 60)
    print("HDP DATABASE BRIDGE EXAMPLE")
    print("=" * 60)
    print()


def print_databases(bridge):

    print("Geo DB")
    print(bridge.geo_db)

    print()

    print("Knowledge DB")
    print(bridge.knowledge_db)

    print()

    print("Attached")
    print(bridge.attached())

    print()

    print("Journal")
    print(bridge.journal_mode())

    print()

    print("Integrity")
    print(bridge.integrity_check())

    print()


# ==========================================================
# BASIC EXAMPLES
# ==========================================================

def example_status(bridge):

    print("=" * 60)
    print("BRIDGE STATUS")
    print("=" * 60)

    status = bridge.status()

    for key, value in status.items():
        print(f"{key:20} : {value}")

    print()


def example_tables(bridge):

    print("=" * 60)
    print("TABLES")
    print("=" * 60)

    print("\nMAIN")

    for table in bridge.tables("main"):
        print(" •", table)

    print("\nKNOWLEDGE")

    for table in bridge.tables("knowledge"):
        print(" •", table)

    print()


# ==========================================================
# SEARCH EXAMPLES
# ==========================================================

def example_search(bridge):

    print("=" * 60)
    print("SEARCH EXAMPLES")
    print("=" * 60)

    keyword = "بندرعباس"

    print(f"Searching for: {keyword}")

    try:

        results = bridge.search_everywhere(keyword)

        for section, rows in results.items():

            print()

            print(f"[{section}]")

            print(f"Rows: {len(rows)}")

            for row in rows[:5]:

                print(row)

    except Exception as e:

        print(e)


# ==========================================================
# QUERY EXAMPLES
# ==========================================================

def example_query(bridge):

    print("=" * 60)
    print("QUERY EXAMPLE")
    print("=" * 60)

    try:

        sql = """
        SELECT name
        FROM main.sqlite_master
        WHERE type='table'
        ORDER BY name
        """

        rows = bridge.query(sql)

        print(f"Tables found: {len(rows)}")

        for row in rows:
            print(" •", row["name"])

    except Exception as e:

        print("Query Error:", e)

    print()


# ==========================================================
# JOIN EXAMPLE
# ==========================================================

def example_join(bridge):

    print("=" * 60)
    print("JOIN EXAMPLE")
    print("=" * 60)

    sql = """
    SELECT
        k.title,
        r.relation_type,
        r.target_entity

    FROM knowledge.knowledge_relations r

    INNER JOIN knowledge.knowledge k

        ON k.title = r.source_entity

    LIMIT 10
    """

    try:

        rows = bridge.query(sql)

        print(f"Rows: {len(rows)}")

        for row in rows:

            print(row)

    except Exception as e:

        print("JOIN skipped:", e)

    print()


# ==========================================================
# TABLE INFORMATION
# ==========================================================

def example_table_info(bridge):

    print("=" * 60)
    print("TABLE INFORMATION")
    print("=" * 60)

    for schema in ("main", "knowledge"):

        print()

        print(schema.upper())

        try:

            tables = bridge.tables(schema)

            for table in tables[:10]:

                count = bridge.count(table, schema)

                print(f"{table:30} {count}")

        except Exception as e:

            print(e)

    print()


# ==========================================================
# MAIN
# ==========================================================

def main():

    parser = argparse.ArgumentParser(

        description="HDP Database Bridge Example"

    )

    parser.add_argument(

        "--geo",

        default=str(GEO_DB),

        help="Path to geo.db"

    )

    parser.add_argument(

        "--knowledge",

        default=str(HDP_DB),

        help="Path to hdp_v2.db"

    )

    parser.add_argument(

        "--query",

        default=None,

        help="Execute custom SQL"

    )

    parser.add_argument(

        "--status",

        action="store_true",

        help="Show bridge status"

    )

    parser.add_argument(

        "--tables",

        action="store_true",

        help="List all tables"

    )

    parser.add_argument(

        "--join",

        action="store_true",

        help="Run JOIN example"

    )

    parser.add_argument(

        "--search",

        action="store_true",

        help="Run search example"

    )

    args = parser.parse_args()

    banner()

    bridge = DatabaseBridge(

        geo_db=args.geo,

        knowledge_db=args.knowledge,

    )

    try:

        with bridge:

            if args.status:

                example_status(bridge)

            if args.tables:

                example_tables(bridge)

            if args.search:

                example_search(bridge)

            if args.join:

                example_join(bridge)

            if args.query:

                print("=" * 60)
                print("CUSTOM QUERY")
                print("=" * 60)

                rows = bridge.query(args.query)

                print(f"Rows: {len(rows)}")

                for row in rows:

                    print(row)

                print()

            if (

                not args.status

                and not args.tables

                and not args.search

                and not args.join

                and args.query is None

            ):

                example_status(bridge)
                example_tables(bridge)
                example_table_info(bridge)

    except Exception as e:

        print()

        print("Bridge FAILED")

        print(e)

        return 1

    print()

    print("Bridge Finished Successfully")

    return 0


# ==========================================================
# ENTRY POINT
# ==========================================================

if __name__ == "__main__":

    raise SystemExit(main())
