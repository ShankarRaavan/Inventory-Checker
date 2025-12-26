import boto3

def get_ecs_inventory(session, regions):
    print("Scanning ECS Inventory...")
    data = []
    
    for region in regions:
        try:
            ecs = session.client('ecs', region_name=region)
            paginator = ecs.get_paginator('list_clusters')
            
            cluster_arns = []
            for page in paginator.paginate():
                cluster_arns.extend(page['clusterArns'])
                
            if not cluster_arns:
                continue
                
            # Describe clusters in batches of 100 (API limit)
            for i in range(0, len(cluster_arns), 100):
                batch = cluster_arns[i:i+100]
                clusters = ecs.describe_clusters(clusters=batch)['clusters']
                
                for cluster in clusters:
                    name = cluster.get('clusterName')
                    status = cluster.get('status')
                    active_services = cluster.get('activeServicesCount')
                    running_tasks = cluster.get('runningTasksCount')
                    pending_tasks = cluster.get('pendingTasksCount')
                    registered_instances = cluster.get('registeredContainerInstancesCount')
                    
                    data.append({
                        'Region': region,
                        'ClusterName': name,
                        'Status': status,
                        'ActiveServices': active_services,
                        'RunningTasks': running_tasks,
                        'PendingTasks': pending_tasks,
                        'ContainerInstances': registered_instances
                    })
        except Exception as e:
            print(f"Error getting ECS inventory in {region}: {e}")
            
    return data
