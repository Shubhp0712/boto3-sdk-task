import boto3
import csv 

ec2 = boto3.client('ec2')

def get_regions():
    response = ec2.describe_regions()
    regions = []
    for region in response['Regions']:
        regions.append(f"{region['RegionName']}")
    return regions

hourly_price = {
    't2.micro': 0.0116,
    't2.small': 0.023,
    't3.micro': 0.0104,
    't3.small': 0.0208,
    't3.medium': 0.0416,
    't2.medium': 0.0464,
    'm5.large': 0.096,
    'm5.xlarge': 0.192,
}


csv_headers = [
    "Instance ID",
    "State",
    "Instance Type",
    "Architecture",
    "Start Time",
    "Region",
    "Hourly Price",
    "Daily Price",
    "Monthly Price",
]

data = []
regions = get_regions()
for region in regions:
    ec2_instance = boto3.resource('ec2', region_name=region)
    for instance in ec2_instance.instances.all():
        instance_type = instance.instance_type
        instance_state = instance.state['Name']

        if instance_state == 'running':
            hourly_price_value = hourly_price.get(instance_type, 0)
            daily_price_value = hourly_price_value * 24
            monthly_price_value = hourly_price_value * 24 * 30
        else: 
            hourly_price_value = 0
            daily_price_value = 0
            monthly_price_value = 0

        data.append(f"{instance.id}, {instance.state['Name']}, {instance.instance_type}, {instance.architecture}, {instance.launch_time}, {region}, {hourly_price[instance.instance_type]}, {daily_price_value:.4f}, {monthly_price_value:.4f}")  

with open('ec2_instances.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(csv_headers)
    for row in data:
        writer.writerow(row.split(', '))