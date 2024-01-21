from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

import subprocess
import json

# 读取现有的 TSV 文件内容
def read_tsv(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    return lines


# 写入查询内容到 TSV 文件中
def write_to_tsv(file_path, query):
    lines = read_tsv(file_path)
    if lines:
        last_index = int(lines[-1].strip().split("\t")[0])
    else:
        last_index = 0
    new_index = last_index + 1
    new_line = f"{new_index}\t{query}\n"
    with open(file_path, 'a', encoding='utf-8') as file:
        file.write(new_line)

@app.route('/search', methods=['POST'])
def search():
    query = request.form['query']
    write_to_tsv('query.tsv', query)

    # TODO: Run the necessary commands to perform information retrieval
    # Use subprocess to run the commands mentioned in the original post

    # For example, you can run the first command like this:
    subprocess.run(['python', 'inference.py', '--model_name=srnair/blade-en-zh', '--input=query.tsv', '--output=experiment/runs/blade.jsonl', '--batch_size=128', '--is_query'])
    subprocess.run(['python', 'scripts/generate_anserini_topics.py', '--input=experiment/runs/blade.jsonl', '--output=experiment/runs/blade_anserini.tsv'])
    # TODO: Implement the rest of the retrieval steps
    subprocess.run(['sh', '/Users/mac/Documents/毕设/anserini/target/appassembler/bin/SearchCollection',
                    '-index', 'experiment/indexes/blade',  # Use the appropriate path for your index
                    '-topics', 'experiment/runs/blade_anserini.tsv',
                    '-topicReader', 'TsvInt',
                    '-output', 'experiment/runs/blade_passage_ranking.trec',
                    '-impact',
                    '-pretokenized',
                    '-hits', '10000'])
    subprocess.run(['python', 'scripts/aggregate_passage_scores.py',
                    '--rank_file', 'experiment/runs/blade_passage_ranking.trec',
                    '--mapping', 'experiment/mapping.tsv',  # Use the appropriate path for your mapping file
                    '--output', 'experiment/runs/blade_doc_ranking.trec'])

    with open('experiment/runs/blade_passage_ranking.trec', 'r') as f:
        lines = f.readlines()

    # Process the lines to extract document IDs or relevant information
    # For simplicity, assuming each line has the format: "doc_id score"
    results = [line.split()[2] for line in lines]
    documents = []
    with open('documents.jsonl', 'r') as f:
        for line in f:
            document = json.loads(line)
            documents.append(document)
    relevant_documents = [doc for doc in documents if doc['id'] in results]

    return render_template('index.html', results=relevant_documents)


if __name__ == '__main__':
    app.run(debug=True)


