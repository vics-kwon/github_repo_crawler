from unittest import TestCase

from github_manual_repo_cralwer import GithubManualRepoCrawler


class TestGithubManualRepoCrawler(TestCase):
    def setUp(self):
        self.manual_crawler = GithubManualRepoCrawler()

    def test_get_repo_content(self):
        query = 'pytorch'
        page_num = 0
        test_yn = True
        res = self.manual_crawler.get_repo_contents(query, page_num, test_yn)
        test_content = res[0]['full_name']
        self.assertGreater(len(test_content), 0)
