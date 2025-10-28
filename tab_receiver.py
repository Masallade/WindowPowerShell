from flask import Flask, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/report_tabs', methods=['POST'])
def report_tabs():
    tabs = request.json
    print("\n================ Chrome Tabs Report ================")
    print(f"Received {len(tabs)} tab(s):")
    print("{:<3} | {:<60} | {}".format('No', 'Title', 'URL'))
    print("-" * 100)
    for idx, tab in enumerate(tabs, 1):
        title = (tab['title'][:57] + '...') if len(tab['title']) > 60 else tab['title']
        print(f"{idx:<3} | {title:<60} | {tab['url']}")
    print("===================================================\n")
    return 'OK'

if __name__ == '__main__':
    app.run(port=5000)