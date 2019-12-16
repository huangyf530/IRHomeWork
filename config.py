maps =  {"mappings": {
            "properties": {
                "text": {
                    "type": "keyword",
                },
                "poses": {
                    "type": "keyword",
                }
            }
        }
    }

query_template = {
        "query": {
            'bool': {
                "must":[]
            }
        }
    }

files_to_handle = ['/Users/huangyf/Dataset/SogouT/Sogou0012_out', '/Users/huangyf/Dataset/SogouT/Sogou0002_out']