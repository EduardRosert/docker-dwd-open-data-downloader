NAME   := eduardrosert/dwd-open-data-downloader
TAG    := $$(git log -1 --pretty=%H)
IMG    := ${NAME}:${TAG}
LATEST := ${NAME}:latest

all: build

build:
	@echo "Building $(IMG) ..."
	@docker build \
		--build-arg http_proxy=$$http_proxy \
		--build-arg https_proxy=$$https_proxy \
		--file Dockerfile \
		--tag ${IMG} \
		.
	@docker tag ${IMG} ${LATEST}

login:
	@docker login

login-user-pass:
	@docker login -u ${DOCKER_USER} -p ${DOCKER_PASS}

push: login
	@docker push ${NAME}

test-local:
	@-mkdir grib-data
	@export MODEL_NAME=icon-eu && export MODEL_FIELDS=t_2m pmsl clct tot_prec && export MAX_TIME_STEP=24 && export GRIB_DIRECTORY=./grib-data/
	@python ./opendata-downloader.py --model $$MODEL_NAME --single-level-fields $$MODEL_FIELDS --min-time-step 0 --max-time-step $$MAX_TIME_STEP -v --directory $$GRIB_DIRECTORY
