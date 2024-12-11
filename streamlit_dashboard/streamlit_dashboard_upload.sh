aws ecr get-login-password --region eu-west-2 | docker login --username AWS --password-stdin 129033205317.dkr.ecr.eu-west-2.amazonaws.com

docker build --platform linux/amd64 -f streamlit_dashboard.dockerfile -t c14-priceslashers-dashboard-ecr:latest .

docker tag c14-priceslashers-dashboard-ecr:latest 129033205317.dkr.ecr.eu-west-2.amazonaws.com/c14-priceslashers-dashboard-ecr:latest

docker push 129033205317.dkr.ecr.eu-west-2.amazonaws.com/c14-priceslashers-dashboard-ecr:latest

