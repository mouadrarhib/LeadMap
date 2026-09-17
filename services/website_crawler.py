import logging
from collections import deque
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

import httpx
from bs4 import BeautifulSoup

from services.email_extractor import choose_preferred_email, extract_emails_from_html
from utils.url_utils import absolute_url, domain_from_url, normalize_url, same_domain

logger = logging.getLogger(__name__)
CONTACT_HINTS = ("contact", "about", "team", "nous-contacter", "qui-sommes-nous")


class WebsiteCrawler:
    def __init__(self, timeout: int = 10, max_pages: int = 5, user_agent: str = "LeadMap/1.0"):
        self.timeout = timeout
        self.max_pages = min(max_pages, 5)
        self.user_agent = user_agent

    def find_email(self, website: str) -> tuple[str | None, list[str]]:
        start_url = normalize_url(website)
        domain = domain_from_url(start_url)
        if not start_url or not domain:
            return None, []
        queue: deque[str] = deque([start_url])
        visited: set[str] = set()
        emails: set[str] = set()
        robots = self._robots(start_url)
        headers = {"User-Agent": self.user_agent, "Accept": "text/html,application/xhtml+xml"}
        with httpx.Client(timeout=self.timeout, follow_redirects=True, headers=headers) as client:
            while queue and len(visited) < self.max_pages:
                url = queue.popleft()
                if url in visited or not same_domain(url, domain):
                    continue
                if robots and not robots.can_fetch(self.user_agent, url):
                    continue
                visited.add(url)
                try:
                    response = client.get(url)
                    response.raise_for_status()
                    if "text/html" not in response.headers.get("content-type", ""):
                        continue
                    emails.update(extract_emails_from_html(response.text))
                    if len(visited) == 1:
                        queue.extend(self._contact_links(response.text, str(response.url), domain))
                except (httpx.HTTPError, ValueError) as exc:
                    logger.info("Could not crawl %s: %s", url, type(exc).__name__)
        return choose_preferred_email(emails, start_url), sorted(emails)

    def _robots(self, start_url: str) -> RobotFileParser | None:
        parsed = urlparse(start_url)
        robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
        parser = RobotFileParser(robots_url)
        try:
            response = httpx.get(
                robots_url,
                timeout=self.timeout,
                follow_redirects=True,
                headers={"User-Agent": self.user_agent},
            )
            if response.status_code >= 400:
                return None
            parser.parse(response.text.splitlines())
            return parser
        except httpx.HTTPError:
            return None

    @staticmethod
    def _contact_links(html: str, base_url: str, domain: str) -> list[str]:
        soup = BeautifulSoup(html, "html.parser")
        ranked: list[str] = []
        for link in soup.find_all("a", href=True):
            href = str(link["href"])
            label = f"{href} {link.get_text(' ', strip=True)}".lower()
            if any(hint in label for hint in CONTACT_HINTS):
                url = absolute_url(base_url, href).split("#", 1)[0]
                if same_domain(url, domain) and url not in ranked:
                    ranked.append(url)
        return ranked
