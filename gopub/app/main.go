package main

import (
	"log"
	"net"
	"os"
	"runtime"
	"strconv"

	"cloud.google.com/go/pubsub"
	"golang.org/x/net/context"
)

func main() {
	ctx := context.Background()
	projectID := os.Getenv("PROJECT_ID")
	listenHost := os.Getenv("LISTEN_HOST")
	listenPort := os.Getenv("LISTEN_PORT")
	log.Printf("GOPUB Server start\n"+
		"GOMAXPROCS: %v\n"+
		"projectID:  %v\n"+
		"listenHost: %v\n"+
		"listenPort: %v\n"+
		"topicName:  %v\n"+
		"bufferSize: %v",
		runtime.GOMAXPROCS(0),
		projectID,
		listenHost,
		listenPort,
		os.Getenv("GOPUB_TOPIC_NAME"),
		os.Getenv("GOPUB_BUFFER_SIZE"))

	// Creates a client.
	pub_client, err := pubsub.NewClient(ctx, projectID)
	if err != nil {
		log.Printf("Failed to create client: %v", err)
		return
	}
	topic := createTopicIfNotExists(ctx, pub_client)
	var listen net.Listener

	listen, err = net.Listen("tcp", listenHost+":"+listenPort)
	if err != nil {
		log.Printf("Failed to listen tcp %v", err)
		return
	}
	defer listen.Close()

	for {
		conn, e := listen.Accept()
		if e != nil {
			log.Printf("Failed to accept %v", e)
			return
		}
		connection_handler(conn, ctx, topic)
	}
}

func connection_handler(conn net.Conn, ctx context.Context, topic *pubsub.Topic) {
	defer conn.Close()
	bufferSize, _ := strconv.ParseUint(os.Getenv("GOPUB_BUFFER_SIZE"), 10, 64)
	buf := make([]byte, bufferSize)
	for {
		n, err := conn.Read(buf)
		if err != nil {
			if err.Error() == "EOF" {
				return
			}
			log.Printf("conn.Read error: %v", err)
			return
		}
		go publish_handler(ctx, topic, buf[:n])
		conn.Write(buf[:n])
	}
}

func publish_handler(ctx context.Context, topic *pubsub.Topic, buf []byte) {
	buf_copy := make([]byte, len(buf))
	copy(buf_copy, buf)
	result := topic.Publish(ctx, &pubsub.Message{Data: buf_copy})
	_, err := result.Get(ctx)
	if err != nil {
		log.Printf("Publish error: %v", err)
		return
	}
}

func createTopicIfNotExists(ctx context.Context, c *pubsub.Client) *pubsub.Topic {
	// Create a topic to subscribe to.
	topicName := os.Getenv("GOPUB_TOPIC_NAME")
	t := c.Topic(topicName)
	ok, err := t.Exists(ctx)
	if err != nil {
		log.Printf("Topic not exsits %v", err)
	}
	if ok {
		return t
	}

	t, err = c.CreateTopic(ctx, topicName)
	if err != nil {
		log.Printf("Failed to create the topic: %v", err)
	}
	return t
}
