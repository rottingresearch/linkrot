# Retraction Checking Feature for Linkrot

## Overview

The retraction checking feature has been successfully added to the linkrot project. This functionality allows users to check DOIs found in PDF documents against retraction databases to identify potentially retracted papers.

## Features Implemented

### 1. Core Retraction Module (`linkrot/retraction.py`)

- **RetractionChecker Class**: Main class for checking DOIs against retraction databases
- **Multiple Detection Methods**:
  - CrossRef API integration for retraction notices
  - Metadata analysis for retraction indicators  
  - Placeholder for direct Retraction Watch Database API (when available)
- **Rate Limiting**: Respectful API usage with configurable delays
- **Caching**: Avoids repeated API calls for the same DOIs
- **Comprehensive Error Handling**: Graceful handling of API failures

### 2. CLI Integration (`linkrot/cli.py`)

- **New Command Line Option**: `-r, --check-retractions`
- **Seamless Integration**: Works with existing flags and output formats
- **JSON Support**: Retraction results included in JSON output
- **Text Output**: Summary included in standard text output

### 3. Detection Methods

The retraction checker uses multiple approaches to identify retractions:

1. **CrossRef API**: Checks paper metadata for retraction keywords in titles and subjects
2. **Metadata Analysis**: Scans DOI landing pages for retraction notices
3. **Future Extension**: Ready for direct Retraction Watch Database API integration

### 4. Key Functions

- `check_dois_for_retractions()`: Convenience function for batch checking
- `RetractionChecker.check_doi()`: Check individual DOI
- `RetractionChecker.check_multiple_dois()`: Batch DOI checking
- `_print_retraction_results()`: Formatted output of results

## Usage Examples

### Command Line Usage

```bash
# Basic retraction check on a PDF
python -m linkrot.cli document.pdf -r

# Check retractions and output as JSON
python -m linkrot.cli document.pdf -r -j

# Check retractions with verbose output
python -m linkrot.cli document.pdf -r -v

# Combine with other features
python -m linkrot.cli document.pdf -r -c  # Also check for broken links
```

### Programmatic Usage

```python
from linkrot.retraction import check_dois_for_retractions

# Check a set of DOIs
dois = {"10.1000/182", "10.1038/nature12373"}
result = check_dois_for_retractions(dois, verbose=True)

print(f"Retracted papers: {result['summary']['retracted_count']}")
```

## Output Format

### Text Output
```
Retraction Check Results:
========================
Total DOIs checked: 3
Clean papers: 2
Retracted papers: 1
Errors: 0

⚠️  RETRACTED PAPERS FOUND:
  DOI: 10.1000/example
    Title: Retraction: Some Paper Title
    Journal: Example Journal
    Reason: Detected via CrossRef metadata
    Notice: https://doi.org/10.1000/example
```

### JSON Output
```json
{
  "retraction_check": {
    "results": {
      "10.1000/182": {
        "doi": "10.1000/182",
        "is_retracted": false,
        "error": null
      }
    },
    "summary": {
      "total_checked": 1,
      "retracted_count": 0,
      "clean_count": 1,
      "error_count": 0
    }
  }
}
```

## Dependencies Added

- `requests>=2.25.0`: For API communications

## Files Modified/Created

### New Files
- `linkrot/retraction.py`: Core retraction checking functionality
- `tests/test_retraction.py`: Comprehensive test suite
- `examples/retraction_demo.py`: Usage demonstration

### Modified Files
- `linkrot/cli.py`: Added CLI integration
- `pyproject.toml`: Added requests dependency

## Testing

The implementation includes:
- Comprehensive unit tests covering all functionality
- Integration tests with the CLI
- Example usage demonstrations
- Error handling validation

## Future Enhancements

1. **Direct Retraction Watch Database API**: When API access becomes available
2. **Additional Databases**: Integration with other retraction databases
3. **Local Database Caching**: For offline retraction checking
4. **Batch Processing**: Optimized handling of large DOI sets
5. **Confidence Scoring**: Probability-based retraction detection

## Benefits

- **Research Integrity**: Helps identify potentially problematic citations
- **Automated Checking**: Reduces manual verification workload
- **Integration Ready**: Works seamlessly with existing linkrot workflows
- **Extensible Design**: Easy to add new retraction databases
- **Respectful API Usage**: Rate limiting and caching prevent API abuse

The retraction checking feature enhances linkrot's capability to ensure research integrity by automatically identifying potentially retracted papers in PDF documents.
