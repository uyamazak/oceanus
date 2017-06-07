FROM golang:1.8.0-alpine

RUN apk add --update git
RUN go get -u cloud.google.com/go/pubsub


ENV LISTEN_HOST ""
ENV LISTEN_PORT 8765
EXPOSE ${LISTEN_PORT}

COPY app /go/app
COPY keys keys
WORKDIR /go/

RUN go build app/main.go

CMD ["./main"]
