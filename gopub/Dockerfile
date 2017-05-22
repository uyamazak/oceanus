FROM golang:1.8.0-alpine

#RUN apt-get update
RUN apk add --update git

RUN go get -u cloud.google.com/go/pubsub

COPY key.json key.json
ENV GOOGLE_APPLICATION_CREDENTIALS key.json

ENV PROJECT_ID "oceanus-dev"
ENV GOPUB_TOPIC_NAME_PREFIX "oceanus-gopub-"
ENV GOPUB_TOPICS "bizocean,movieform,namecard,skj,docreq,bizpow,moneynext"
ENV GOPUB_SUBSCRIPTION_NAME "oceanus-subscription"
ENV GOPUB_COMBINED_TOPIC_NAME "oceanus-combined"
ENV GOPUB_BUFFER_SIZE 4096
ENV GOPUB_PUBLISH_MODE "COMBINED"
ENV LISTEN_HOST ""
ENV LISTEN_PORT 8765
EXPOSE ${LISTEN_PORT}

COPY app /go/app
WORKDIR /go/

RUN go build app/main.go

CMD ["./main"]
