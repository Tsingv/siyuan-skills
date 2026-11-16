import csv
import io
import sys
import unittest
from pathlib import Path
from unittest.mock import Mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "skill" / "python"))

from siyuan_skill.formatters import build_envelope, render_result
from siyuan_skill.operations.query import QueryOperations


class QueryOutputTests(unittest.TestCase):
    def query(self, rows):
        client = Mock()
        client.call.return_value = {"data": rows}
        return QueryOperations(client).sql("SELECT type, count(*) AS total FROM blocks GROUP BY type")

    def test_custom_projection_has_only_actual_columns_in_all_formats(self):
        result = self.query([{"type": "p", "total": 3}])
        self.assertEqual(build_envelope(result, "json")["meta"]["columns"], ["type", "total"])
        self.assertEqual(list(csv.reader(io.StringIO(render_result(result, "csv")))),
                         [["type", "total"], ["p", "3"]])
        markdown = render_result(result, "markdown")
        self.assertIn("total", markdown)
        self.assertNotIn("root_id", markdown)

    def test_empty_result_does_not_claim_block_schema(self):
        result = self.query([])
        self.assertEqual(build_envelope(result, "json")["meta"]["row_count"], 0)
        self.assertNotIn("columns", build_envelope(result, "json")["meta"])


if __name__ == "__main__":
    unittest.main()
