import boto3

def get_lambda_inventory(session, regions):
    print("Scanning Lambda Inventory...")
    data = []
    
    for region in regions:
        try:
            lamb = session.client('lambda', region_name=region)
            paginator = lamb.get_paginator('list_functions')
            
            for page in paginator.paginate():
                for func in page['Functions']:
                    name = func.get('FunctionName')
                    runtime = func.get('Runtime')
                    last_modified = func.get('LastModified')
                    memory = func.get('MemorySize')
                    timeout = func.get('Timeout')
                    
                    data.append({
                        'Region': region,
                        'FunctionName': name,
                        'Runtime': runtime,
                        'Memory(MB)': memory,
                        'Timeout(s)': timeout,
                        'LastModified': last_modified
                    })
        except Exception as e:
            print(f"Error getting Lambda inventory in {region}: {e}")
            
    return data
