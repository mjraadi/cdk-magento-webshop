# Magento Webshop CDK Project with Python

This is a CDK app to provision the required resources to run a flexible, scalable and cost-effective Magento webshop on top of AWS.

### Project Setup

This project is set up like a standard Python project. The initialization
process also creates a virtualenv within this project, stored under the `.venv`
directory. To create the virtualenv it assumes that there is a `python3`
(or `python` for Windows) executable in your path with access to the `venv`
package. If for any reason the automatic creation of the virtualenv fails,
you can create the virtualenv manually.

To manually create a virtualenv on MacOS and Linux:

```
$ python3 -m venv .venv
```

After the init process completes and the virtualenv is created, you can use the following
step to activate your virtualenv.

```
$ source .venv/bin/activate
```

If you are a Windows platform, you would activate the virtualenv like this:

```
% .venv\Scripts\activate.bat
```

Once the virtualenv is activated, you can install the required dependencies.

```
$ pip install -r requirements.txt
```

At this point you can now synthesize the CloudFormation template for this code.

```
$ cdk synth
```

To add additional dependencies, for example other CDK libraries, just add
them to your `setup.py` file and rerun the `pip install -r requirements.txt`
command.

## Useful commands

- `./cdk-run.sh AWSAccountId AWSRegion ls -c config=dev` list all stacks in the app in the development environment
- `./cdk-run.sh AWSAccountId AWSRegion ls -c config=prod` list all stacks in the app in the production environment
- `./cdk-run.sh AWSAccountId AWSRegion synth -c config=dev` emits the synthesized CloudFormation template in the development environment
- `./cdk-run.sh AWSAccountId AWSRegion synth -c config=prod` emits the synthesized CloudFormation template in the production environment
- `./cdk-run.sh AWSAccountId AWSRegion diff -c config=dev` compare deployed stack with current state in the development environment
- `./cdk-run.sh AWSAccountId AWSRegion diff -c config=prod` compare deployed stack with current state in the production environment
- `./cdk-run.sh AWSAccountId AWSRegion deploy -c config=dev` deploy this stack to your provided AWS account/region in the development environment
- `./cdk-run.sh AWSAccountId AWSRegion deploy -c config=prod` deploy this stack to your provided AWS account/region in the production environment
- `cdk docs` open CDK documentation

**Notes:**

- You can use `cdk-run.bat` to run the commands above on Windows
- Be sure to replace `AWSAccountId` and `AWSRegion` with proper values

Enjoy!
