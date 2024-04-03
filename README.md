# openapi2apigeex

WORK IN PROGRESS

For this example, imagine you need to start migrating APIs from Sensedia into Apigee. You might need to create a facade in Apigee and start poiting to target backends incrementally. This might help creating that initial layer (the facade).

What is this for:
- This scripts allows you to automatically import APIs into apigee based on a directory of open apis.
- Create an apiproduct for each API
- Implement a standard and static target endpoint for downstream connection.
- Deploys the created revision for a selected environment.

Required:
- pip3 install requests
- npm install -g openapi2apigee

Disclaimer: Open APIs have to be on yaml format.

You can use convertion to achive this purpose.
```shell
yq -p json -o yaml file.json > converted_file.yaml
```


Check the code in **apigee-creator.py**:

### dynamic variables - you should populate this variables:
- main_workdir = '/openapi2apigeex' #define your workdir based on your workspace
- org = "" #this is your apigee x organization (should be the name of the gcp project)
- env = "" #the environment in which you want to deploy your apis.
- version = "api-version" ##this will be applied globally. (used as nomenclature on the proxy name)
- prefix = "define-your-prefix" ##prefix for proxy naming convention.
