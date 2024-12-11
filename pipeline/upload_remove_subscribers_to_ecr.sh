aws ecr get-login-password --region eu-west-2 | docker login --username AWS --password-stdin 129033205317.dkr.ecr.eu-west-2.amazonaws.com

docker build --platform linux/amd64 -f remove_subscribers.dockerfile -t c14-priceslashers-subscription-checker-repo .

docker tag c14-priceslashers-subscription-checker-repo:latest 129033205317.dkr.ecr.eu-west-2.amazonaws.com/c14-priceslashers-subscription-checker-repo:latest

docker push 129033205317.dkr.ecr.eu-west-2.amazonaws.com/c14-priceslashers-subscription-checker-repo:latest

