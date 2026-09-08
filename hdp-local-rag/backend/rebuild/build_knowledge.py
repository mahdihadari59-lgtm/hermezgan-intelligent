#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
==========================================================
HDP Knowledge Builder
Pipeline اصلی ساخت پایگاه دانش
==========================================================
"""

import sqlite3
from pathlib import Path

from parser import KnowledgeParser
from normalizer import normalize
from keyword_extractor import extract_keywords
from classifier import KnowledgeClassifier


class KnowledgeBuilder:

    def __init__(self, json_file, db_file):

        self.json_file = json_file
        self.db_file = db_file

        self.parser = KnowledgeParser(json_file)
        self.classifier = KnowledgeClassifier()

        self.conn = sqlite3.connect(db_file)
        self.conn.row_factory = sqlite3.Row

    # ---------------------------------------------------

    def process_record(self, record):

        record.title = normalize(record.title)
        record.content = normalize(record.content)

        record.keywords = extract_keywords(
            record.title + " " + record.content
        )

        record = self.classifier.classify(record)

        return record

    # ---------------------------------------------------

    def save_record(self, record):

        self.conn.execute("""

        INSERT INTO knowledge(

            title,
            content,
            category,
            city,
            entity_type,
            intent,
            main_intent,
            sub_intent,
            topic,
            keywords,
            confidence,
            source

        )

        VALUES(

            ?,?,?,?,?,?,?,?,?,?,?,?

        )

        """,

        (

            record.title,
            record.content,
            record.category,
            record.city,
            record.entity_type,
            record.intent,
            record.main_intent,
            record.sub_intent,
            record.topic,
            ",".join(record.keywords),
            record.confidence,
            record.source

        )

        )

    # ---------------------------------------------------

    def build(self):

        records = self.parser.parse()

        total = len(records)

        print(f"\nLoaded {total} records\n")

        for index, record in enumerate(records, start=1):

            record = self.process_record(record)

            self.save_record(record)

            if index % 500 == 0:

                print(f"{index}/{total}")

        self.conn.commit()

        print("\nFinished Successfully")

    # ---------------------------------------------------

    def close(self):

        self.conn.close()


# ======================================================

if __name__ == "__main__":

    JSON_FILE = "/data/data/com.termux/files/home/hormozgan-driver-pro121/hdp_flask_app/data/hormozgan_knowledge.json"

    DB_FILE = "/data/data/com.termux/files/home/ai-system/hdp_x1/development/data/hdp_v2.db"

    builder = KnowledgeBuilder(

        JSON_FILE,
        DB_FILE

    )

    builder.build()

    builder.close()
