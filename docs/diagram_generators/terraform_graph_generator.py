from diagrams import Cluster, Diagram
from diagrams.custom import Custom
from diagrams.onprem.client import User
from diagrams.aws.compute import ElasticContainerService, EC2, EC2Ami


# A terraform node that has arrows connected to 3 nodes

# These 3 nodes are AWS Provider, Hashicorp Random Provider, Mongodb Atlas Provider

# The AWS Provider is connected to two variables which are var.AWS_ACCESS_KEY and var.AWS_SECRET_KEY

# For the AWS Provider

with Diagram("Infrastructure created by Terraform", show=True):
    # Desgin Terraform and Provider nodes
    tf = Custom("", "./images/terraform.png")

    with Cluster("Providers"):
        aws = Custom("", "./images/aws.png")
        hashicorp_random = Custom("Random", "./images/hashicorp.png")
        mongodb_atlas = Custom("MongoDB Atlas", "./images/mongodb_atlas.png")
        providers = [aws, hashicorp_random, mongodb_atlas]
    
    tf >> providers

    # Design the MongoDB Atlas side (and do the AWS side later)
    with Cluster("Database"):
        ## Design the DB User
        mongodb_atlas_db_user = User("DB User")
        mongodb_atlas >> mongodb_atlas_db_user
        ## Design the Serverless Instance
        mongodb_atlas >> Custom("Serverless", "./images/serverless_instance.png")

    ## Design the random password created by Hashicorp Random
    random_password = Custom("Random Password", "./images/password.png")
    hashicorp_random >> random_password
    ## Modify this link so that it's not a direct arrow
    mongodb_atlas_db_user - random_password
    
    # Design the EC2 cluster

    with Cluster("Jenkins Server on EC2") as ec2:
        ## Design the Ubuntu AMI
        ubuntu_ami = EC2Ami("Ubuntu AMI")
        # Design the EC2 Instance
        ec2_instance = EC2("EC2 Instance")
        ## Design the Security Group
        security_group = Custom("Security Group", "./images/security_group.png")
        ec2_instance - ubuntu_ami
        ec2_instance - security_group
        ec2_cluster = [ubuntu_ami, security_group, ec2_instance]

    aws >> ec2_instance
