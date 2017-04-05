package main

import (
	"log"
	"net"
	"os"
	"reflect"
	"runtime"
	"strconv"

	"./pubservice"
)

func connectionHandler(conn net.Conn, bufferSize uint64, bufferReceiver func([]byte) error) {
	defer conn.Close()
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
		conn.Write(buf[:n])
		go func() {
			err = bufferReceiver(buf[:n])
			if err != nil {
				log.Printf("bufferReceiver err: %v \n type:%v", err, reflect.TypeOf(err).String())
			}
		}()
	}
}

func main() {
	projectID := os.Getenv("PROJECT_ID")
	listenHost := os.Getenv("LISTEN_HOST")
	listenPort := os.Getenv("LISTEN_PORT")
	bufferSize, err := strconv.ParseUint(os.Getenv("GOPUB_BUFFER_SIZE"), 10, 64)
	if err != nil {
		log.Printf("bufferSize is invalid %v", err)
		return
	}
	topicsMeta, err := pubservice.NewTopicsMeta(os.Getenv("GOPUB_TOPICS"), os.Getenv("GOPUB_TOPIC_NAME_PREFIX"))
	if err != nil {
		log.Printf("Failed to create topicsMeta %v", err)
		return
	}
	log.Printf("GOPUB Server start\n"+
		"GOMAXPROCS:              %v\n"+
		"projectID:               %v\n"+
		"topicsMeta.Names:        %v\n"+
		"topicsMeta.ConfigString: %v\n"+
		"topicsMeta.Count:        %v\n"+
		"listenHost:              %v\n"+
		"listenPort:              %v\n"+
		"bufferSize:              %v",
		runtime.GOMAXPROCS(0),
		projectID,
		topicsMeta.Names,
		topicsMeta.ConfigString,
		topicsMeta.Count,
		listenHost,
		listenPort,
		bufferSize)

	listen, err := net.Listen("tcp", listenHost+":"+listenPort)
	defer listen.Close()
	if err != nil {
		log.Printf("Failed to listen tcp %v", err)
		return
	}
	service, err := pubservice.NewPubService(topicsMeta, projectID)
	if err != nil {
		log.Printf("NewPubService error: %v", err)
		return
	}
	log.Println("PubService created")

	for {
		conn, err := listen.Accept()
		if err != nil {
			log.Printf("Failed to accept %v", err)
			return
		}
		connectionHandler(conn, bufferSize, service.PublishHandler)
	}
}
