"""
Comprehensive tests for the colorprint module.
Tests color formatting and ANSI escape sequence functionality.
"""

import pytest
from unittest.mock import patch
from io import StringIO

from linkrot.colorprint import (
    colorprint,
    HEADER, OKBLUE, OKGREEN, WARNING, FAIL,
    BOLD, UNDERLINE, BLINK, REVERSE,
    ENDC
)


class TestColorConstants:
    """Test color and formatting constants."""

    def test_color_constants_defined(self):
        """Test that all color constants are defined."""
        constants = [HEADER, OKBLUE, OKGREEN, WARNING, FAIL]
        for constant in constants:
            assert isinstance(constant, str)
            assert constant.startswith('\033[')
            assert constant.endswith('m')

    def test_style_constants_defined(self):
        """Test that all style constants are defined."""
        styles = [BOLD, UNDERLINE, BLINK, REVERSE]
        for style in styles:
            assert isinstance(style, str)
            assert style.startswith('\033[')
            assert style.endswith('m')

    def test_end_constant_defined(self):
        """Test that ENDC constant is defined."""
        assert isinstance(ENDC, str)
        assert ENDC == '\033[0m'

    def test_constants_are_ansi_sequences(self):
        """Test that constants are valid ANSI escape sequences."""
        all_constants = [
            HEADER, OKBLUE, OKGREEN, WARNING, FAIL,
            BOLD, UNDERLINE, BLINK, REVERSE, ENDC
        ]
        
        for constant in all_constants:
            assert constant.startswith('\033[')
            assert constant.endswith('m')
            # Should contain digits between brackets
            inner = constant[2:-1]  # Remove \033[ and m
            assert inner.isdigit() or ';' in inner

    def test_color_constants_unique(self):
        """Test that color constants are unique."""
        colors = [HEADER, OKBLUE, OKGREEN, WARNING, FAIL]
        assert len(set(colors)) == len(colors)

    def test_style_constants_unique(self):
        """Test that style constants are unique."""
        styles = [BOLD, UNDERLINE, BLINK, REVERSE]
        assert len(set(styles)) == len(styles)


class TestColorprint:
    """Test colorprint function."""

    @patch('builtins.print')
    def test_colorprint_basic(self, mock_print):
        """Test basic colorprint functionality."""
        result = colorprint(OKGREEN, "Success message")
        
        expected = f"{OKGREEN}Success message{ENDC}"
        mock_print.assert_called_once_with(expected)
        assert result == expected

    @patch('builtins.print')
    def test_colorprint_all_colors(self, mock_print):
        """Test colorprint with all color constants."""
        colors = [HEADER, OKBLUE, OKGREEN, WARNING, FAIL]
        messages = ["Header", "Blue", "Green", "Warning", "Fail"]
        
        for color, message in zip(colors, messages):
            result = colorprint(color, message)
            expected = f"{color}{message}{ENDC}"
            assert result == expected

    @patch('builtins.print')
    def test_colorprint_with_styles(self, mock_print):
        """Test colorprint with style formatting."""
        styles = [BOLD, UNDERLINE, BLINK, REVERSE]
        
        for style in styles:
            result = colorprint(style, "Styled text")
            expected = f"{style}Styled text{ENDC}"
            assert result == expected

    @patch('builtins.print')
    def test_colorprint_empty_string(self, mock_print):
        """Test colorprint with empty string."""
        result = colorprint(OKGREEN, "")
        expected = f"{OKGREEN}{ENDC}"
        
        mock_print.assert_called_once_with(expected)
        assert result == expected

    @patch('builtins.print')
    def test_colorprint_special_characters(self, mock_print):
        """Test colorprint with special characters."""
        special_text = "Hello\nWorld\t!@#$%^&*()"
        result = colorprint(WARNING, special_text)
        expected = f"{WARNING}{special_text}{ENDC}"
        
        mock_print.assert_called_once_with(expected)
        assert result == expected

    @patch('builtins.print')
    def test_colorprint_unicode(self, mock_print):
        """Test colorprint with unicode characters."""
        unicode_text = "Hello 世界 🌍 café"
        result = colorprint(OKBLUE, unicode_text)
        expected = f"{OKBLUE}{unicode_text}{ENDC}"
        
        mock_print.assert_called_once_with(expected)
        assert result == expected

    @patch('builtins.print')
    def test_colorprint_long_text(self, mock_print):
        """Test colorprint with long text."""
        long_text = "This is a very long message " * 50
        result = colorprint(HEADER, long_text)
        expected = f"{HEADER}{long_text}{ENDC}"
        
        mock_print.assert_called_once_with(expected)
        assert result == expected

    @patch('builtins.print')
    def test_colorprint_multiple_calls(self, mock_print):
        """Test multiple colorprint calls."""
        messages = [
            (OKGREEN, "Success 1"),
            (WARNING, "Warning 1"),
            (FAIL, "Error 1"),
            (OKBLUE, "Info 1")
        ]
        
        results = []
        for color, message in messages:
            result = colorprint(color, message)
            results.append(result)
        
        # Should have made 4 print calls
        assert mock_print.call_count == 4
        
        # Each result should be properly formatted
        for i, (color, message) in enumerate(messages):
            expected = f"{color}{message}{ENDC}"
            assert results[i] == expected

    def test_colorprint_return_value(self):
        """Test that colorprint returns formatted string."""
        with patch('builtins.print'):
            result = colorprint(OKGREEN, "Test message")
            
            expected = f"{OKGREEN}Test message{ENDC}"
            assert result == expected
            assert isinstance(result, str)

    @patch('sys.stdout', new_callable=StringIO)
    def test_colorprint_actual_output(self, mock_stdout):
        """Test actual output to stdout."""
        colorprint(OKGREEN, "Test output")
        
        output = mock_stdout.getvalue()
        expected = f"{OKGREEN}Test output{ENDC}\n"
        assert output == expected

    @patch('builtins.print')
    def test_colorprint_formatting_consistency(self, mock_print):
        """Test that formatting is consistent across calls."""
        test_cases = [
            (OKGREEN, "Success"),
            (WARNING, "Warning"),
            (FAIL, "Error"),
            (HEADER, "Header"),
            (OKBLUE, "Info")
        ]
        
        for color, message in test_cases:
            result = colorprint(color, message)
            
            # Should always start with color code
            assert result.startswith(color)
            # Should always end with reset code
            assert result.endswith(ENDC)
            # Should contain the message
            assert message in result
            # Format should be: color + message + endc
            assert result == f"{color}{message}{ENDC}"


