import boto3
import pandas as pd
from datetime import datetime
import sys

# Import custom inventory modules
from src.get_namespaces import get_namespaces
from src.get_ec2_inventory import get_ec2_inventory
from src.get_rds_inventory import get_rds_inventory
from src.get_ecs_inventory import get_ecs_inventory
from src.get_lambda_inventory import get_lambda_inventory

def get_all_regions(session):
    """
    Get list of all available regions for the account.
    """
    try:
        # us-east-1 is usually a safe default to list regions from
        ec2 = session.client('ec2', region_name='us-east-1')
        regions = [region['RegionName'] for region in ec2.describe_regions()['Regions']]
        return regions
    except Exception as e:
        print(f"Error getting regions: {e}")
        # If we can't list regions, fallback to the session's default region or us-east-1
        default_region = session.region_name or 'us-east-1'
        print(f"Falling back to default region: {default_region}")
        return [default_region]

def main():
    print("Starting AWS Inventory Script...")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"aws_inventory_{timestamp}.xlsx"
    
    try:
        session = boto3.Session()
        # Verify credentials
        sts = session.client('sts')
        identity = sts.get_caller_identity()
        print(f"Authenticated as: {identity['Arn']}")
        
    except Exception as e:
        print("Error: Could not authenticate with AWS. Please check your credentials.")
        print(e)
        sys.exit(1)

    regions = get_all_regions(session)
    print(f"Scanning {len(regions)} Regions: {regions}")
    
    # 1. Namespaces
    print("\n--- Getting CloudWatch Namespaces ---")
    namespaces_data = get_namespaces(session, regions)
    df_ns = pd.DataFrame(namespaces_data)
    
    # 2. EC2
    print("\n--- Getting EC2 Inventory ---")
    ec2_data = get_ec2_inventory(session, regions)
    df_ec2 = pd.DataFrame(ec2_data)
    
    # 3. RDS
    print("\n--- Getting RDS Inventory ---")
    rds_data = get_rds_inventory(session, regions)
    df_rds = pd.DataFrame(rds_data)
    
    # 4. ECS
    print("\n--- Getting ECS Inventory ---")
    ecs_data = get_ecs_inventory(session, regions)
    df_ecs = pd.DataFrame(ecs_data)
    
    # 5. Lambda
    print("\n--- Getting Lambda Inventory ---")
    lambda_data = get_lambda_inventory(session, regions)
    df_lambda = pd.DataFrame(lambda_data)
    
    # Write to Excel
    print(f"\nWriting results to {output_file}...")
    try:
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            # Helper to write sheet
            def write_sheet(df, sheet_name):
                if not df.empty:
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
                else:
                    pd.DataFrame({'Message': ['No data found']}).to_excel(writer, sheet_name=sheet_name, index=False)

            write_sheet(df_ns, 'Namespaces')
            write_sheet(df_ec2, 'EC2')
            write_sheet(df_rds, 'RDS')
            write_sheet(df_ecs, 'ECS')
            write_sheet(df_lambda, 'Lambda')
            
        print("Done! Inventory generation complete.")
    except Exception as e:
        print(f"Error writing Excel file: {e}")

if __name__ == "__main__":
    main()
