terraform {
    required_providers {
        aws = {
            source  = "hashicorp/aws"
            version = "~> 4.0"
        }
        docker = {
            source = "kreuzwerker/docker"
            version = "3.0.2"
        }
    }
}

provider "aws" {
    region = "us-east-1"
    shared_credentials_files = ["./credentials"]
    default_tags {
        tags = {
            Course       = "CSSE6400"
            Name         = "SpamOverflow-lars"
        }
    }
}

data "aws_ecr_authorization_token" "ecr_token" {} 

// ECR Resources
resource "aws_ecr_repository" "spamoverflow" {
  name = "spamoverflow-ecr-repo"
}

resource "docker_image" "spamoverflow_image" {
  name = "${aws_ecr_repository.spamoverflow.repository_url}:latest"

  build {
    context = "."
    dockerfile = "Dockerfile.deploy"    //Uses the deployment dockerfile which ensures compatability with linux
    labels = {
      version = 1.0
    }
  }
}

resource "docker_registry_image" "taskoverflow" {
  name = docker_image.spamoverflow_image.name
}

 
provider "docker" { 
 registry_auth { 
   address = data.aws_ecr_authorization_token.ecr_token.proxy_endpoint 
   username = data.aws_ecr_authorization_token.ecr_token.user_name 
   password = data.aws_ecr_authorization_token.ecr_token.password 
 } 
}

//Terraform works like magic. Somehow the database resource in db.tf can access the locals. variables
locals { 
    database_username = "administrator" 
    database_password = "foobarbaz" # this is bad 
} 

data "aws_iam_role" "lab" { 
   name = "LabRole" 
} 
 
data "aws_vpc" "default" { 
   default = true 
} 
 
data "aws_subnets" "private" { 
   filter { 
      name = "vpc-id" 
      values = [data.aws_vpc.default.id] 
   } 
}


//This is the magic trick to gain access to the url that the load balancer provides?
// I think it gets the DNS from the load balancer and actually writes it to ./api.txt
resource "local_file" "url" {
    content = "http://${aws_lb.spamoverflow.dns_name}/"
    filename = "./api.txt"
}
