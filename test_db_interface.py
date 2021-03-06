import unittest2
from db_interface import query_to_json


class TestDb_Interface(unittest2.TestCase):

    def test_no_results(self):
        q = "SELECT school_name FROM codetran_collegedata.collegescorecard WHERE latest_admissions_act_scores_midpoint_cumulative BETWEEN 36 AND 35"

        actualOutput = query_to_json(q)
        expectedOutput = {"column_names": [], "rows": []}

        self.assertEqual(actualOutput, expectedOutput)

    def test_one_col_results(self):
        q = 'SELECT school_name FROM codetran_collegedata.collegescorecard WHERE school_name="Pomona College" or school_name="Rice University"'

        actualOutput = query_to_json(q)
        expectedOutput = {
            "column_names": ["school_name"],
            "rows": [{
                "school_name": "Pomona College"
            }, {
                "school_name": "Rice University"
            }]
        }

        self.assertEqual(actualOutput["column_names"],
                         expectedOutput["column_names"])
        self.assertEqual(actualOutput["rows"], expectedOutput["rows"])

    def test_two_col_results(self):
        q = 'SELECT school_name, school_state FROM codetran_collegedata.collegescorecard WHERE school_name="Pomona College" or school_name="Rice University"'

        actualOutput = query_to_json(q)
        expectedOutput = {
            "column_names": ["school_name", "school_state"],
            "rows": [{
                "school_name": "Pomona College",
                "school_state": "CA"
            }, {
                "school_name": "Rice University",
                "school_state": "TX"
            }]
        }

        self.assertEqual(actualOutput["column_names"],
                         expectedOutput["column_names"])
        self.assertEqual(actualOutput["rows"], expectedOutput["rows"])

    def test_results_with_id(self):
        q = 'SELECT ope6_id, school_name, school_state FROM codetran_collegedata.collegescorecard WHERE school_name="Pomona College" or school_name="Rice University"'

        actualOutput = query_to_json(q)
        expectedOutput = {
            "column_names": ["ope6_id", "school_name", "school_state"],
            "rows": [{
                "ope6_id": 1173,
                "school_name": "Pomona College",
                "school_state": "CA"
            }, {
                "ope6_id": 3604,
                "school_name": "Rice University",
                "school_state": "TX"
            }]
        }

        self.assertEqual(actualOutput["column_names"],
                         expectedOutput["column_names"])
        self.assertEqual(actualOutput["rows"], expectedOutput["rows"])

    # TODO: make test pass
    # def test_non_string_results(self):
    #     q = 'SELECT school_name, latest_student_size FROM codetran_collegedata.collegescorecard WHERE school_name = "Pomona College" OR school_name = "Rice University"'

    #     actualOutput = query_to_json(q)
    #     expectedOutput = {
    #         "column_names": ["school_name", "latest_student_size"],
    #         "rows": [("Pomona College", 1549.0), ("Rice University", 3962.0)]
    #     }

    #     self.assertEqual(actualOutput["column_names"],
    #                      expectedOutput["column_names"])
    #     self.assertEqual(actualOutput["rows"], expectedOutput["rows"])


if __name__ == '__main__':
    unittest2.main()
