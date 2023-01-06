# elasticsearch mac

The released build for elasticsearch `quay.io/cdis/elasticsearch-oss:6.8.12` tends to run poorly on mac silicon.

Symptoms include:
* cpu utilization at 100%
* timeouts
* not starting

This custom build targets mac silicon.  see https://stackoverflow.com/a/70713284


## getting started 

Make this change to docker compose.

```commandline
   esproxy-service:
-    image: quay.io/cdis/elasticsearch-oss:6.8.12
+    # image: quay.io/cdis/elasticsearch-oss:6.8.12
+    build: elasticsearch-mac
     container_name: esproxy-service
     environment:
       - cluster.name=elasticsearch-cluster

```

Stop and rm the exiting elastic search.

```
dc stop esproxy-service ; dc rm -f esproxy-service ; 
```

Build and launch the new image 
```commandline
dc build esproxy-service ; dc up -d esproxy-service
```
