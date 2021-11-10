#!/bin/bash -xe

# Log EC2 Linux user data and then ship it to the console logs
exec > >(tee /var/log/user-data.log|logger -t user-data -s 2>/dev/console) 2>&1

echo "Hello from user-data!"
# install the required packages
sudo yum update -y
sudo yum -y install mysql httpd jq

# define variables
AWS_ACCOUNT_ID="${__AWS_ACCOUNT_ID__}"
AWS_REGION="${__AWS_REGION__}"
MYSQL_INSTANCE_ADDRESS="${__MYSQL_INSTANCE_ADDRESS__}"
MYSQL_SECRET_NAME="${__MYSQL_SECRET_NAME__}"

# retriveing mysql credentials from secrets manager
MYSQL_USER=$(aws secretsmanager get-secret-value \
  --region ${!AWS_REGION} --secret-id ${!MYSQL_SECRET_NAME} \
--query SecretString --output text | jq -r .username)

MYSQL_PWD=$(aws secretsmanager get-secret-value \
  --region ${!AWS_REGION} --secret-id ${!MYSQL_SECRET_NAME} \
--query SecretString --output text | jq -r .password)

# testing mysql connection
# TODO: the password will be visible on user data logs. find a way
# to prevent this
mysql -h ${!MYSQL_INSTANCE_ADDRESS} -u ${!MYSQL_USER} \
-p${!MYSQL_PWD} -e"quit" && \
echo "connecting to MySQL server was successful"

# start the web server on boot
sudo systemctl enable httpd
# start the web server now
sudo systemctl start httpd
echo "<h1>Hello World from $(hostname -f)</h1>" > /var/www/html/index.html