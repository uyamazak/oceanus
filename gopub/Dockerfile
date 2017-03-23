FROM golang:1.8.0-alpine

#RUN apt-get update
RUN apk add --update git

RUN go get -u cloud.google.com/go/pubsub

COPY key.json key.json
ENV GOOGLE_APPLICATION_CREDENTIALS key.json

ENV PROJECT_ID "oceanus-dev"
ENV GOPUB_TOPIC_NAME "oceanus-arms"
ENV GOPUB_SUBSCRIPTION_NAME "ml30gen9"
ENV GOPUB_BUFFER_SIZE 4096
ENV LISTEN_HOST ""
ENV LISTEN_PORT 8765
EXPOSE ${LISTEN_PORT}


COPY app /go/app
WORKDIR /go/

RUN go build app/main.go

CMD ["./main"]