class TestColorprintIntegration:
    """Integration tests for colorprint functionality."""

    def test_colorprint_in_sequence(self):
        """Test colorprint calls in sequence produce correct output."""
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            colorprint(OKGREEN, "Starting process...")
            colorprint(WARNING, "Warning: Check configuration")
            colorprint(FAIL, "Error: Connection failed")
            colorprint(OKBLUE, "Info: Retrying...")
            colorprint(OKGREEN, "Success: Connected")
            
            output = mock_stdout.getvalue()
            lines = output.strip().split('\n')
            
            # Should have 5 lines of output
            assert len(lines) == 5
            
            # Each line should be properly formatted
            expected_lines = [
                f"{OKGREEN}Starting process...{ENDC}",
                f"{WARNING}Warning: Check configuration{ENDC}",
                f"{FAIL}Error: Connection failed{ENDC}",
                f"{OKBLUE}Info: Retrying...{ENDC}",
                f"{OKGREEN}Success: Connected{ENDC}"
            ]
            
            assert lines == expected_lines

    def test_colorprint_mixed_formatting(self):
        """Test colorprint with mixed color and style formatting."""
        # Note: In practice, you might combine colors and styles,
        # but the current implementation only uses one format at a time
        test_formats = [
            HEADER + BOLD,  # Combined formatting
            OKGREEN + UNDERLINE,
            WARNING + BLINK,
            FAIL + REVERSE
        ]
        
        for format_code in test_formats:
            with patch('builtins.print') as mock_print:
                result = colorprint(format_code, "Test")
                expected = f"{format_code}Test{ENDC}"
                
                mock_print.assert_called_once_with(expected)
                assert result == expected

    def test_colorprint_performance(self):
        """Test colorprint performance with many calls."""
        import time
        
        with patch('builtins.print'):
            start_time = time.time()
            
            # Make many colorprint calls
            for i in range(1000):
                colorprint(OKGREEN, f"Message {i}")
            
            end_time = time.time()
            execution_time = end_time - start_time
            
            # Should complete quickly (less than 1 second for 1000 calls)
            assert execution_time < 1.0

    def test_colorprint_error_handling(self):
        """Test colorprint with various input types."""
        with patch('builtins.print'):
            # Should handle various input types gracefully
            test_inputs = [
                ("", ""),  # Empty strings
                (OKGREEN, None),  # None message
                ("", "message"),  # Empty color
            ]
            
            for color, message in test_inputs:
                try:
                    result = colorprint(color, message)
                    # Should produce some string result
                    assert isinstance(result, str)
                except Exception as e:
                    # If it fails, it should be a reasonable error
                    assert isinstance(e, (TypeError, AttributeError))

    def test_ansi_sequence_validation(self):
        """Test that produced ANSI sequences are valid."""
        test_messages = ["Test", "123", "Special!@#", "Unicode: 🎨"]
        
        with patch('builtins.print'):
            for message in test_messages:
                result = colorprint(OKGREEN, message)
                
                # Should start with ANSI escape sequence
                assert result.startswith('\033[')
                # Should end with reset sequence
                assert result.endswith('\033[0m')
                # Should contain the original message
                assert message in result

    def test_colorprint_docstring_example(self):
        """Test the example from the docstring."""
        with patch('builtins.print') as mock_print:
            # Test the functionality described in the docstring
            result = colorprint(OKGREEN, "Success message")
            
            # Should format with color and reset
            expected = f"{OKGREEN}Success message{ENDC}"
            mock_print.assert_called_once_with(expected)
            assert result == expected
            
            # Verify the format matches docstring description
            assert result.startswith(OKGREEN)
            assert "Success message" in result
            assert result.endswith(ENDC)
