from datetime import datetime
from bs4 import BeautifulSoup
import requests
import random
import time
import json


class GithubManualRepoCrawler(object):

    def __init__(self):
        pass

    def get_repo_contents(self, query, page_num, test_yn):
        repo_content_list = []
        search_url = "https://github.com/search"
        params = {
            "q": query,
            "p": page_num,
            "type": "Repositories"
        }

        search_result = requests.get(search_url, params=params)
        soup = BeautifulSoup(search_result.content, "html.parser")

        body_contents = soup.select("#js-pjax-container > div.container ul.repo-list > div")
        for idx, a_content in enumerate(body_contents):
            repo_content_list.append(self.get_one_repo_content(a_content))
            if test_yn:
                break

        return repo_content_list

    def get_one_repo_content(self, a_content):
        one_repo_content = dict()
        one_repo_content['full_name'] = a_content.select("a")[0]['href']
        one_repo_content['html_url'] = "https://github.com%s" % (one_repo_content['full_name'])
        one_repo_content['description'] = ""
        for des_idx, des_content in enumerate(a_content.select("p")[0].contents):
            one_repo_content['description'] = one_repo_content['description'] + " " + des_content.string.strip()
        one_repo_content['language'] = a_content.select("div.d-table-cell.col-2.text-gray.pt-2")[0].contents[
            -1].strip()

        one_repo_content['topics'] = []
        topics_content = a_content.select(
            "div.col-8.pr-3 > div.topics-row-container.col-9.d-inline-flex.flex-wrap.flex-items-center.f6.my-1 > a")
        if len(topics_content) > 0:
            for a_topic in topics_content:
                topic = a_topic.string.strip()
                one_repo_content['topics'].append(topic)

        reputation_content = self.get_one_reputation_content(one_repo_content['full_name'])

        one_repo_content['stargazers_count'] = reputation_content['stargazers_count']
        one_repo_content['watchers_count'] = reputation_content['watchers_count']
        one_repo_content['forks_count'] = reputation_content['forks_count']

        print("## Content of %s is crawled." %one_repo_content['full_name'])
        return one_repo_content

    @staticmethod
    def get_one_reputation_content(full_name):
        repo_url = "https://github.com%s/wiki" %full_name
        params = None

        repo_result = requests.get(repo_url, params=params)

        reputation_content = dict()
        repu_soup = BeautifulSoup(repo_result.content, "html.parser")
        repu_container = repu_soup.select("div.pagehead.repohead.instapaper_ignore.readability-menu.experiment-repo-nav > div > ul > li")

        for idx, repu in enumerate(repu_container):
            res = repu.contents[3].contents[0].strip()
            if idx == 0:
                reputation_content['stargazers_count'] = res.replace(',', '')
            if idx == 1:
                reputation_content['watchers_count'] = res.replace(',', '')
            if idx == 2:
                reputation_content['forks_count'] = res.replace(',', '')

        time.sleep(random.uniform(2.5, 3.5))
        return reputation_content

    @staticmethod
    def save_repo_content_list(repo_content_list, save_path):
        with open(save_path, "w") as fpout:
            json.dump(repo_content_list, fpout, ensure_ascii=False, indent=2)

        print("Crawled Content is saved in %s" % save_path)


if __name__ == "__main__":
    query = input("Enter your query : ")
    from_page = input("Enter the page number you want to start crawl : ")
    to_page = input("Enter the page number you want to stop crawl : ")

    total_count = 10 * (int(to_page) - int(from_page) + 1)
    timestamp = datetime.today().strftime("%Y%m%d")
    save_path = "./%s_crawl_%s.json" % (query, timestamp)

    print("Crawling github repo content of %s will be started." % query)
    print("Crawling range is from %s to %s. Total count of crawling contents will be %s." % (
    from_page, to_page, total_count))
    print("Result will be stored in %s" % save_path)

    github_manual_repo_crawler = GithubManualRepoCrawler()
    test_yn = False

    crawl_result = []
    for page in range(int(from_page), int(to_page)):
        search_result = github_manual_repo_crawler.get_repo_contents(query, page, test_yn)
        crawl_result.extend(search_result)

    github_manual_repo_crawler.save_repo_content_list(crawl_result, save_path)
