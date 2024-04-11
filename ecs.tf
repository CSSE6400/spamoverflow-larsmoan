resource "aws_ecs_cluster" "spamoverflow" {
  name = "spamoverflow-ecs-cluster"
}

resource "aws_ecs_task_definition" "spamscanner" {
  family                   = "spamscanner"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = 1024
  memory                   = 2048
  execution_role_arn       = data.aws_iam_role.lab.arn

  container_definitions = jsonencode([
    {
      image        = "${aws_ecr_repository.spamoverflow.repository_url}:latest"
      cpu          = 1024
      memory       = 2048
      name         = "spamscanner"
      networkMode  = "awsvpc"
      portMappings = [
        {
          containerPort = 6400
          hostPort      = 6400
        }
      ]
      environment = [
        {
          name  = "SQLALCHEMY_DATABASE_URI"
          value = "postgresql://${local.database_username}:${local.database_password}@${aws_db_instance.database.address}:${aws_db_instance.database.port}/${aws_db_instance.database.db_name}"
        }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"            = "/spamoverflow/spamscanner"
          "awslogs-region"           = "us-east-1"
          "awslogs-stream-prefix"    = "ecs"
          "awslogs-create-group"     = "true"
        }
      }
    }
  ])
}

resource "aws_ecs_service" "spamoverflow" {
  name            = "spamoverflow"
  cluster         = aws_ecs_cluster.spamoverflow.id
  task_definition = aws_ecs_task_definition.spamscanner.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets             = data.aws_subnets.private.ids
    security_groups     = [aws_security_group.spamscanner.id]
    assign_public_ip    = true
  }

  load_balancer { 
    target_group_arn = aws_lb_target_group.spamscanner.arn 
    container_name   = "spamscanner" 
    container_port   = 6400 
  }

}

//Security group for the task?
resource "aws_security_group" "spamscanner" {
  name = "spamscanner"
  description = "SpamoverFlow Security Group"

  ingress {
    from_port = 6400
    to_port = 6400
    protocol = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port = 22
    to_port = 22
    protocol = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port = 0
    to_port = 0
    protocol = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
