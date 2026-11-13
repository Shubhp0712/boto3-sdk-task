import boto3
import csv 
import json

pricing = boto3.client("pricing", region_name="us-east-1")

price_cache = {}

# This function retrieves the price of an EC2 instance based on its type and region. It uses caching to avoid redundant API calls for the same instance type and region combination.
def get_ec2_price(instance_type, region):
    key = (instance_type, region)
    if key in price_cache:
        return price_cache[key]

    response = pricing.get_products(
        ServiceCode='AmazonEC2',
        Filters=[
            {"Type": "TERM_MATCH", "Field": "regionCode", "Value": region},
            
            {"Type": "TERM_MATCH", "Field": "instanceType", "Value": instance_type},

            {"Type": "TERM_MATCH", "Field": "operatingSystem", "Value": "Linux"},

            {"Type": "TERM_MATCH", "Field": "capacitystatus", "Value": "Used"},        

            {"Type": "TERM_MATCH", "Field": "tenancy", "Value": "Shared"},

            {"Type": "TERM_MATCH", "Field": "preInstalledSw", "Value": "NA"},

            {"Type": "TERM_MATCH", "Field": "productFamily", "Value": "Compute Instance"},
        ]
    )

    for item in response['PriceList']:
        product = json.loads(item)
        terms = product['terms']['OnDemand']

        for term in terms.values():
            price_dimensions = term['priceDimensions']

            for dimension in price_dimensions.values():

                if dimension['unit'] == 'Hrs':
                    price_per_unit = dimension['pricePerUnit']['USD']
                    price_cache[key] = float(price_per_unit)
                    return float(price_per_unit)
    price_cache[key] = None
    return None

# This function retrieves the list of available AWS regions for EC2 instances.
def get_regions():
    ec2 = boto3.client('ec2')
    response = ec2.describe_regions()
    regions = []
    for region in response['Regions']:
        regions.append(f"{region['RegionName']}")
    return regions

# This function retrieves the name of an EC2 instance based on its tags. If the instance has a tag with the key 'Name', it returns the corresponding value; otherwise, it returns 'N/A'.
def get_instance_name(instance):
    if instance.tags:
        for tag in instance.tags:
            if tag['Key'] == 'Name':
                return tag['Value']
    return 'N/A'

csv_headers = [
    "Instance Name",
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
print(f"Retrieved regions: {regions}")

# This loop iterates through each AWS region, retrieves the EC2 instances in that region, and collects relevant information about each instance, including its name, ID, state, type, architecture, launch time, region, and pricing details. The collected data is then appended to the 'data' list for later writing to a CSV file.
for region in regions:
    ec2_instance = boto3.resource('ec2', region_name=region)
    print(f"Region checking for ec2 in {region}")

    for instance in ec2_instance.instances.all():
        instance_type = instance.instance_type
        instance_state = instance.state['Name']
        instance_name = get_instance_name(instance)
        hourly_price_value = get_ec2_price(instance_type, region)

        if instance_state == 'running' and hourly_price_value is not None:
            hourly_cost = hourly_price_value
            daily_cost = hourly_price_value * 24
            monthly_cost = hourly_price_value * 730
        else: 
            hourly_cost = 0
            daily_cost = 0
            monthly_cost = 0

        data.append([
            instance_name, 
            instance.id, 
            instance_state, 
            instance.instance_type, 
            instance.architecture, 
            instance.launch_time, 
            region, 
            hourly_price_value, 
            daily_cost, 
            monthly_cost
        ])

# This block generate the csv file with the collected EC2 instance data. It opens a new CSV file named 'ec2_instances.csv', writes the headers, and then writes each row of instance data to the file.
with open('ec2_instances.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(csv_headers)
    writer.writerows(data)
print("CSV file 'ec2_instances.csv' has been created successfully.")