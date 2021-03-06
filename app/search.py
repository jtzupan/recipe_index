from flask import current_app
import re


def add_to_index(index, model):
    if not current_app.elasticsearch:
        return
    payload = {}
    for field in model.__searchable__:
        payload[field] = getattr(model, field)
    current_app.elasticsearch.index(index=index, id=model.id, body=payload)


def remove_from_index(index, model):
    if not current_app.elasticsearch:
        return
    current_app.elasticsearch.delete(index=index, id=model.id)


def query_index(index, query, page, per_page):
    if not current_app.elasticsearch:
        return [], 0
    search = current_app.elasticsearch.search(
        index=index,
        body={'query': {'multi_match': {'query': query, 'fields': ['*']}},
              "highlight": {"fields": {'*': {}}},
              'from': (page - 1) * per_page, 'size': per_page})
    ids = [int(hit['_id']) for hit in search['hits']['hits']]
    full_texts = [hit['highlight']['recipe_text'] for hit in search['hits']['hits']]
    full_texts_joined = [' '.join(s) for s in full_texts]
    full_texts_filtered = [re.findall(r'<em>(\S*)</em>', st) for st in full_texts_joined]
    full_texts_filtered = [", ".join(a) for a in full_texts_filtered]
    return ids, search['hits']['total']['value'], full_texts_filtered
