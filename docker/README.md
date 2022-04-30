## Docker Build

docker build -t $BASE_IMAGE --platform x86_64 --build-arg BASE_IMAGE=$BASE_IMAGE --build-arg TAG=$TAG --no-cache -f docker/Dockerfile .


## CodeBuild Test

### Install

~~~bash
$ docker pull public.ecr.aws/codebuild/amazonlinux2-x86_64-standard:3.0
$ docker pull public.ecr.aws/codebuild/local-builds:latest
~~~

~~~bash
$ wget https://raw.githubusercontent.com/aws/aws-codebuild-docker-images/master/local_builds/codebuild_build.sh
$ chmod +x codebuild_build.sh
~~~


### Exec

~~~bash
./codebuild_build.sh -c　-i $CODEBUILD_RUNNER -a /tmp/artifacts -e .env
~~~ 