import boto3

def get_namespaces(session, regions):
    """
    Retrieves distinct CloudWatch namespaces across all specified regions.
    """
    rows = []
    print("Scanning CloudWatch Namespaces...")
    
    for region in regions:
        try:
            cw = session.client('cloudwatch', region_name=region)
            paginator = cw.get_paginator('list_metrics')
            seen_in_region = set()
            
            # Using list_metrics can be slow, but it's the only way to get exact custom namespaces too.
            for page in paginator.paginate():
                for m in page['Metrics']:
                    ns = m['Namespace']
                    if ns not in seen_in_region:
                        seen_in_region.add(ns)
                        rows.append({'Region': region, 'Namespace': ns})
        except Exception as e:
            print(f"Error checking namespaces in {region}: {e}")

    return rows
