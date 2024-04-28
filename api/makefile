target: build stop run logs

build:
	docker build . --file Dockerfile -t bscholer/pepper-pod-pal

stop:
	- docker stop pepper-pod-pal
	- docker rm pepper-pod-pal

run:
	docker run -it -d --env-file=.env -p 5789:5789 --name pepper-pod-pal bscholer/pepper-pod-pal

exec:
	docker exec -it pepper-pod-pal /bin/bash

logs:
	docker logs --follow pepper-pod-pal

publish:
	docker push bscholer/pepper-pod-pal
