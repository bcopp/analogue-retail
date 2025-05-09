VERSION:=0.0.4

auth:
	gcloud auth configure-docker \
    us-central1-docker.pkg.dev

build:
	docker build -t us-central1-docker.pkg.dev/boost-446418/retail/backend:${VERSION} .

push: build
	docker push us-central1-docker.pkg.dev/boost-446418/retail/backend:${VERSION}



