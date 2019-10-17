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