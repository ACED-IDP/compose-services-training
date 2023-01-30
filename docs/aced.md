- [ACED specific changes](#aced-specific-changes)
  - [Fence (Authentication and Authorization)](#fence-authentication-and-authorization)
    - [Setup](#setup)
    - [Windmill's Auth Display](#windmills-auth-display)
    - [Database Migrations](#database-migrations)
    - [Authentication](#authentication)
    - [Certs](#certs)
    - [Customize Fence](#customize-fence)
  - [Guppy and Kibana (Data)](#guppy-and-kibana-data)
    - [Manual TSV Upload](#manual-tsv-upload)
    - [`metadata` Command Upload](#metadata-command-upload)
    - [API](#api)
    - [Re-Enable Guppy](#re-enable-guppy)
    - [Expose the Kibana Service](#expose-the-kibana-service)
    - [Refactor the Spark and Tube Services](#refactor-the-spark-and-tube-services)
    - [Local Object Store (Minio)](#local-object-store-minio)
  - [Let's Setup Discovery](#lets-setup-discovery)
  - [Enable jupyter notebooks](#enable-jupyter-notebooks)
- [Microservices Reference](#microservices-reference)

# ACED specific changes

> This document assumes you have completed setting up a 'stock' gen3 instance as described in https://github.com/uc-cdis/compose-services
> 
> Now that you've completed this task, let's explore some ACED specific customizations.

## Fence (Authentication and Authorization)

> Fence is the main authentication mechanism for Gen3.   Let's add some ACED specifics ...

### Setup

> Let's create an instance that should be hosted on  aced-training.compbio.ohsu.edu

You should have already seen this in the compose services docs for `bash ./creds_setup.sh aced-training.compbio.ohsu.edu`

To test locally, update your `/etc/hosts` file.

```
# testing
127.0.0.1 aced-training.compbio.ohsu.edu
127.0.0.1 minio.compbio.ohsu.edu
127.0.0.1 minio-console.compbio.ohsu.edu
```
### Windmill's Auth Display
  
add to Secrets/gitops.json
```json
"showArboristAuthzOnProfile": true,
"showFenceAuthzOnProfile": false
```

You should now see detailed authorization in the profile screen.

![image](profile.png)

### Database Migrations

> The fence service will automatically apply a database migration on startup.   We don't want to do that every time, let's turn that off

In Secrets/fence-config.yaml
```
ENABLE_DB_MIGRATION: false   
```

Now, when you re-start fence-service, you should see this message
```
fence-service  | [2022-09-06 21:27:31,812][     fence][   INFO] NOT running database migration.
```

### Authentication

> For testing, we won't configure OAuth, we will use a default user "test"

* Let's turn off auth: Secrets/fence-config.yaml#L48-L49

```yaml
# if true, will automatically login a user with username "test"
MOCK_AUTH: true
```

* Then adjust the user mapping to make the "test" user admin. In Secrets/user.yaml, change all occurrences of `username1@gmail.com` to `test`

* Then restart fence.
```sh
docker-compose stop fence-service ; docker-compose rm  -f fence-service ; docker-compose up -d fence-service ;
```

### Certs

* If you are on an exastack node (or AWS instance) and want to use the official certificate, please ask for access:

```
https://ohsuitg-my.sharepoint.com/ XXXXX
```

* Once you have access, to install the certificate in gen3 follow these steps, assuming certs directory in ~/compbio-tls

```sh
cp /home/ubuntu/compbio-tls/compbio-tls/compbio.ohsu.edu-2022.interim-bundle.pem  ./Secrets/TLS/service.crt
cp /home/ubuntu/compbio-tls/compbio-tls/compbio.ohsu.edu-2022.key ./Secrets/TLS/service.key   
```

### Customize Fence

PRs to allow user to upload file to any of the buckets fence manages.
https://github.com/uc-cdis/gen3sdk-python/pull/158
https://github.com/uc-cdis/fence/pull/1048

> These steps assume the PRs have _not_ been merged to main.

* Clone fence in the compose-services dir. checkout the `alternate-data_upload_bucket` branch  
* Alter docker-compose.

```diff
-    image: "quay.io/cdis/fence:2021.03"
+    #image: "quay.io/cdis/fence:2021.03"
+    build: fence
```

* update etl/requirements.txt to point to client side PR

```diff
# etl/requirements.txt
-gen3
+#  gen3
+https://github.com/ohsu-comp-bio/gen3sdk-python/archive/feat/alternate-data_upload_bucket.zip
```

## Guppy and Kibana (Data)

* Per instructions, to disable guppy and kibana see https://github.com/uc-cdis/compose-services/blob/master/docs/setup.md#start-running-your-local-gen3-docker-compose-environment

* Create a program (MyFirstProgram) and project (MyFirstProject).  See https://github.com/uc-cdis/compose-services/blob/master/docs/using_the_commons.md#programs-and-projects

* Activate the virtual environment and install required packages.

```sh
python3 -m venv venv
source venv/bin/activate
pip install -r etl/requirements.txt
```

* Let's generate some synthetic meta data

```sh
export TEST_DATA_PATH="$(pwd)/tests/fixtures/projects/MyFirstProject"
mkdir -p "$TEST_DATA_PATH"

docker run -it -v "${TEST_DATA_PATH}:/mnt/data" --rm --name=dsim --entrypoint=data-simulator quay.io/cdis/data-simulator:master simulate --url https://s3.amazonaws.com/dictionary-artifacts/datadictionary/develop/schema.json --path /mnt/data --program MyFirstProgram --project MyFirstProject --max_samples 10
```

* Now, let's generate corresponding data files

```sh
./etl/generate_simulated_files --project_path tests/fixtures/projects/MyFirstProject --output_path tests/fixtures/projects/MyFirstProject/DATA

./etl/file --gen3_credentials_file Secrets/credentials.json upload --project_path tests/fixtures/projects/MyFirstProject/
```
### Manual TSV Upload

* Load the data manually by following the [instructions](https://gen3.org/resources/user/submit-data/#begin-metadata-tsv-submissions)
(Note that the data we will be using is in JSON form.) This will be a good opportunity to discover data dependency order. Navigate to the "Submit Data" page. Load the data, following the hierarchy displayed in the "Toogle View"

![image](graph-view.png)

* When complete, the graph should look like this.

![image](graph-view-complete.png)

### `metadata` Command Upload

* Alternatively, to upload the metadata with the `metadata` command enter the following:

```sh
./etl/metadata --gen3_credentials_file Secrets/credentials.json load --project MyFirstProject --program MyFirstProgram --data_directory tests/fixtures/projects/MyFirstProject/
```

### API

This may be a good time to examine the Gen3 API.  You will need an API key first.

![image](profile-create-key.png)

For example, view the `metadata` script, where `credentials.json` is the key file downloaded above.

List the schema entities: 

```sh
./etl/metadata --gen3_credentials_file Secrets/credentials.json ls  | jq .

{
"programs": {
"MyFirstProgram": [
"MyFirstProject",
"MySecondProject"
]
},
"entities": [
"program",
"project",
"acknowledgement",
"core_metadata_collection",
"experiment",
"keyword",
"publication",
"experimental_metadata",
"submitted_copy_number",
"case",
"demographic",
"diagnosis",
"sample",
"exposure",
"family_history",
"clinical_test",
"aliquot",
"slide",
"treatment",
"slide_image",
"submitted_methylation",
"read_group",
"slide_count",
"submitted_aligned_reads",
"submitted_somatic_mutation",
"submitted_unaligned_reads",
"aligned_reads_index",
"read_group_qc"
]
}

```

### Re-Enable Guppy

* (Re)Read the [documentation](https://github.com/uc-cdis/compose-services/blob/master/docs/using_the_commons.md#configuring-guppy-for-exploration-page)  
* Rollback comment out of guppy in nginx.conf
* Rollback comment out of kibana in docker-compose.yml
* Run `bash guppy_setup.sh`  - this should run the spark, tube service and launch the guppy service.  

### Expose the Kibana Service

* Add the kibana path to `nginx.conf`

```diff
+++ b/nginx.conf
@@ -276,5 +276,17 @@ http {
location /lw-workspace/ {
return 302 /lw-workspace/proxy;
}
+
+        location /kibana {
+          proxy_http_version 1.1;
+          proxy_set_header Upgrade $http_upgrade;
+          proxy_set_header Connection 'upgrade';
+          proxy_set_header Host $host;
+          proxy_cache_bypass $http_upgrade;
+
+          proxy_pass  http://kibana-service:5601/;
+          rewrite ^/kibana/(.*)$ /$1 break;
+        }
+
}
}
```   

* add the path to docker-compose

```diff
kibana-service:
image: quay.io/cdis/kibana-oss:6.5.4
container_name: kibana-service
environment:
- SERVER_NAME=kibana-service
- ELASTICSEARCH_URL=http://esproxy-service:9200
+      - SERVER_BASEPATH=/kibana
ports:
- 5601:5601
networks:

```

### Refactor the Spark and Tube Services

* Update the docker compose to disable the spark and tube service

```diff
@@ -283,42 +287,42 @@ services:
- fence-service
- portal-service
- pidgin-service
-  tube-service:
-    image: "quay.io/cdis/tube:2021.03"
-    container_name: tube-service
-    command: bash -c "while true; do sleep 5; done"
-    networks:
-      - devnet

...
```

* Run the `tube-lite` replacement of spark and tube

```sh
./etl/tube_lite --credentials_path Secrets/credentials.json  --elastic http://localhost:9200
```

* Alter `guppy-setup.sh` to run the tube_lite

```diff
diff --git a/guppy_setup.sh b/guppy_setup.sh
index 559668d..5081eb1 100644
--- a/guppy_setup.sh
+++ b/guppy_setup.sh
@@ -1,16 +1,9 @@
#!/bin/bash
# Script to create and re-create es indices and setup guppy

-sleep 2
-docker exec esproxy-service curl -X DELETE http://localhost:9200/etl_0
-sleep 2
-docker exec esproxy-service curl -X DELETE http://localhost:9200/file_0
-sleep 2
-docker exec esproxy-service curl -X DELETE http://localhost:9200/file-array-config_0
-sleep 2
-docker exec esproxy-service curl -X DELETE http://localhost:9200/etl-array-config_0
-sleep 2
-docker exec tube-service bash -c "python run_config.py && python run_etl.py"
-
+docker exec esproxy-service curl -X DELETE http://localhost:9200/gen3.aced.*
docker container stop guppy-service
+
+./etl/tube_lite --credentials_path $1  --elastic http://localhost:9200
+
docker container start guppy-service

```

* Examine the results using [kibana](http://localhost:5601/app/kibana#/dev_tools/console?_g=())

![image](kibana.png)

* Examine the results in the [portal](http://localhost/files)

![image](portal-tube-results.png)

### Local Object Store (Minio)

* Add the following to `/etc/hosts` for local host testing.

```
127.0.0.1 minio-default.compbio.ohsu.edu
127.0.0.1 minio-default-console.compbio.ohsu.edu
127.0.0.1 minio-ohsu.compbio.ohsu.edu
127.0.0.1 minio-ohsu-console.compbio.ohsu.edu
127.0.0.1 minio-ucl.compbio.ohsu.edu
127.0.0.1 minio-ucl-console.compbio.ohsu.edu
127.0.0.1 minio-manchester.compbio.ohsu.edu
127.0.0.1 minio-manchester-console.compbio.ohsu.edu
127.0.0.1 minio-stanford.compbio.ohsu.edu
127.0.0.1 minio-stanford-console.compbio.ohsu.edu
```

* Add the minio.conf file to the revproxy-service

```diff
$ git diff docker-compose.yml
diff --git a/docker-compose.yml b/docker-compose.yml
index 62c536d..0a0f03f 100644
--- a/docker-compose.yml
+++ b/docker-compose.yml
@@ -269,6 +269,7 @@ services:
- devnet
volumes:
- ./nginx.conf:/etc/nginx/nginx.conf
+      - ./minio.conf:/etc/nginx/minio.conf
- ./Secrets/TLS/service.crt:/etc/nginx/ssl/nginx.crt
- ./Secrets/TLS/service.key:/etc/nginx/ssl/nginx.key
ports:
```

* Add the minio configuration to `docker-compose-override.yml` 

* Start the service

```dc up -d ; dc logs -f minio-default```

* Setup minio
```yaml
cat etl/setup-minio.sh |  docker exec -i  etl-service bash

```

* Examine logs

```sh
$ dc logs  minio-default
minio1-service  | Formatting 1st pool, 1 set(s), 2 drives per set.
minio1-service  | WARNING: Host minio1-service:9000 has more than 1 drives of set. A host failure will result in data becoming unavailable.
minio1-service  | MinIO Object Storage Server
minio1-service  | Copyright: 2015-2022 MinIO, Inc.
minio1-service  | License: GNU AGPLv3 <https://www.gnu.org/licenses/agpl-3.0.html>
minio1-service  | Version: RELEASE.2022-09-01T23-53-36Z (go1.18.5 linux/arm64)
minio1-service  |
minio1-service  | Status:         2 Online, 0 Offline.
minio1-service  | API: http://172.19.0.2:9000  http://127.0.0.1:9000
minio1-service  | Console: http://172.19.0.2:9001 http://127.0.0.1:9001
minio1-service  |
minio1-service  | Documentation: https://docs.min.io  
```

* Verify connection

* `curl http://minio-default.compbio.ohsu.edu/minio/health/live`
* open http://minio-default-console.compbio.ohsu.edu
* repeat for other minio-* servers

* Enable fence URL signing
* see AWS_CREDENTIALS, S3_BUCKETS in Secrets/fence-config.yml

* Now, let's empty the project, then re-create the project end to end.

```sh
# empty the project
./etl/metadata --gen3_credentials_file Secrets/credentials.json empty --program MyFirstProgram --project MyFirstProject
# upload the data files
./etl/file --gen3_credentials_file Secrets/credentials.json upload --project_path tests/fixtures/projects/MyFirstProject/
# upload the meta data
./etl/metadata --gen3_credentials_file Secrets/credentials.json  load --project MyFirstProject --program MyFirstProgram --data_directory tests/fixtures/projects/MyFirstProject/
# re-create the elastic search indices
bash ./guppy_setup.sh Secrets/credentials.json
```

## Let's Setup Discovery

* Update the metadata service image

```diff
metadata-service:
-    image: "quay.io/cdis/metadata-service:2021.03"
+    image: "quay.io/cdis/metadata-service:1.8.0"
container_name: metadata-service
depends_on:
- postgres
+    volumes:
+      # /env/bin/python /src/src/mds/populate.py --config /var/local/metadata-service/aggregate_config.json
+      - ./Secrets/metadata/aggregate_config.json:/var/local/metadata-service/aggregate_config.json
environment:
- DB_HOST=postgres
- DB_USER=metadata_user
- DB_PASSWORD=metadata_pass
- DB_DATABASE=metadata
+      - USE_AGG_MDS=true
+      - GEN3_ES_ENDPOINT=http://esproxy-service:9200
command: >
```

* Update gitops.json

See example/Secrets

## Enable jupyter notebooks

* All we need to do is specify trusted domain for the jupyter notebook in docker-compose.yml

```diff
environment:
-      - FRAME_ANCESTORS=http://localhost
+      - FRAME_ANCESTORS=http://aced-training.compbio.ohsu.edu
revproxy-service:
```

## Change the data dictionary

* Update the data dictionary.  In this case we've updated it from the data_dictionary repo.
  * Note: This is not the only potential source of changes, see https://github.com/uc-cdis/compose-services/blob/master/docs/using_the_commons.md#changing-the-data-dictionary

```commandline
  cp ../data_model/DATA/gen3/*.yaml datadictionary/gdcdictionary/schemas/
  #  "compile" the yaml into a single json file
  python3 etl/compile.py datadictionary/gdcdictionary/schemas/  --out datadictionary/
  #  copy the resulting datadictionary/aced.json  to S3
  # verify you can read https://aced-public.s3.us-west-2.amazonaws.com/aced.json
```
 
* Set the new datadictionary URL in docker-compose
```commandline
git diff docker-compose.yml 
diff --git a/docker-compose.yml b/docker-compose.yml
index 7d139a0..6280178 100644
--- a/docker-compose.yml
+++ b/docker-compose.yml
@@ -125,7 +125,7 @@ services:
       - ./scripts/peregrine_setup.sh:/peregrine_setup.sh
       - ./datadictionary/gdcdictionary/schemas:/schemas_dir
     environment: &env
-      DICTIONARY_URL: https://s3.amazonaws.com/dictionary-artifacts/datadictionary/develop/schema.json
+      DICTIONARY_URL: https://aced-public.s3.us-west-2.amazonaws.com/aced.json

```

* add custom graphql section to 
* Review services
  * restart services as necessary, typically peregrine, sheepdog and portal
    * comment out guppy in nginx.conf until we re-build guppy 
  * see https://github.com/uc-cdis/compose-services/blob/master/docs/using_the_commons.md#changing-the-data-dictionary* 

### Import data files from the study into gen3

```commandline
 python3 etl/file --gen3_credentials_file  Secrets/credentials.json upload-pfb  --pfb_path output/research_study_Alzheimers.pfb > file-object_ids.ndjson
```

* This will upload the files into gen3's indexd & mino's default_bucket.   
* Indexd's object ids are saved to file-object_ids.ndjson

### Import metadata into gen3

```commandline
 python3 etl/import_pfb.py 
Importing output/research_study_Alzheimers.pfb into MyFirstProgram-MyFirstProject project node d8668bf7-ed94-5fe2-bc2c-24a9ede57d4f
2022-10-10 14:50:29.497221
total_count 10000 Practitioner 2022-10-10 14:50:49.200088
...
total_count 450000 DocumentReference 2022-10-10 15:22:35.035110
total_count 460000 DocumentReference 2022-10-10 15:23:22.449487
Elapsed time: 0:32:58.921382 total_count 461412

```

### Try some Graphql queries "Graph"

````commandline
{
  program {
    id
    name
    projects {
      id
      code
      ResearchStudies {
        id
        state
        title
        ResearchSubjects(first: 1) {
          id
          Patients {
            id
            Specimen {
              Tasks {
                id
                DocumentReferences {
                  ga4gh_drs_uri
                }
              }
            }
            Observations {
              id
              category_coding_observation_category
              code_text
              valueString
              valueQuantity_unit
              valueQuantity_value
              component_0_code_coding_loinc_org
              component_0_code_text
              component_0_valueQuantity_unit
              component_0_valueQuantity_value
              component_1_code_coding_loinc_org
              component_1_code_text
              component_1_valueQuantity_unit
              component_1_valueQuantity_value
            }
          }
        }
      }
    }
  }
}


````
![image](https://user-images.githubusercontent.com/47808/194961779-8603208c-9d3c-46d1-a7b4-103e71ad75c4.png)

```commandline
{
  DocumentReference(id: "6c37767e-6b9a-5376-bf93-b814d6a24fc1") {
    id
    object_id
    content_attachment_md5
    content_attachment_size
    content_attachment_url
    Tasks {
      id
      Specimen {
        id
        Patients {
          id
        }
      }
    }
	}
}
```

![image](https://user-images.githubusercontent.com/47808/194962256-a2ef9522-3d0b-46d6-a402-87f2337716aa.png)

### Test download

```commandline
$ python3 etl/file --gen3_credentials_file  credentials-aced-training-local.json  drs-download --did FOOBAR:17a1bf1b-d71b-40c3-8382-967628546eec  --file_name /tmp/ttt
2022-10-10 15:42:48,120 cli INFO : https://aced-training.compbio.ohsu.edu
2022-10-10 15:42:48,487 download DEBUG : START
2022-10-10 15:42:48,487 download DEBUG : ('process', 'https://minio-default.compbio.ohsu.edu/aced-default/FOOBAR%3A17a1bf1b-d71b-40c3-8382-967628546eec/output/dna/Adam631_Turner526_6f60d183-2b8d-8c3c-77d0-2b684653651e_dna.csv?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=test%2F20221010%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20221010T224248Z&X-Amz-Expires=3600&X-Amz-SignedHeaders=host&client_id=&user_id=1&username=test&X-Amz-Signature=f35fd6d6bc079845d812720c972804511df9f2aad9c739c6af629b64c9881240')
2022-10-10 15:42:48,548 download DEBUG : ('get', 'https://minio-default.compbio.ohsu.edu/aced-default/FOOBAR%3A17a1bf1b-d71b-40c3-8382-967628546eec/output/dna/Adam631_Turner526_6f60d183-2b8d-8c3c-77d0-2b684653651e_dna.csv?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=test%2F20221010%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20221010T224248Z&X-Amz-Expires=3600&X-Amz-SignedHeaders=host&client_id=&user_id=1&username=test&X-Amz-Signature=f35fd6d6bc079845d812720c972804511df9f2aad9c739c6af629b64c9881240', <ClientResponse(https://minio-default.compbio.ohsu.edu/aced-default/FOOBAR:17a1bf1b-d71b-40c3-8382-967628546eec/output/dna/Adam631_Turner526_6f60d183-2b8d-8c3c-77d0-2b684653651e_dna.csv?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=test/20221010/us-east-1/s3/aws4_request&X-Amz-Date=20221010T224248Z&X-Amz-Expires=3600&X-Amz-SignedHeaders=host&client_id=&user_id=1&username=test&X-Amz-Signature=f35fd6d6bc079845d812720c972804511df9f2aad9c739c6af629b64c9881240) [206 Partial Content]>
<CIMultiDictProxy('Server': 'nginx/1.19.6', 'Date': 'Mon, 10 Oct 2022 22:42:48 GMT', 'Content-Type': 'binary/octet-stream', 'Content-Length': '23485', 'Connection': 'keep-alive', 'Accept-Ranges': 'bytes', 'Content-Range': 'bytes 0-23484/23485', 'Content-Security-Policy': 'block-all-mixed-content', 'Etag': '"499555740bfeed3cf1b28bb6525f0fa7"', 'Last-Modified': 'Mon, 10 Oct 2022 20:04:55 GMT', 'Strict-Transport-Security': 'max-age=31536000; includeSubDomains', 'Vary': 'Origin', 'Vary': 'Accept-Encoding', 'X-Amz-Request-Id': '171CD676F036578C', 'X-Content-Type-Options': 'nosniff', 'X-Xss-Protection': '1; mode=block', 'x-amz-meta-datanode_object_id': 'FOOBAR:17a1bf1b-d71b-40c3-8382-967628546eec', 'x-amz-meta-datanode_submitter_id': '6c37767e-6b9a-5376-bf93-b814d6a24fc1', 'x-amz-meta-datanode_type': 'DocumentReference', 'x-amz-meta-md5': '499555740bfeed3cf1b28bb6525f0fa7')>
)
2022-10-10 15:42:48,550 download DEBUG : ('download', 4341499264, '/Users/walsbr/aced/compose-services/Adam631_Turner526_6f60d183-2b8d-8c3c-77d0-2b684653651e_dna.csv2q8u7a6g/Adam631_Turner526_6f60d183-2b8d-8c3c-77d0-2b684653651e_dna.csv.part0')
2022-10-10 15:42:48,560 download DEBUG : ('md5', 4341499264, 'Adam631_Turner526_6f60d183-2b8d-8c3c-77d0-2b684653651e_dna.csv', '499555740bfeed3cf1b28bb6525f0fa7', b'SZVVdAv+7Tzxsou2Ul8Ppw==')
2022-10-10 15:42:48,566 download INFO : 0.07946720800000007 seconds [True]

```

# Microservices Reference

- Sheepdog: Handles the submitting and downloading of metadata to and from the GraphQL database.
- Peregrine: Sends GraphQL queries to the PostgreSQL backend and returns results in JSON format.
- Fence: Authenticates (AuthN) and authorizes (AuthZ) users. Generates tokens in `credentials.json`.
- Indexd: Creates permanent ID's (GUID) for every newly submitted data object.
- Windmill: Frontend for the exploration, submission, and downloading of data.