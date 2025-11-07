#!/usr/bin/env python3
import unittest
from helper import parse_time, fmt_time
from schedule_generation import generate_base_schedule, apply_overrides, merge_adjacent

# Test 0: given example in the prompt and basic functionality checks
class TestPromptExample(unittest.TestCase):

    def setUp(self):
        # Sample schedule and overrides for testing
        self.schedule = {
            "users": ["alice", "bob", "charlie"],
            "handover_start_at": "2025-11-07T17:00:00Z",
            "handover_interval_days": 7
        }
        self.overrides = [
            {
                "user": "charlie",
                "start_at": "2025-11-10T17:00:00Z",
                "end_at": "2025-11-10T22:00:00Z"
            }
        ]
        self.from_dt = parse_time("2025-11-07T17:00:00Z")
        self.until_dt = parse_time("2025-11-21T17:00:00Z")
        self.expected = [
            {"user": "alice", "start_at": "2025-11-07T17:00:00Z", "end_at": "2025-11-10T17:00:00Z"},
            {"user": "charlie", "start_at": "2025-11-10T17:00:00Z", "end_at": "2025-11-10T22:00:00Z"},
            {"user": "alice", "start_at": "2025-11-10T22:00:00Z", "end_at": "2025-11-14T17:00:00Z"},
            {"user": "bob", "start_at": "2025-11-14T17:00:00Z", "end_at": "2025-11-21T17:00:00Z"},
        ]

    def test_generate_base_schedule(self):
        base_schedule = generate_base_schedule(self.schedule, self.from_dt, self.until_dt)
        self.assertEqual(len(base_schedule), 2)  # Expecting 2 entries
        self.assertEqual(base_schedule[0]["user"], "alice")
        self.assertEqual(base_schedule[1]["user"], "bob")

    def test_merge_adjacent(self):
        entries = [
            {"user": "alice", "start_at": parse_time("2025-11-07T17:00:00Z"), "end_at": parse_time("2025-11-14T17:00:00Z")},
            {"user": "alice", "start_at": parse_time("2025-11-14T17:00:00Z"), "end_at": parse_time("2025-11-21T17:00:00Z")}
        ]
        merged = merge_adjacent(entries)
        self.assertEqual(len(merged), 1)  # Expecting 1 merged entry
        self.assertEqual(merged[0]["end_at"], parse_time("2025-11-21T17:00:00Z"))
        
    def test_full_flow(self):
        base_schedule = generate_base_schedule(self.schedule, self.from_dt, self.until_dt)
        final_schedule = apply_overrides(base_schedule, self.overrides)
        merged = merge_adjacent(final_schedule)
        self.assertEqual(len(merged), len(self.expected))
        for i, exp in enumerate(self.expected):
            with self.subTest(i=i):
                self.assertEqual(merged[i]["user"], exp["user"])
                self.assertEqual(fmt_time(merged[i]["start_at"]), exp["start_at"])
                self.assertEqual(fmt_time(merged[i]["end_at"]), exp["end_at"])


# Test 1: more tricky edge case - overrides spanning multiple base shifts
class TestMultispanOverride(unittest.TestCase):

    def setUp(self):
        # Sample schedule and overrides for testing
        self.schedule = {
            "users": ["alice", "bob", "charlie"],
            "handover_start_at": "2025-11-07T17:00:00Z",
            "handover_interval_days": 2
        }
        self.overrides = [
            {
                "user": "maria",
                "start_at": "2025-11-8T17:00:00Z",
                "end_at": "2025-11-13T22:00:00Z"
            }
        ]
        self.from_dt = parse_time("2025-11-07T17:00:00Z")
        self.until_dt = parse_time("2025-11-15T17:00:00Z")
        self.expected = [
            {"user": "alice", "start_at": "2025-11-07T17:00:00Z", "end_at": "2025-11-08T17:00:00Z"},
            {"user": "maria", "start_at": "2025-11-08T17:00:00Z", "end_at": "2025-11-13T22:00:00Z"},
            {"user": "alice", "start_at": "2025-11-13T22:00:00Z", "end_at": "2025-11-15T17:00:00Z"}
        ]      
        
    def test_full_flow(self):
        base_schedule = generate_base_schedule(self.schedule, self.from_dt, self.until_dt)
        final_schedule = apply_overrides(base_schedule, self.overrides)
        print(final_schedule)
        merged = merge_adjacent(final_schedule)
        self.assertEqual(len(merged), len(self.expected))
        for i, exp in enumerate(self.expected):
            with self.subTest(i=i):
                self.assertEqual(merged[i]["user"], exp["user"])
                self.assertEqual(fmt_time(merged[i]["start_at"]), exp["start_at"])
                self.assertEqual(fmt_time(merged[i]["end_at"]), exp["end_at"])


