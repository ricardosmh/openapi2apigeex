from os import walk, popen
import os
import subprocess
import requests
import json
import yaml

from authenticate import generate_token

#dynamic variables
main_workdir = '/openapi2apigeex' #define your workdir based on your workspace
org = "" #this is your apigee x organization (should be the name of the gcp project)
env = "" #the environment in which you want to deploy your apis.
version = "api-version" ##this will be applied globally. (used as nomenclature on the proxy name)
prefix = "define-your-prefix" ##prefix for proxy naming convention.

#constant variables
domain = "https://apigee.googleapis.com"
token = generate_token()
resource_path = "/v1/organizations/{org}/".format(org = org)


def deploy_api(api_name, rev):
    url = domain + resource_path + "environments/{env}/apis/{api}-apiproxy/revisions/{rev}/deployments".format(env=env, api=api_name, rev=rev)
    query = "?override=true"
    headers = { "Authorization" : "Bearer " + token, 
                "Accept": "application/json" }
    try:
        r = requests.post(  url + query,
                            headers=headers)
        print(r.json())
        if(r):
            print("Status Code: " + str(r.status_code) + " - APIProxy: " + api_name + " deployed revision: " + rev +" in env: "+ env)
    except Exception as e:
        print("Exception: " + str(e))

#create api product in apigee
def create_product(api_name):
    os.chdir(main_workdir)
    headers = { "Authorization" : "Bearer " + token, 
                "Accept": "application/json", 
                "Content-Type": "application/json" }

    #load json template
    product_template = json.load(open('product-template.json'))
    product_template["name"] = api_name + "-apiproduct"
    product_template["displayName"] = api_name + "-apiproduct"
    product_template["description"] = api_name + "-apiproduct"
    product_template["operationGroup"]["operationConfigs"][0]["apiSource"] = api_name + "-apiproxy"

    try:
        r = requests.post(  domain + resource_path + "apiproducts", 
                            headers=headers, 
                            data=json.dumps(product_template))
        if(r):
            print("Status Code: " + str(r.status_code) + " - Published Product: "+ api_name + "-apiproduct" + " to Apigee X")
            
    except Exception as e:
        print("Exception: " + str(e))


#create apis in apigee from bundle
def create_api_apigee(api_name):
    os.chdir(main_workdir)
    query = "?action=import&name={api_name}-apiproxy".format(api_name=api_name)
    
    headers = { "Authorization" : "Bearer " + token, 
                "Accept": "application/json", 
                "Content-Type": "application/octet-stream" }
    
    file_path = "bundles/{api_name}-apiproxy/apiproxy.zip".format(api_name=api_name)
    fileobj = open(file_path, 'rb')
    
    try:
        r = requests.post(  domain + resource_path + "apis" + query, 
                            headers=headers, 
                            files={"file": ("apiproxy.zip", fileobj)})
        if(r):
            print("Status Code: " + str(r.status_code) + " - Published APIProxy: "+ api_name + "-apiproxy" + " to Apigee X")
            
            #returning the revision number of the apiproxy just created
            return r.json()["revision"]
    except Exception as e:
        print("Exception: " + str(e))

#compress api proxy bundle prior to import
def compile_bundle(api_name): 
    os.chdir('bundles/{api_name}-apiproxy'.format(api_name=api_name))
    subprocess.check_call('zip -r apiproxy.zip apiproxy', shell=True)

#replace default sensedia configs
def replace_target_server_config(api_name):
    #replaces static sensedia target config
    os.popen('cp manifest/default-target.xml bundles/{api_name}-apiproxy/apiproxy/targets/default.xml'.format(api_name=api_name))

#create api from oas file   
def create_bundle(api_name, api):
    subprocess.check_call('openapi2apigee generateApi {api_name}-apiproxy -s openapis/{api}.yaml -d bundles/'.format(api_name = api_name, api = api), shell=True)
    #removes pre created bundle from bundle folder
    os.remove("bundles/{api_name}-apiproxy/apiproxy.zip".format(api_name=api_name))

#adding host and schemes to oas files
def repair_oas(apiname):
    correction = { 'host': 'apis.tarjetaoh.com.pe',
             'schemes': ['https'] }
    relative_path = "openapis/" + apiname + ".yaml"
    with open(relative_path,'r') as yamlfile:
        cur_yaml = yaml.safe_load(yamlfile) # Note the safe_load
        cur_yaml.update(correction)
        if cur_yaml:
            with open(relative_path,'w') as yamlfile:
                yaml.safe_dump(cur_yaml, yamlfile)

# fetch all name of the apis based on oas.yaml file name.
def get_file_names():
    mypath = "openapis"
    filenames = next(walk(mypath), (None, None, []))[2]  # [] if no file
    clean_names = []
    for name in filenames:
        clean_names.append(name.replace(".yaml", ""))
    return clean_names

## Main function, invoking each api to be prepared and created.
def create_apis(version, prefix):
    file_names = get_file_names()
    for filename in file_names:
        os.chdir(main_workdir)
        api_name = "{prefix}-{api}-{v}".format(api = filename, v = version, prefix=prefix)
        
        repair_oas(filename)
        create_bundle(api_name, filename)
        replace_target_server_config(api_name)
        compile_bundle(api_name)
        revision_number = create_api_apigee(api_name)
        deploy_api(api_name, revision_number)
        create_product(api_name)

if __name__ == '__main__':
    create_apis(version, prefix)