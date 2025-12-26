import boto3

def get_ec2_inventory(session, regions):
    print("Scanning EC2 Inventory...")
    data = []
    
    for region in regions:
        try:
            ec2 = session.client('ec2', region_name=region)
            paginator = ec2.get_paginator('describe_instances')
            
            for page in paginator.paginate():
                for reservation in page['Reservations']:
                    for instance in reservation['Instances']:
                        instance_id = instance.get('InstanceId')
                        instance_type = instance.get('InstanceType')
                        state = instance.get('State', {}).get('Name')
                        launch_time = instance.get('LaunchTime')
                        private_ip = instance.get('PrivateIpAddress')
                        public_ip = instance.get('PublicIpAddress')
                        vpc_id = instance.get('VpcId')
                        
                        # Extract Name tag if exists
                        name = ""
                        if 'Tags' in instance:
                            for tag in instance['Tags']:
                                if tag['Key'] == 'Name':
                                    name = tag['Value']
                                    break
                        
                        data.append({
                            'Region': region,
                            'InstanceId': instance_id,
                            'Name': name,
                            'Type': instance_type,
                            'State': state,
                            'PrivateIP': private_ip,
                            'PublicIP': public_ip,
                            'VpcId': vpc_id,
                            'LaunchTime': str(launch_time)
                        })
        except Exception as e:
            print(f"Error getting EC2 inventory in {region}: {e}")
            
    return data
