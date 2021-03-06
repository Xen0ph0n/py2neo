#/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2011-2013, Nigel Small
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
import unittest

from py2neo import neo4j
from py2neo.calendar import GregorianCalendar

logging.basicConfig(
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
    level=logging.DEBUG,
)

def default_graph_db():
    return neo4j.GraphDatabaseService("http://localhost:7474/db/data/")

# Grab a handle to an index for linking to time data
TIME = neo4j.GraphDatabaseService().get_or_create_index(neo4j.Node, "TIME")


class TestExampleCode(unittest.TestCase):

    def test_example_code_runs(self):
        from py2neo import neo4j
        from py2neo.calendar import GregorianCalendar

        graph_db = neo4j.GraphDatabaseService()
        time_index = graph_db.get_or_create_index(neo4j.Node, "TIME")
        calendar = GregorianCalendar(time_index)

        alice, birth, death = graph_db.create(
            {"name": "Alice"},
            (0, "BORN", calendar.day(1800, 1, 1)),
            (0, "DIED", calendar.day(1900, 12, 31)),
        )

        assert birth.end_node["year"] == 1800
        assert birth.end_node["month"] == 1
        assert birth.end_node["day"] == 1

        assert death.end_node["year"] == 1900
        assert death.end_node["month"] == 12
        assert death.end_node["day"] == 31


class TestDays(unittest.TestCase):

    def setUp(self):
        self.calendar = GregorianCalendar(TIME)

    def test_can_get_day_node(self):
        christmas = self.calendar.day(2000, 12, 25)
        assert isinstance(christmas, neo4j.Node)
        assert christmas["year"] == 2000
        assert christmas["month"] == 12
        assert christmas["day"] == 25

    def test_will_always_get_same_day_node(self):
        first_christmas = self.calendar.day(2000, 12, 25)
        for i in range(100):
            next_christmas = self.calendar.day(2000, 12, 25)
            assert next_christmas == first_christmas

    def test_can_get_different_day_nodes(self):
        christmas = self.calendar.day(2000, 12, 25)
        boxing_day = self.calendar.day(2000, 12, 26)
        assert christmas != boxing_day


class TestMonths(unittest.TestCase):

    def setUp(self):
        self.calendar = GregorianCalendar(TIME)

    def test_can_get_month_node(self):
        december = self.calendar.month(2000, 12)
        assert isinstance(december, neo4j.Node)
        assert december["year"] == 2000
        assert december["month"] == 12

    def test_will_always_get_same_month_node(self):
        first_december = self.calendar.month(2000, 12)
        for i in range(100):
            next_december = self.calendar.month(2000, 12)
            assert next_december == first_december

    def test_can_get_different_month_nodes(self):
        december = self.calendar.month(2000, 12)
        january = self.calendar.month(2001, 1)
        assert december != january


class TestYears(unittest.TestCase):

    def setUp(self):
        self.calendar = GregorianCalendar(TIME)

    def test_can_get_year_node(self):
        millennium = self.calendar.year(2000)
        assert isinstance(millennium, neo4j.Node)
        assert millennium["year"] == 2000

    def test_will_always_get_same_month_node(self):
        first_millennium = self.calendar.year(2000)
        for i in range(100):
            next_millennium = self.calendar.year(2000)
            assert next_millennium == first_millennium

    def test_can_get_different_year_nodes(self):
        millennium_2000 = self.calendar.year(2000)
        millennium_2001 = self.calendar.year(2001)
        assert millennium_2000 != millennium_2001


class TestDateRanges(unittest.TestCase):

    def setUp(self):
        self.calendar = GregorianCalendar(TIME)

    def test_can_get_date_range(self):
        xmas_year = self.calendar.date_range((2000, 12, 25), (2001, 12, 25))
        assert isinstance(xmas_year, neo4j.Node)
        assert xmas_year["start_date"] == "2000-12-25"
        assert xmas_year["end_date"] == "2001-12-25"
        rels = xmas_year.get_relationships(neo4j.Direction.OUTGOING, "START_DATE")
        assert len(rels) == 1
        assert rels[0].end_node == self.calendar.date((2000, 12, 25))
        assert rels[0].end_node == self.calendar.day(2000, 12, 25)
        rels = xmas_year.get_relationships(neo4j.Direction.OUTGOING, "END_DATE")
        assert len(rels) == 1
        assert rels[0].end_node == self.calendar.date((2001, 12, 25))
        assert rels[0].end_node == self.calendar.day(2001, 12, 25)

    def test_will_always_get_same_date_range_node(self):
        range1 = self.calendar.date_range((2000, 12, 25), (2001, 12, 25))
        range2 = self.calendar.date_range((2000, 12, 25), (2001, 12, 25))
        assert range1 == range2

    def test_can_get_different_date_range_nodes(self):
        range1 = self.calendar.date_range((2000, 12, 25), (2001, 12, 25))
        range2 = self.calendar.date_range((2000, 1, 1), (2000, 12, 31))
        assert range1 != range2

    def test_single_day_range(self):
        range = self.calendar.date_range((2000, 12, 25), (2000, 12, 25))
        assert range == self.calendar.day(2000, 12, 25)

    def test_range_within_month(self):
        advent = self.calendar.date_range((2000, 12, 1), (2000, 12, 24))
        rels = advent.get_relationships(neo4j.Direction.INCOMING, "DATE_RANGE")
        assert len(rels) == 1
        assert rels[0].start_node == self.calendar.month(2000, 12)
        rels = advent.get_relationships(neo4j.Direction.OUTGOING, "START_DATE")
        assert len(rels) == 1
        assert rels[0].end_node == self.calendar.date((2000, 12, 1))
        assert rels[0].end_node == self.calendar.day(2000, 12, 1)
        rels = advent.get_relationships(neo4j.Direction.OUTGOING, "END_DATE")
        assert len(rels) == 1
        assert rels[0].end_node == self.calendar.date((2000, 12, 24))
        assert rels[0].end_node == self.calendar.day(2000, 12, 24)

    def test_range_within_year(self):
        range = self.calendar.date_range((2000, 4, 10), (2000, 12, 24))
        rels = range.get_relationships(neo4j.Direction.INCOMING, "DATE_RANGE")
        assert len(rels) == 1
        assert rels[0].start_node == self.calendar.year(2000)
        rels = range.get_relationships(neo4j.Direction.OUTGOING, "START_DATE")
        assert len(rels) == 1
        assert rels[0].end_node == self.calendar.date((2000, 4, 10))
        assert rels[0].end_node == self.calendar.day(2000, 4, 10)
        rels = range.get_relationships(neo4j.Direction.OUTGOING, "END_DATE")
        assert len(rels) == 1
        assert rels[0].end_node == self.calendar.date((2000, 12, 24))
        assert rels[0].end_node == self.calendar.day(2000, 12, 24)


if __name__ == "__main__":
    unittest.main()
