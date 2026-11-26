from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from feedback_check import check_batches
from feedback_review import review_batches


PROJECT = Path(__file__).resolve().parent.parent
MARKET_FILES = [PROJECT / 'samples' / f'{market}.csv' for market in ('uk', 'sg', 'au')]
REVISED_FILES = [PROJECT / 'samples' / f'{market}-revised.csv' for market in ('uk', 'sg', 'au')]
REVISED_AU = REVISED_FILES[-1]


def check(version, files):
    return check_batches(PROJECT / 'rules' / f'{version}.json', files)


class FeedbackCheckTests(unittest.TestCase):
    def test_v1_accepts_original_market_files(self):
        result = check('v1', MARKET_FILES)
        self.assertEqual(result['status'], 'READY_FOR_REVIEW')
        self.assertEqual(result['market_label_counts']['AU']['packaging'], 8)

    def test_v1_blocks_new_label(self):
        result = check('v1', REVISED_FILES)
        self.assertEqual(result['status'], 'BLOCKED')
        self.assertEqual(len(result['issues']), 9)
        self.assertIsNone(result['market_label_counts'])

    def test_new_rules_accept_new_and_previous_labels(self):
        result = check('v2', REVISED_FILES)
        self.assertEqual(result['status'], 'READY_FOR_REVIEW')
        self.assertEqual(result['market_label_counts']['AU']['refill_compatibility'], 5)
        for market in ('UK', 'SG'):
            self.assertEqual(result['market_label_counts'][market]['refill_compatibility'], 2)
            self.assertEqual(result['market_label_counts'][market]['packaging'], 3)
            self.assertEqual(result['market_label_counts'][market]['availability'], 5)
        self.assertEqual(check('v2', MARKET_FILES)['market_label_counts']['AU']['packaging'], 8)

    def test_duplicate_between_markets_or_submissions_is_blocked(self):
        result = check('v2', [MARKET_FILES[2], REVISED_AU])
        self.assertEqual(result['status'], 'BLOCKED')
        self.assertEqual(len(result['issues']), 15)

    def test_missing_headers_or_values_block_summary(self):
        with TemporaryDirectory() as directory:
            wrong_headers = Path(directory) / 'wrong-headers.csv'
            wrong_headers.write_text('id,market,label\nAU-04,AU,packaging\n', encoding='utf-8')
            missing_value = Path(directory) / 'missing-value.csv'
            missing_value.write_text('id,market,feedback,label\nAU-05,AU,,packaging\n', encoding='utf-8')
            result = check('v2', [wrong_headers, missing_value])
            self.assertEqual(result['status'], 'BLOCKED')
            self.assertEqual(len(result['issues']), 2)
            self.assertIsNone(result['market_label_counts'])

    def test_coverage_review_distinguishes_gaps_from_legacy_labels(self):
        expected_ids = [
            'UK-05', 'UK-13', 'SG-05', 'SG-13',
            'AU-01', 'AU-02', 'AU-04', 'AU-05', 'AU-06',
        ]
        for version, expected_code in [('v1', 'COVERAGE_GAP'), ('v2', 'LABEL_MISMATCH')]:
            with self.subTest(version=version):
                result = review_batches(PROJECT / 'rules' / f'{version}.json', MARKET_FILES)
                self.assertEqual(result['scanned_records'], 45)
                self.assertEqual([(flag['id'], flag['code']) for flag in result['flags']],
                                 [(case_id, expected_code) for case_id in expected_ids])

    def test_coverage_review_does_not_flag_sold_out_or_leaking_original_bottle(self):
        result = review_batches(PROJECT / 'rules' / 'v2.json', REVISED_FILES)
        self.assertEqual(result['scanned_records'], 45)
        self.assertEqual(result['flags'], [])
