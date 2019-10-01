all: build-image

build-image:
	docker build \
		--build-arg http_proxy=$$http_proxy \
		--build-arg https_proxy=$$https_proxy \
		--file Dockerfile \
		--tag eduardrosert/dwd-open-data-downloader:latest \
		.