# Test 2: edge case - overrides that exactly match base shift boundaries
class TestExactBoundaryOverride(unittest.TestCase):
    
    def setUp(self):
        # Sample schedule and overrides for testing
        self.schedule = {
            "users": ["alice", "bob", "charlie"],
            "handover_start_at": "2025-11-07T17:00:00Z",
            "handover_interval_days": 2
        }
        self.overrides = [
            {
                "user": "maria",
                "start_at": "2025-11-09T17:00:00Z",
                "end_at": "2025-11-11T17:00:00Z"
            }
        ]
        self.from_dt = parse_time("2025-11-07T17:00:00Z")
        self.until_dt = parse_time("2025-11-15T17:00:00Z")
        self.expected = [
            {"user": "alice", "start_at": "2025-11-07T17:00:00Z", "end_at": "2025-11-09T17:00:00Z"},
            {"user": "maria", "start_at": "2025-11-09T17:00:00Z", "end_at": "2025-11-11T17:00:00Z"},
            {"user": "charlie", "start_at": "2025-11-11T17:00:00Z", "end_at": "2025-11-13T17:00:00Z"},
            {"user": "alice", "start_at": "2025-11-13T17:00:00Z", "end_at": "2025-11-15T17:00:00Z"}
        ]
        
    def test_full_flow(self):
        base_schedule = generate_base_schedule(self.schedule, self.from_dt, self.until_dt)
        final_schedule = apply_overrides(base_schedule, self.overrides)
        merged = merge_adjacent(final_schedule)
        self.assertEqual(len(merged), len(self.expected))
        for i, exp in enumerate(self.expected):
            with self.subTest(i=i):  # makes failures easier to debug
                self.assertEqual(merged[i]["user"], exp["user"])
                self.assertEqual(fmt_time(merged[i]["start_at"]), exp["start_at"])
                self.assertEqual(fmt_time(merged[i]["end_at"]), exp["end_at"])

# Test 3.1: when time range far exceeds schedule entries
class TestFarFromSchedule(unittest.TestCase):

    def setUp(self):
        # Sample schedule and overrides for testing
        self.schedule = {
            "users": ["alice", "bob", "charlie"],
            "handover_start_at": "2025-11-07T17:00:00Z",
            "handover_interval_days": 7
        }
        self.overrides = []
        self.from_dt = parse_time("2025-12-01T17:00:00Z")
        self.until_dt = parse_time("2025-12-07T17:00:00Z")
        self.expected = [
            {"user": "alice", "start_at": "2025-12-01T17:00:00Z", "end_at": "2025-12-05T17:00:00Z"},
            {"user": "bob", "start_at": "2025-12-05T17:00:00Z", "end_at": "2025-12-07T17:00:00Z"},
        ]
        
    def test_full_flow(self):
        base_schedule = generate_base_schedule(self.schedule, self.from_dt, self.until_dt)
        final_schedule = apply_overrides(base_schedule, self.overrides)
        merged = merge_adjacent(final_schedule)
        self.assertEqual(len(merged), len(self.expected))
        for i, exp in enumerate(self.expected):
            with self.subTest(i=i):
                self.assertEqual(merged[i]["user"], exp["user"])
                self.assertEqual(fmt_time(merged[i]["start_at"]), exp["start_at"])
                self.assertEqual(fmt_time(merged[i]["end_at"]), exp["end_at"])


# Test 3.2: when time range has no schedule
class TestNoSchedule(unittest.TestCase):

    def setUp(self):
        # Sample schedule and overrides for testing
        self.schedule = {
            "users": ["alice", "bob", "charlie"],
            "handover_start_at": "2025-11-07T17:00:00Z",
            "handover_interval_days": 7
        }
        self.overrides = []
        self.from_dt = parse_time("2025-10-01T17:00:00Z")
        self.until_dt = parse_time("2025-10-07T17:00:00Z")
        self.expected = []
        
    def test_full_flow(self):
        base_schedule = generate_base_schedule(self.schedule, self.from_dt, self.until_dt)
        final_schedule = apply_overrides(base_schedule, self.overrides)
        merged = merge_adjacent(final_schedule)
        self.assertEqual(len(merged), len(self.expected))
        for i, exp in enumerate(self.expected):
            with self.subTest(i=i):
                self.assertEqual(merged[i]["user"], exp["user"])
                self.assertEqual(fmt_time(merged[i]["start_at"]), exp["start_at"])
                self.assertEqual(fmt_time(merged[i]["end_at"]), exp["end_at"])


