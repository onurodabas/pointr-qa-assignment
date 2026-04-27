# Pointr Blog UI Automation

Selenium-based BDD test suite that validates the Pointr blog page and analyzes the latest 3 articles.

## What It Does

1. Opens `https://www.pointr.tech/blog`
2. Verifies all articles have loaded on the page
3. Picks the latest 3 articles (from the "Latest" section, skipping the Featured one)
4. Visits each article and extracts its text
5. Finds the top 5 most frequent words in each article (after filtering stop words)
6. Saves the results to a `.txt` file

The tests run on both Chrome and Firefox.

## Project Structure

```
q2_ui_automation_bdd/
├── requirements.txt
├── README.md
├── .gitignore
├── .github/
│   └── workflows/
│       └── bdd-tests.yml           # CI/CD pipeline (Chrome + Firefox matrix)
├── output/                         # Generated reports go here
│   ├── word_frequency_report.txt
│   └── full_report.txt
└── features/
    ├── environment.py              # Browser setup/teardown
    ├── blog_page.feature           # BDD scenarios
    └── steps/
        └── blog_steps.py
```

## How to Run

### Prerequisites

- Python 3.11+
- Chrome and/or Firefox installed
- pip

Browser drivers are downloaded automatically by `webdriver-manager`, so no manual setup is needed.

### Setup

```bash
pip install -r requirements.txt
```

### Running the Tests

```bash
# Default: Chrome
behave

# Firefox
BROWSER=firefox behave

# A specific scenario
behave -n "Analyze word frequency"

# Verbose output
behave --no-capture
```

After running, check the `output/` folder for the generated `.txt` reports.

## Test Scenarios

| # | Scenario                                      | Verifies                                                    |
|---|-----------------------------------------------|-------------------------------------------------------------|
| 1 | Blog page loads successfully                  | Page title, URL, fully loaded                               |
| 2 | All articles are visible on the blog page     | At least 9 articles, each has a title and a "Read more" link |
| 3 | Extract the latest 3 articles                 | Three valid pointr.tech/blog URLs are collected             |
| 4 | Analyze word frequency for the latest 3       | Visits each article, finds top 5 words, saves to .txt       |
| 5 | Complete end-to-end workflow                  | Integration test that runs the full flow                    |

## Output Format

```
============================================================
POINTR BLOG - WORD FREQUENCY ANALYSIS
============================================================
Browser: CHROME
Articles analyzed: 3
============================================================

ARTICLE 1
Title: ...
URL: ...
------------------------------------------------------------
Top 5 Most Frequent Words:
  1. word: 32 occurrences
  2. word: 26 occurrences
  ...
```

## Design Decisions

**Why "Read more" link as the article selector?**
Every article card on the Pointr blog has a "Read more" link, and this text doesn't appear in the navigation or footer. It's a more reliable selector than CSS classes, which tend to be auto-generated and change between site versions.

**Why skip the Featured article when picking the "latest 3"?**
The Featured article is a pinned/highlighted post, not necessarily the most recent. The task asks for the latest 3, so I take the first 3 articles from the "Latest" section instead.

**Why filter stop words?**
Without filtering, the top 5 in every article would be "the", "and", "to", "of", "is" — which tells us nothing about the article. Filtering common stop words gives us meaningful, content-specific words like "maps", "wayfinding", "stadium", etc.

**Why a fresh browser per scenario?**
Each scenario starts a new browser instance and quits it after. This isolates tests from each other so that cookies, cache, or leftover state from one test can't affect another. Slightly slower, but much more reliable.

**Why text from `<body>` instead of a specific article container?**
A specific container would be cleaner, but Pointr's blog uses generic class names that may change. Reading from `<body>` is robust across layout changes; the stop word filter compensates for the extra navigation/footer text.

## CI/CD

The GitHub Actions workflow uses a matrix strategy to run the tests in parallel on both Chrome and Firefox. Output files are uploaded as artifacts so you can download the generated reports from the Actions tab.



