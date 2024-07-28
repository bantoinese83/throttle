import time
import unittest
from io import StringIO
from unittest.mock import patch, Mock

from progress_loader import ProgressLoader, my_example_function, process_data


class TestProgressLoader(unittest.TestCase):

    def setUp(self):
        self.test_data = list(range(1, 11))

    def test_update(self):
        loader = ProgressLoader(total=10)
        loader.update(1)
        self.assertEqual(loader.completed, 1)
        loader.update(4)
        self.assertEqual(loader.completed, 5)

    def test_default_render_bar(self):
        loader = ProgressLoader(total=10, desc="Test", bar_length=10, fill_char="=", empty_char=" ")
        loader.update(3)
        expected_output = "\033[94m[===       ]\033[0m"  # Blue bar for 3/10 progress
        self.assertIn(expected_output, loader._default_render_bar())

    def test_default_render_bar_green(self):
        loader = ProgressLoader(total=10, desc="Test", bar_length=10, fill_char="=", empty_char=" ", color="green")
        loader.update(3)
        expected_output = "\033[92m[===       ]\033[0m"  # Green bar for 3/10 progress
        self.assertIn(expected_output, loader._default_render_bar())

    def test_default_render_bar_red(self):
        loader = ProgressLoader(total=10, desc="Test", bar_length=10, fill_char="=", empty_char=" ", color="red")
        loader.update(3)
        expected_output = "\033[91m[===       ]\033[0m"  # Red bar for 3/10 progress
        self.assertIn(expected_output, loader._default_render_bar())

    def test_default_render_spinner(self):
        loader = ProgressLoader(total=10, desc="Test", spinner=True)
        output = loader._default_render_spinner()
        self.assertIn(loader.spinner_chars[loader.spinner_index], output)

    def test_default_render_dots(self):
        loader = ProgressLoader(total=10, desc="Test", style="dots")
        loader.update(1)
        self.assertEqual(loader._default_render_dots(), "Test: .")
        loader.update(1)
        self.assertEqual(loader._default_render_dots(), "Test: ..")

    @patch('sys.stdout', new_callable=StringIO)
    def test_render_progress(self, mock_stdout):
        loader = ProgressLoader(total=5, desc="Test", style="bar", bar_length=10, fill_char="=", empty_char=" ")
        loader.start()
        time.sleep(0.2)  # Let the loader run a bit
        loader.update(2)
        loader.update(3)
        time.sleep(0.2)  # Give some time for the last update to be rendered
        loader.close()
        output = mock_stdout.getvalue()
        # Remove ANSI color codes for comparison
        output = output.replace("\033[94m", "").replace("\033[0m", "")
        self.assertIn("Test: [==========] 100% (5/5 items)", output)

    @patch('sys.stdout', new_callable=StringIO)
    def test_with_function(self, mock_stdout):
        loader = ProgressLoader(total=5, desc="Loading", style="bar", bar_length=10, fill_char="=", empty_char=" ")
        loader.start()
        loader.with_function(my_example_function, list(range(5)))
        output = mock_stdout.getvalue()
        self.assertIn("Processing 4 ", output)

    @patch('sys.stdout', new_callable=StringIO)
    def test_decorator(self, mock_stdout):
        process_data(self.test_data)
        output = mock_stdout.getvalue()
        self.assertIn("Processing 10 ", output)

    @patch('sys.stdout', new_callable=StringIO)
    def test_with_function_spinner(self, mock_stdout):
        with ProgressLoader(total=10, desc="Processing data", spinner=True) as loader:
            loader.with_function(my_example_function, self.test_data)
        output = mock_stdout.getvalue()
        self.assertIn("Processing data: |", output)

    @patch('sys.stdout', new_callable=StringIO)
    def test_with_function_dots(self, mock_stdout):
        with ProgressLoader(total=10, desc="Processing data", style="dots", fill_char="*", empty_char=".") as loader:
            loader.with_function(my_example_function, self.test_data)
        output = mock_stdout.getvalue()
        self.assertIn("Processing data: ..", output)

    def test_initialization(self):
        loader = ProgressLoader(total=10, desc="Test", bar_length=10, fill_char="=", empty_char=" ")
        self.assertEqual(loader.total, 10)
        self.assertEqual(loader.desc, "Test")
        self.assertEqual(loader.bar_length, 10)
        self.assertEqual(loader.fill_char, "=")
        self.assertEqual(loader.empty_char, " ")

    def test_update_callback(self):
        mock_callback = Mock()
        loader = ProgressLoader(total=10, update_callback=mock_callback)
        loader.update(1)
        mock_callback.assert_called_with(1)
        loader.update(4)
        mock_callback.assert_called_with(5)

    @patch('sys.stdout', new_callable=StringIO)
    def test_render_callback(self, mock_stdout):
        mock_render = Mock(return_value="Custom Render")
        loader = ProgressLoader(total=5, desc="Test", render_callback=mock_render)
        loader.start()
        time.sleep(0.2)
        loader.update(2)
        loader.update(3)
        time.sleep(0.2)
        loader.close()
        output = mock_stdout.getvalue()
        self.assertIn("Custom Render", output)

    @patch('sys.stdout', new_callable=StringIO)
    def test_with_function_exception_handling(self, mock_stdout):
        def faulty_function(data, loader):
            raise ValueError("Test Exception")

        loader = ProgressLoader(total=5, desc="Loading", style="bar", bar_length=10, fill_char="=", empty_char=" ")
        with self.assertRaises(ValueError):
            loader.with_function(faulty_function, list(range(5)))
        output = mock_stdout.getvalue()
        self.assertIn("Test Exception", output)

    @patch('sys.stdout', new_callable=StringIO)
    def test_render_progress_default_bar(self, mock_stdout):
        loader = ProgressLoader(total=5, desc="Test", style="bar", bar_length=10, fill_char="=", empty_char=" ")
        loader.start()
        time.sleep(0.2)  # Let the loader run a bit
        loader.update(2)
        loader.update(3)
        time.sleep(0.2)  # Give some time for the last update to be rendered
        loader.close()
        output = mock_stdout.getvalue()
        # Remove ANSI color codes for comparison
        output = output.replace("\033[94m", "").replace("\033[0m", "")
        self.assertIn("Test: [==========] 100% (5/5 items)", output)

    @patch('sys.stdout', new_callable=StringIO)
    def test_default_render_time_clock(self, mock_stdout):
        loader = ProgressLoader(total=10, desc="Test", style="time_clock")
        loader.update(3)  # 30% progress
        output = loader._default_render_time_clock()
        self.assertEqual(output, "Test: 🕒")  # Expecting the third clock emoji

        loader.update(7)  # 70% progress
        output = loader._default_render_time_clock()
        self.assertEqual(output, "Test: 🕝")  # Expecting the eighth clock emoji

    @patch('sys.stdout', new_callable=StringIO)
    def test_render_progress_time_clock(self, mock_stdout):
        loader = ProgressLoader(total=10, desc="Test", style="time_clock")
        loader.start()
        time.sleep(0.2)
        loader.update(5)
        time.sleep(0.2)
        loader.close()
        output = mock_stdout.getvalue()
        self.assertIn("Test: 🕗", output)  # Check for a clock emoji in the output

    @patch('sys.stdout', new_callable=StringIO)
    def test_start_and_close(self, mock_stdout):
        loader = ProgressLoader(total=10, desc="Test", style="bar")
        loader.start()
        time.sleep(0.2)
        loader.close()
        output = mock_stdout.getvalue()
        self.assertIn("Test: \x1b[94m[                    ]\x1b[0m 0% (0/10 items)", output)  # Adjusted expected output

    def test_with_function_no_data(self):
        loader = ProgressLoader(total=10)
        with self.assertRaises(ValueError):
            loader.with_function(my_example_function, [])  # Ensure the function raises ValueError for empty data


