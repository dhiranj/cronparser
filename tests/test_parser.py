import unittest
from cron.parser import Parser, InvalidCronRangeError

class TestCronParser(unittest.TestCase):

    def test_valid_cron_expression(self):
        expression = "*/15 0 1,15 * 1-5 /usr/bin/find"
        parser = Parser(expression)
        result = parser.split_expression()

        expected_result = {
            'minute': [0, 15, 30, 45],
            'hour': [0],
            'day_of_month': [1, 15],
            'month': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
            'day_of_week': [1, 2, 3, 4, 5],
            'command': '/usr/bin/find'
        }
        
        self.assertDictEqual(result, expected_result)

    def test_invalid_cron_expression_length(self):
        expression = "*/15 0 1,15 * 1-5"
        with self.assertRaises(ValueError):
            parser = Parser(expression)
            parser.split_expression()

    def test_invalid_range(self):
        expression = "*/15 0 1,32 * 1-5 /usr/bin/find"
        with self.assertRaises(InvalidCronRangeError):
            parser = Parser(expression)
            parser.split_expression()

    def test_invalid_increment_step(self):
        expression = "*/-15 0 1,15 * 1-5 /usr/bin/find"
        with self.assertRaises(InvalidCronRangeError):
            parser = Parser(expression)
            parser.split_expression()

    def test_invalid_special_character(self):
        expression = "*/15 0 1,15 * 1-5? /usr/bin/find"
        with self.assertRaises(ValueError):
            parser = Parser(expression)
            parser.split_expression()

    def test_valid_cron_expression_with_range_increment(self):
        expression = "10-45/15 0 1,15 * 1-5 /usr/bin/find"
        parser = Parser(expression)
        result = parser.split_expression()

        expected_result = {
            'minute': [10, 25, 40],
            'hour': [0],
            'day_of_month': [1, 15],
            'month': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
            'day_of_week': [1, 2, 3, 4, 5],
            'command': '/usr/bin/find'
        }

        self.assertDictEqual(result, expected_result)

    def test_valid_cron_expression_with_combined_fields(self):
        expression = "10-45/15,50 0 1,15 * 1-5 ls"
        parser = Parser(expression)
        result = parser.split_expression()

        expected_result = {
            'minute': [10, 25, 30, 45, 50],
            'hour': [0],
            'day_of_month': [1, 15],
            'month': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
            'day_of_week': [1, 2, 3, 4, 5],
            'command': 'ls'
        }

        self.assertDictEqual(result, expected_result)

    def test_all_asterisks(self):
        expression = "* * * * * ls"
        parser = Parser(expression)
        result = parser.split_expression()

        expected_result = {
            'minute': list(range(0, 60)),
            'hour': list(range(0, 24)),
            'day_of_month': list(range(1, 32)),
            'month': list(range(1, 13)),
            'day_of_week': list(range(1, 8)), 
            'command': 'ls'
        }

        self.assertDictEqual(result, expected_result)

    def test_single_value_fields(self):
        expression = "5 14 1 7 3 /usr/bin/backup"
        parser = Parser(expression)
        result = parser.split_expression()

        expected_result = {
            'minute': [5],
            'hour': [14],
            'day_of_month': [1],
            'month': [7],
            'day_of_week': [3],
            'command': '/usr/bin/backup'
        }

        self.assertDictEqual(result, expected_result)

    def test_multiple_ranges(self):
        expression = "0-10/5,20-30/10 2 1,15 5 1 /usr/bin/cleanup"
        parser = Parser(expression)
        result = parser.split_expression()

        expected_result = {
            'minute': [0, 5, 10, 20, 30],
            'hour': [2],
            'day_of_month': [1, 15],
            'month': [5],
            'day_of_week': [1],
            'command': '/usr/bin/cleanup'
        }

        self.assertDictEqual(result, expected_result)

    def test_invalid_day_of_week(self):
        expression = "0 0 1 1 8 /usr/bin/find"
        with self.assertRaises(InvalidCronRangeError):
            parser = Parser(expression)
            parser.split_expression()

    def test_invalid_month(self):
        expression = "0 0 1 13 1 /usr/bin/find"
        with self.assertRaises(InvalidCronRangeError):
            parser = Parser(expression)
            parser.split_expression()

    def test_invalid_minute_range(self):
        expression = "60 0 1 * * /usr/bin/find"
        with self.assertRaises(InvalidCronRangeError):
            parser = Parser(expression)
            parser.split_expression()

    def test_invalid_hour_range(self):
        expression = "0 24 1 * * /usr/bin/find"
        with self.assertRaises(InvalidCronRangeError):
            parser = Parser(expression)
            parser.split_expression()

if __name__ == "__main__":
    unittest.main()