# Test 4: when overrides list is empty
class TestEmptyOverrides(unittest.TestCase):
    
    def setUp(self):
        # Sample schedule and overrides for testing
        self.schedule = {
            "users": ["alice", "bob", "charlie"],
            "handover_start_at": "2025-11-07T17:00:00Z",
            "handover_interval_days": 7
        }
        self.overrides = []
        self.from_dt = parse_time("2025-11-07T17:00:00Z")
        self.until_dt = parse_time("2025-11-21T17:00:00Z")
        self.expected = [
            {"user": "alice", "start_at": "2025-11-07T17:00:00Z", "end_at": "2025-11-14T17:00:00Z"},
            {"user": "bob", "start_at": "2025-11-14T17:00:00Z", "end_at": "2025-11-21T17:00:00Z"},
        ]
        
    def test_full_flow(self):
        base_schedule = generate_base_schedule(self.schedule, self.from_dt, self.until_dt)
        final_schedule = apply_overrides(base_schedule, self.overrides)
        merged = merge_adjacent(final_schedule)
        self.assertEqual(len(merged), len(self.expected))
        for i, exp in enumerate(self.expected):
            with self.subTest(i=i):  # makes failures easier to debug
                self.assertEqual(merged[i]["user"], exp["user"])
                self.assertEqual(fmt_time(merged[i]["start_at"]), exp["start_at"])
                self.assertEqual(fmt_time(merged[i]["end_at"]), exp["end_at"])


# Test 5: when from and until are not aligned with shift boundaries
class TestUnalignedFromUntil(unittest.TestCase):

    def setUp(self):
        # Sample schedule and overrides for testing
        self.schedule = {
            "users": ["alice", "bob", "charlie"],
            "handover_start_at": "2025-11-07T17:00:00Z",
            "handover_interval_days": 7
        }
        self.overrides = []
        self.from_dt = parse_time("2025-11-10T12:00:00Z")
        self.until_dt = parse_time("2025-11-20T12:00:00Z")
        self.expected = [
            {"user": "alice", "start_at": "2025-11-10T12:00:00Z", "end_at": "2025-11-14T17:00:00Z"},
            {"user": "bob", "start_at": "2025-11-14T17:00:00Z", "end_at": "2025-11-20T12:00:00Z"},
        ]
        
    def test_full_flow(self):
        base_schedule = generate_base_schedule(self.schedule, self.from_dt, self.until_dt)
        final_schedule = apply_overrides(base_schedule, self.overrides)
        merged = merge_adjacent(final_schedule)
        self.assertEqual(len(merged), len(self.expected))
        for i, exp in enumerate(self.expected):
            with self.subTest(i=i):  # makes failures easier to debug
                self.assertEqual(merged[i]["user"], exp["user"])
                self.assertEqual(fmt_time(merged[i]["start_at"]), exp["start_at"])
                self.assertEqual(fmt_time(merged[i]["end_at"]), exp["end_at"])


# Test 6: when later overrides overlap earlier ones
class TestOverlappingOverrides(unittest.TestCase):

    def setUp(self):
        # Sample schedule and overrides for testing
        self.schedule = {
            "users": ["alice", "bob", "charlie"],
            "handover_start_at": "2025-11-07T17:00:00Z",
            "handover_interval_days": 7
        }
        self.overrides = [
            {
                "user": "maria",
                "start_at": "2025-11-10T17:00:00Z",
                "end_at": "2025-11-12T17:00:00Z"
            },
            {
                "user": "james",
                "start_at": "2025-11-11T17:00:00Z",
                "end_at": "2025-11-13T17:00:00Z"
            }
        ]
        self.from_dt = parse_time("2025-11-07T17:00:00Z")
        self.until_dt = parse_time("2025-11-21T17:00:00Z")
        self.expected = [
            {"user": "alice", "start_at": "2025-11-07T17:00:00Z", "end_at": "2025-11-10T17:00:00Z"},
            {"user": "maria", "start_at": "2025-11-10T17:00:00Z", "end_at": "2025-11-11T17:00:00Z"},
            {"user": "james", "start_at": "2025-11-11T17:00:00Z", "end_at": "2025-11-13T17:00:00Z"},
            {"user": "alice", "start_at": "2025-11-13T17:00:00Z", "end_at": "2025-11-14T17:00:00Z"},
            {"user": "bob", "start_at": "2025-11-14T17:00:00Z", "end_at": "2025-11-21T17:00:00Z"},
        ]
        
    def test_full_flow(self):
        base_schedule = generate_base_schedule(self.schedule, self.from_dt, self.until_dt)
        final_schedule = apply_overrides(base_schedule, self.overrides)
        merged = merge_adjacent(final_schedule)
        self.assertEqual(len(merged), len(self.expected))
        for i, exp in enumerate(self.expected):
            with self.subTest(i=i):  # makes failures easier to debug
                self.assertEqual(merged[i]["user"], exp["user"])
                self.assertEqual(fmt_time(merged[i]["start_at"]), exp["start_at"])
                self.assertEqual(fmt_time(merged[i]["end_at"]), exp["end_at"])


if __name__ == "__main__":
    unittest.main()