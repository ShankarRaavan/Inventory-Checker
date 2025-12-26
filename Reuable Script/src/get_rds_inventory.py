import boto3

def get_rds_inventory(session, regions):
    print("Scanning RDS Inventory...")
    data = []
    
    for region in regions:
        try:
            rds = session.client('rds', region_name=region)
            paginator = rds.get_paginator('describe_db_instances')
            
            for page in paginator.paginate():
                for db in page['DBInstances']:
                    db_identifier = db.get('DBInstanceIdentifier')
                    engine = db.get('Engine')
                    status = db.get('DBInstanceStatus')
                    instance_class = db.get('DBInstanceClass')
                    allocated_storage = db.get('AllocatedStorage')
                    endpoint = db.get('Endpoint', {}).get('Address')
                    
                    data.append({
                        'Region': region,
                        'DBIdentifier': db_identifier,
                        'Engine': engine,
                        'Class': instance_class,
                        'Status': status,
                        'Storage(GB)': allocated_storage,
                        'Endpoint': endpoint
                    })
        except Exception as e:
            print(f"Error getting RDS inventory in {region}: {e}")
            
    return data
