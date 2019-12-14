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

query = {
        "query": {
            'bool': {
                "must":[
                    {'match' : {"text": "牛市" }},
                ]
            }
        }
    }

files_to_handle = ['/Users/huangyf/Dataset/SogouT/Sogou0012_out']