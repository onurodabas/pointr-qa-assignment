"""
Step definitions for blog_page.feature
"""

from behave import given, when, then
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from collections import Counter
import re
import os
import time


# Common English stop words plus some web/site-specific noise.
# Filtering these out gives us meaningful, content-specific top words.
STOP_WORDS = {
    # articles, pronouns
    'the', 'a', 'an',
    'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her',
    'us', 'them', 'my', 'your', 'his', 'its', 'our', 'their',
    # common verbs
    'is', 'are', 'was', 'were', 'be', 'been', 'being', 'am',
    'have', 'has', 'had', 'do', 'does', 'did', 'doing',
    'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can',
    'shall', 'ought',
    # conjunctions
    'and', 'or', 'but', 'nor', 'so', 'yet', 'for',
    # prepositions / common adverbs
    'of', 'in', 'to', 'with', 'on', 'at', 'by', 'from', 'about',
    'as', 'into', 'through', 'during', 'before', 'after', 'above',
    'below', 'up', 'down', 'out', 'off', 'over', 'under', 'again',
    'further', 'then', 'once', 'here', 'there', 'when', 'where',
    'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more',
    'most', 'other', 'some', 'such', 'no', 'not', 'only', 'own',
    'same', 'than', 'too', 'very', 'just', 'now',
    # determiners
    'this', 'that', 'these', 'those', 'which', 'who', 'whom', 'whose',
    # misc common words
    'also', 'said', 'says', 'one', 'two', 'if', 'while', 'because',
    'until', 'although', 'though', 'since', 'unless', 'whereas',
    # site/navigation noise
    'read', 'more', 'less', 'home', 'page', 'click', 'menu',
    'blog', 'post', 'posts', 'article', 'articles', 'pointr'
}


@given('I open the Pointr blog page')
def step_open_blog_page(context):
    context.blog_url = 'https://www.pointr.tech/blog'
    context.driver.get(context.blog_url)

    WebDriverWait(context.driver, 30).until(
        lambda driver: driver.execute_script('return document.readyState') == 'complete'
    )

    # Small extra wait for any client-side rendering
    time.sleep(2)


@then('the page title should contain "{expected_text}"')
def step_check_title(context, expected_text):
    actual_title = context.driver.title
    assert expected_text.lower() in actual_title.lower(), \
        f"Expected title to contain '{expected_text}', got '{actual_title}'"


@then('the URL should contain "{expected_url_part}"')
def step_check_url(context, expected_url_part):
    current_url = context.driver.current_url
    assert expected_url_part in current_url, \
        f"Expected URL to contain '{expected_url_part}', got '{current_url}'"


@then('the page should be fully loaded')
def step_check_page_loaded(context):
    ready_state = context.driver.execute_script('return document.readyState')
    assert ready_state == 'complete', \
        f"Page not fully loaded. readyState: {ready_state}"


@then('the page should display at least {min_count:d} articles')
def step_check_article_count(context, min_count):
    """
    Count 'Read more' links on the page. Each article card has one,
    and the text doesn't appear in nav or footer, so it's a reliable
    way to count articles.
    """
    read_more_links = context.driver.find_elements(
        By.XPATH,
        "//a[contains(text(), 'Read more')]"
    )
    context.all_article_links = read_more_links

    actual_count = len(read_more_links)
    assert actual_count >= min_count, \
        f"Expected at least {min_count} articles, found {actual_count}"


@then('each article should have a title')
def step_check_article_titles(context):
    """Pointr's blog uses <h4> for article card titles."""
    article_titles = context.driver.find_elements(By.TAG_NAME, 'h4')
    non_empty_titles = [t for t in article_titles if t.text.strip()]

    assert len(non_empty_titles) > 0, "No article titles found"


@then('each article should have a "Read more" link')
def step_check_read_more_links(context):
    assert hasattr(context, 'all_article_links'), \
        "Article links not collected; run the count step first"

    assert len(context.all_article_links) > 0, "No 'Read more' links found"

    for link in context.all_article_links:
        href = link.get_attribute('href')
        assert href and 'pointr.tech/blog' in href, \
            f"Invalid article link: {href}"


