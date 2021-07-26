iWebLense is a client server application where one can send a 

Make sure you install Python 3, docker and Kubernetes on your VM before performing steps below

1. Create docker image from dockerfile
$ docker build -t iweblense . 

-t is for tag or naming the image

2. List docker images and check for the last build image
$ docker images 

3. Run a docker container using docker image name
$ docker container run -dp 3000:2020 <image name>
$ docker container run -dp 3000:2020 iweblense 

-d is for detached mode so that it runs in the background
-p is to expose port 
Here 3000 is host port
2020 is container port

4. Call server using client python file
$ python3 iWebLens_client.py ./images http://localhost:3000/api/object_detection 4

iWebLens_client.py is the client file
./images is the folder from where images are used for detection
http://localhost:3000/api/object_detection is calling the docker container 
4 is the number of threads used in the python execution

5. Stop running container
$ docker container stop <container id>


—----

In order to run above program in a Kubernetes cluster-

1. Create yaml file for service and deployment
Mention the container port in the service config and Ports (node port, target port, port(default), port type) in the deployment config

2. Create the service and deployment
$ kubectl apply -f kuberdeploy.yaml

3. Check status of the deployments, services, nodes, pods
$ kubectl get deployments
$ kubectl get svc or $ kubectl get services
$ kubectl get pods
$ kubectl get nodes
$ kubectl get cs

Make sure-
Status of pods is Running
Status of nodes is Ready
Status of scheduler is Healthy
If pod is not running visit step 4. If scheduler is not running, go to end of file and come back to this step later

4. If status of pods is not running
At this stage it is possible that the pods are not running

To troubleshoot-
$ kubectl describe <deployment name>
$ kubectl describe pod <pod name> 

Here you will observe that pod wasn’t running because pod couldn’t fetch image
Error: ErrImagePull
Error: ImagePullBackOff

5. Rename your docker image
docker tag iweblense:latest <your docker hub userid>/iweblense:latest 
$docker tag iweblense:latest mehtapreeti09/iweblense:latest 

6. Upload docker image to docker hub
Login to your docker hub account (assuming you have one)
If you wish to use my image, skip to step 7
$docker login

Push docker image to your docker hub
$docker push <your docker hub account>/iweblense:latest

7. Change image name in kuberdeploy.yaml and reapply deployment service yaml
Rename the docker image same as the one you uploaded in the deployment config
Create the deployment and service as -
$ kubectl apply -f kuberdeploy.yaml

8. Call server using client python file
$ python3 iWebLens_client.py ./images http://localhost/api/object_detection 16

If type is NodePort in deployment yaml, it will be called in nodePort
$ python3 iWebLens_client.py ./images http://localhost:30200/api/object_detection 16

If type is LoadBalancer in deployment yam, it will be called on port(80 or default)
$ python3 iWebLens_client.py ./images http://localhost/api/object_detection 16

—----

-> If the nodes are not ready and if controller-manager/ scheduler  is unhealthy on command $ kubectl get cs

Run below commands remove the —port=0 line from the scheduler and controller scheduler config file and restart the cluster.

$ sed -i 's|- --port=0|#- --port=0|' /etc/kubernetes/manifests/kube-scheduler.yaml
$ sed -i 's|- --port=0|#- --port=0|' /etc/kubernetes/manifests/kube-controller-manager.yaml

$ systemctl restart kubelet
