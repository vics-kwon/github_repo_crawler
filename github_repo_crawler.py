import requests
import json
from datetime import datetime
import base64

class GithubRepoCrawler(object):

    def __init__(self):
        pass

    def search_repository(self, query, file_path):
        search_url = "https://api.github.com/search/repositories"
        params = {
            "q":query
        }
        search_result = requests.get(search_url, params=params).json()
        with open(file_path, "w") as fpout:
            json.dump(search_result, fpout, indent=2)

    def load_search_result(self, file_path):
        search_result = dict()
        with open(file_path, "r") as fpin:
            search_result = json.load(fpin)
        return search_result['items']
    
    def filter_search_result(self, a_search_result, filter_fields):
        a_result_filtered = {k:v for k,v in a_search_result.items() if k in filter_fields}
        return a_result_filtered

    def get_readme(self, full_name):
        readme_url = "https://api.github.com/repos/{full_name}/readme".format(full_name=full_name)
        result = requests.get(readme_url).json()
        readme = base64.b64decode(result['content'])
        return str(readme)

    def get_topics(self, full_name):
        topic_url = "https://api.github.com/repos/{full_name}/topics".format(full_name=full_name)
        headers = {'Accept':'application/vnd.github.mercy-preview+json'}
        result = requests.get(topic_url, headers=headers).json()
        return result['names']


if __name__ == "__main__":
    github_repo_crawler = GithubRepoCrawler()
    # query = "pytorch"
    # timestamp = datetime.today().strftime("%Y%m%d")
    # search_result_file = "%s_%s.json" %(query, timestamp)
    # github_crawler.search_repository(query, search_result_file)
    
    origin_path = "pytorch_20171127.json"
    filtered_path = "pytorch_20171127_filtered.json"
    search_result = github_repo_crawler.load_search_result(origin_path)
    
    filter_fields = [
        "id",
        "name",
        "full_name",
        "html_url",
        "description",
        "created_at",
        "updated_at",
        "stargazers_count",
        "watchers_count",
        "forks_count",
        "language"
    ]

    search_result_list = []

    test_idx = 0
    for a_search_result in search_result:
        if test_idx > 1:
            break
        search_result_filtered = github_repo_crawler.filter_search_result(a_search_result, filter_fields)
        full_name = search_result_filtered['full_name']
        search_result_filtered['readme'] = github_repo_crawler.get_readme(full_name)
        search_result_filtered['topics'] = github_repo_crawler.get_topics(full_name)

        search_result_list.append(json.dumps(search_result_filtered, ensure_ascii=False, indent=2))
        test_idx += 1

    with open(filtered_path, "w") as fpout:
        fpout.write('[')
        fpout.write(",".join(search_result_list))
        fpout.write(']')