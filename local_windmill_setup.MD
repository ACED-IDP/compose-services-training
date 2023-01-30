These are the steps for setting up a local Windmill local Windmill/Portal-Service Instance 

1. clone feature/local-data-portal branch and follow the steps to setup in 
https://github.com/ACED-IDP/compose-services-training/blob/feature/staging/docs/New_Setup.md


OR if you already have a working staging implementation:


```sh
dc down rm -f
```

change line 230 in docker compose yaml:
https://github.com/ACED-IDP/compose-services-training/blob/feature/local-data-portal/docker-compose.yml#L230


2. Clone data-portal into your compose-services root directory located here:
https://github.com/uc-cdis/data-portal/

3. cd into data portal and build the image locally with:
```sh
docker build -t windmill .
```

4. cd into the root of compose-services and dc up

5. If portal-services is running and healthy proceed otherwise dc down dc rm -f dc up -d

6. Run this command in data-portal directory :
```sh
npm i
```

7. Put your gitops.json file in data/config and title it config.json. This is the file that you will edit to make changes in your local windmill build

8. The below command is what you run when you want to see changes in a gitops file. The hot mapping only works for changes directly to the source code, 
but the command should only take 30 seconds at most and will automatically update the page when it has been initiated. 

```sh
HOSTNAME=aced-training.compbio.ohsu.edu APP=config NODE_ENV=dev bash ./runWebpack.sh
change hostname to whatever your hostname is that you were using before. 
```

This is the new root url of the website. You know you have suceeded in the previous steps when this works:
https://aced-training.compbio.ohsu.edu/dev.html/

Visit this if your webpage isn't loading https://localhost:9443/bundle.js you will probably have to visit it the first time you load the dev server.

9. You might need this line if you get an error about certs or versions when running the runWebpack.sh command:
```sh
export NODE_OPTIONS=--openssl-legacy-provider
```

10. To get the query page to load make this one line change in data-portal/src/localconf.js:L108 and reload webpack with the above command:

```txt
const graphqlSchemaUrl = `${hostname}${(basename && basename !== '/' && basename !== '/dev.html') ? basename : ''}/data/schema.json`;s
```



