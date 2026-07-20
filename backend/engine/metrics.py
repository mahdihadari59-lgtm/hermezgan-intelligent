#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
HDP Metrics Engine v3.2

Performance Monitor
"""

import time
import threading


class PerformanceMetrics:

    def __init__(self):

        self.lock = threading.RLock()

        self.total_queries = 0

        self.total_results = 0

        self.total_time = 0.0

        self.engine_stats = {
            "intent": [],
            "fts": [],
            "graph": [],
            "synonym": [],
            "rerank": []
        }

    def start(self):

        return time.time()

    def stop(self, start):

        return round(
            time.time() - start,
            6
        )

    def record_query(
        self,
        elapsed,
        result_count
    ):

        with self.lock:

            self.total_queries += 1

            self.total_time += elapsed

            self.total_results += result_count

    def record_engine(
        self,
        engine,
        elapsed
    ):

        with self.lock:

            if engine not in self.engine_stats:

                self.engine_stats[engine] = []

            self.engine_stats[engine].append(elapsed)

    def average_engine(
        self,
        engine
    ):

        values = self.engine_stats.get(engine, [])

        if not values:

            return 0.0

        return round(

            sum(values) / len(values),

            6

        )

    def summary(self):

        with self.lock:

            avg_time = 0

            avg_results = 0

            if self.total_queries:

                avg_time = round(

                    self.total_time /

                    self.total_queries,

                    6

                )

                avg_results = round(

                    self.total_results /

                    self.total_queries,

                    2

                )

            engines = {}

            for name in self.engine_stats:

                engines[name] = self.average_engine(name)

            return {

                "queries": self.total_queries,

                "average_time": avg_time,

                "average_results": avg_results,

                "engine_average": engines

            }

    def reset(self):

        with self.lock:

            self.total_queries = 0

            self.total_results = 0

            self.total_time = 0

            for key in self.engine_stats:

                self.engine_stats[key].clear()


if __name__ == "__main__":

    m = PerformanceMetrics()

    s = m.start()

    time.sleep(0.2)

    e = m.stop(s)

    m.record_query(e, 12)

    m.record_engine("fts", 0.08)

    m.record_engine("graph", 0.31)

    print(m.summary())