@when('I extract the latest 3 article URLs')
def step_extract_latest_urls(context):
    """
    Skip the first 'Read more' link (Featured article) and take the
    next 3 from the Latest section.
    """
    all_links = context.driver.find_elements(
        By.XPATH,
        "//a[contains(text(), 'Read more')]"
    )

    assert len(all_links) >= 4, \
        "Need at least 4 articles (1 featured + 3 latest)"

    latest_3_urls = [all_links[i].get_attribute('href') for i in range(1, 4)]
    context.latest_article_urls = latest_3_urls


@then('I should have exactly 3 article URLs')
def step_verify_3_urls(context):
    count = len(context.latest_article_urls)
    assert count == 3, f"Expected 3 URLs, got {count}"


@then('each URL should contain "{expected_part}"')
def step_verify_urls_contain(context, expected_part):
    for url in context.latest_article_urls:
        assert expected_part in url, \
            f"Invalid URL (missing '{expected_part}'): {url}"


@when('I visit each article and extract its text')
def step_visit_articles_extract_text(context):
    """
    Navigate to each article and grab the text from <body>.
    Reading from <body> is a deliberate trade-off: it includes some
    navigation/footer noise, but it's robust to layout changes.
    The stop word filter compensates for the extra noise.
    """
    context.article_texts = {}

    for url in context.latest_article_urls:
        context.driver.get(url)

        WebDriverWait(context.driver, 30).until(
            lambda driver: driver.execute_script('return document.readyState') == 'complete'
        )
        time.sleep(2)

        body = context.driver.find_element(By.TAG_NAME, 'body')
        text = body.text

        try:
            title = context.driver.find_element(By.TAG_NAME, 'h1').text
        except Exception:
            title = "Unknown Title"

        context.article_texts[url] = {'title': title, 'text': text}


@then('each article should have its top 5 words identified')
def step_find_top_5_words(context):
    """
    For each article: lowercase, extract letter-only words (3+ chars),
    drop stop words, count frequencies, take top 5.
    """
    context.article_word_counts = {}

    for url, data in context.article_texts.items():
        text = data['text'].lower()
        words = re.findall(r'\b[a-z]{3,}\b', text)
        meaningful_words = [w for w in words if w not in STOP_WORDS]

        word_counts = Counter(meaningful_words)
        top_5 = word_counts.most_common(5)

        context.article_word_counts[url] = {
            'title': data['title'],
            'top_5': top_5
        }

        assert len(top_5) == 5, \
            f"Expected 5 words for {url}, got {len(top_5)}"


@then('the results should be saved to "{filename}"')
def step_save_to_file(context, filename):
    filepath = os.path.join(context.output_dir, filename)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write("=" * 60 + "\n")
        f.write("POINTR BLOG - WORD FREQUENCY ANALYSIS\n")
        f.write("=" * 60 + "\n")
        f.write(f"Browser: {context.browser_name.upper()}\n")
        f.write(f"Articles analyzed: {len(context.article_word_counts)}\n")
        f.write("=" * 60 + "\n\n")

        for i, (url, data) in enumerate(context.article_word_counts.items(), 1):
            f.write(f"ARTICLE {i}\n")
            f.write(f"Title: {data['title']}\n")
            f.write(f"URL: {url}\n")
            f.write("-" * 60 + "\n")
            f.write("Top 5 Most Frequent Words:\n")

            for rank, (word, count) in enumerate(data['top_5'], 1):
                f.write(f"  {rank}. {word}: {count} occurrences\n")

            f.write("\n")

    assert os.path.exists(filepath), f"File not created: {filepath}"
    context.output_filepath = filepath


@then('the output file should exist')
def step_verify_file_exists(context):
    assert os.path.exists(context.output_filepath), \
        f"Output file does not exist: {context.output_filepath}"

    size = os.path.getsize(context.output_filepath)
    assert size > 0, "Output file is empty"


@then('the output file should contain data for all 3 articles')
def step_verify_file_contents(context):
    with open(context.output_filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    for i in range(1, 4):
        marker = f"ARTICLE {i}"
        assert marker in content, f"'{marker}' not found in output file"
