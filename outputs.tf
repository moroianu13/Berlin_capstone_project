output "instance_public_ip" {
  value = aws_instance.web.public_ip
  description = "The public IP address of the EC2 instance"
}

output "ec2_public_dns" {
  value       = aws_instance.web.public_dns
  description = "The public DNS name of the EC2 instance"
}