class TestProgressLoaderEdgeCases(unittest.TestCase):

    def test_zero_total(self):
        loader = ProgressLoader(total=0)
        self.assertEqual(loader.total, 0)
        loader.update()
        self.assertEqual(loader.completed, 1)  # Should handle zero totals gracefully

    def test_negative_update(self):
        loader = ProgressLoader(total=10)
        loader.update(-1)
        self.assertEqual(loader.completed, -1)  # Should handle negative updates

    def test_high_total(self):
        loader = ProgressLoader(total=1000000)
        loader.update(500000)
        self.assertEqual(loader.completed, 500000)  # Should handle very high totals

    def test_invalid_style(self):
        with self.assertRaises(ValueError):
            ProgressLoader(total=10, style="invalid_style")

    def test_invalid_color(self):
        with self.assertRaises(ValueError):
            ProgressLoader(total=10, color="invalid_color")

    def test_invalid_fill_char(self):
        with self.assertRaises(ValueError):
            ProgressLoader(total=10, fill_char="##")

    def test_invalid_empty_char(self):
        with self.assertRaises(ValueError):
            ProgressLoader(total=10, empty_char="  ")

    def test_invalid_time_clock(self):
        with self.assertRaises(ValueError):
            ProgressLoader(total=10, style="time_clock", fill_char="##")


if __name__ == '__main__':
    unittest.main()
