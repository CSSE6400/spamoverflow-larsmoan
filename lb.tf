resource "aws_lb_target_group" "spamscanner" { 
  name          = "spamscanner" 
  port          = 6400 
  protocol      = "HTTP" 
  vpc_id        = aws_security_group.spamscanner.vpc_id 
  target_type   = "ip" 
 
  health_check { 
    path                = "/api/v1/health" 
    port                = "6400" 
    protocol            = "HTTP" 
    healthy_threshold   = 2 
    unhealthy_threshold = 2 
    timeout             = 5 
    interval            = 10 
  } 
}


resource "aws_lb" "spamoverflow" { 
  name               = "spamoverflow-lb" 
  internal           = false 
  load_balancer_type = "application" 
  subnets            = data.aws_subnets.private.ids 
  security_groups    = [aws_security_group.spamoverflow.id] 
} 
 
resource "aws_security_group" "spamoverflow" { 
  name        = "spamoverflow" 
  description = "spamoverflow Security Group" 
 
  ingress { 
    from_port     = 80 
    to_port       = 80 
    protocol      = "tcp" 
    cidr_blocks   = ["0.0.0.0/0"] 
  } 
 
  egress { 
    from_port     = 0 
    to_port       = 0 
    protocol      = "-1" 
    cidr_blocks   = ["0.0.0.0/0"] 
  } 
}

//Listener aka entrypoint to the load balancer
resource "aws_lb_listener" "spamscanner" { 
  load_balancer_arn   = aws_lb.spamoverflow.arn 
  port                = "80" 
  protocol            = "HTTP" 
 
  default_action { 
    type              = "forward" 
    target_group_arn  = aws_lb_target_group.spamscanner.arn 
  } 
}
