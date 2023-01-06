These are the steps for setting up a feature/staging localhost

1. Clone compose services checkout to feature/staging 
```sh
git clone [ADDRESS OF feature/staging]
git checkout feature/staging
cd compose-services trainign
```

2.  Change. Etl/dockerfile From python:3.10 to From python:3.9
Assuming that you’re running python 3.9 locally 

3. If on a new machine the  etc/hosts additions from https://github.com/ACED-IDP/compose-services-training/blob/feature/staging/docs/aced.md 
(it’s in 2 different places so you should be adding around 10 lines in total)
```sh
sudo vim /etl/hosts
```

4. Do a creds setup like this: 
```sh
bash ./creds_setup.sh aced-training.compbio.ohsu.edu
```

5. Drag in all files from examples/Secrets   to Secrets directory and overwrite all of the secrets directory files. The ones in examples/Secrets are more up to date

6.
```sh
docker compose up -d 
```
you should see the page with a working fence

7. Generate a credentials.json file and save it to Secrets directory by clicking on the profile button and create API key button and download json file button 

8. Replace the 2 certs service.crt and service.key in your TLS folder
With the ones provided from the development.aced-idp server this may require you to ssh into it, refer to step 11.

9. Make a new program and project following this guide:
https://github.com/uc-cdis/compose-services/blob/master/docs/using_the_commons.md#programs-and-projects

But instead of using MyFirstProgram for the program name use aced and instead of using MyFirstProject for the project name follow the conventions in the command listed on step 10 for arguments project_code being STUDY and program_name being aced

10. Execute the following command from the data_model directory within a virtual environment:

```sh
python3 -m venv venv
source venv/bin/activate
```

 It uploads files into buckets:
```sh
nice -n 10 scripts/upload-files STUDY BUCKET &
```
 Load the meta data: 
```sh
nice -n 10 python3 scripts/emitter.py data load  --project_code STUDY --input_path output/STUDY/extractions  --db_host localhost --program_name aced  --sheepdog_creds_path ../compose-services-training/Secrets/sheepdog_creds.json 
```
```txt
STUDY        		BUCKET
Alcoholism		  aced-ohsu
Alzheimers		  aced-ucl
Breast_Cancer		aced-manchester
Colon_Cancer		aced-stanford
Diabetes			  aced-ucl
Lung_Cancer		  aced-manchester
Prostate_Cancer	aced-stanford
```

11. Ssh into staging via 
```sh
ssh ubuntu@staging.aced-idp.org 
```

For each copy to . (The current directory) Pay attention where The directory is in Staging.aced-idp.org. 

12. Make a new folder called data_model that is a sibling folder to compose-services-training this is the folder that all of the scp are going to

13. Run all of these commands to copy all of the required Packages and files into data model:
```sh
scp ubuntu@staging.aced-idp.org:/home/ubuntu/data_model/output/all_studies-2.zip .
```
Unzip all of the studies from all studies and put them into the output folder.
```sh
scp -r ubuntu@staging.aced-idp.org:/home/ubuntu/data_model/output/dicom .
```
Where . Is data_model/output directory
(This one takes some time and might be optional I’m not sure)

```sh
scp -r ubuntu@staging.aced-idp.org:/home/ubuntu/data_model/output/dna .
```
Where . Is data_model/output directory

```sh
scp -r ubuntu@staging.aced-idp.org:/home/ubuntu/data_model/output/gen3 .
```
Where . Is data_model/output directory

```sh
scp -r ubuntu@staging.aced-idp.org:/home/ubuntu/data_model/scripts .
```
Where . Is data_model directory

```sh
scp ubuntu@staging.aced-idp.org:/home/ubuntu/data_model/config.yaml .
```
Where . Is data_model directory

These two package folders should go in data_model/scripts directory
```sh
scp -r ubuntu@staging.aced-idp.org:/home/ubuntu/data_model/venv/lib/python3.9/site-packages/jwt .
 
scp -r ubuntu@staging.aced-idp.org:/home/ubuntu/data_model/venv/lib/python3.9/site-packages/pelican .
```

Change the name of data_model/output/STUDY/extract to
data_model/output/STUDY/extractions (or look for where it is in the code and change it)

Pip install all of the other required non-standard packages that will be shown in 
Emmitter.py at the top of the file

14. Re-enable guppy services  in Nginx.conf if you never disabled it disregard this step. L:147-149 or search for guppy and uncomment out the three lines where it is referenced 


15. Virtual environment  for guppy setup this time downloading the etl/requirements.txt 
16. 
```sh
python3 -m venv venv
source venv/bin/activate
pip install -r etl/requirements.txt
```

16. 
```sh
bash guppy_setup.sh Secrets/credentials.json
```
This should not fail if it does fail consider doing a docker compose restart especially if it talks about permissions errors
Also consider running this line 

```sh
python3 -m pip uninstall certifi 
python3 -m pip install certifi 
```
if you’re having problems with certification issues, you may have to do this step.

you will have to wait until esproxy-service is running for guppy setup to work this can take some time. docker compose ps to check if it is running or not.  

17. Restart everything with 
```sh
docker compose restart
```

