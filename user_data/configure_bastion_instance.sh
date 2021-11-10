#!/bin/bash -xe

# Log EC2 Linux user data and then ship it to the console logs
exec > >(tee /var/log/user-data.log|logger -t user-data -s 2>/dev/console) 2>&1

echo "Hello from user-data!"
# define variables
MY_SQL_INSTANCE_ADDRESS="${__MY_SQL_INSTANCE_ADDRESS__}"

# install the required packages
sudo yum update -y
sudo yum -y install mysql

# TODO: test connection, get credentionals from secrets manager
# mysql -h ${!__MY_SQL_INSTANCE_ADDRESS__} -u user -p<whatever> -e"quit"
