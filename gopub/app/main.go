package main

import (
	"bytes"
	"errors"
	"fmt"
	"log"
	"net"
	"os"
	"reflect"
	"runtime"
	"strconv"
	"strings"

	"cloud.google.com/go/pubsub"
	"golang.org/x/net/context"
)

type ReceivedData struct {
	Key   string
	Value []byte
}

func NewReceivedData(buf []byte) (*ReceivedData, error) {
	fields := bytes.Fields(buf)
	d := &ReceivedData{}
	if len(fields) == 0 {
		return d, errors.New("Received bytes have not fields")
	}
	d.Key = string(fields[0])
	d.Value = bytes.Trim(buf[len(d.Key):], " \t\n")
	return d, nil
}

type PubService struct {
	Ctx             context.Context
	Client          *pubsub.Client
	Topics          map[string]*pubsub.Topic
	TopicNamePrefix string
}

func NewPubService(tm *TopicsMeta, projectID string) (*PubService, error) {
	ps := &PubService{}
	ps.Ctx = context.Background()
	client, err := pubsub.NewClient(ps.Ctx, projectID)
	if err != nil {
		return ps, errors.New(fmt.Sprintf("Failed to create client: %v", err))
	}
	ps.Client = client
	ps.Topics, err = ps.getTopics(tm)
	ps.TopicNamePrefix = tm.NamePrefix
	if err != nil {
		return ps, err
	}
	return ps, nil
}
func (s *PubService) getTopics(tm *TopicsMeta) (map[string]*pubsub.Topic, error) {
	topics := make(map[string]*pubsub.Topic)
	if len(tm.Names) == 0 {
		return topics, errors.New("Names is empty")
	}
	for _, name := range tm.Names {
		topics[name] = s.createTopicIfNotExists(name)
		log.Printf("topic %v loaded\n", name)
	}
	return topics, nil
}
func (s *PubService) createTopicIfNotExists(topicName string) *pubsub.Topic {
	t := s.Client.Topic(topicName)
	ok, err := t.Exists(s.Ctx)
	if err != nil {
		log.Printf("Topic not exsits %v", err)
	}
	if ok {
		return t
	}
	t, err = s.Client.CreateTopic(s.Ctx, topicName)
	if err != nil {
		log.Printf("Failed to create the topic: %v", err)
	}
	return t
}
func (s *PubService) publishHandler(buf []byte) error {
	buf_copy := make([]byte, len(buf))
	copy(buf_copy, buf)
	data, err := NewReceivedData(buf_copy)
	if err != nil {
		log.Printf("Error in Received Data: %v", err)
		return err
	}
	topicName := s.TopicNamePrefix + data.Key
	topic, ok := s.Topics[topicName]
	if ok == false {
		msg := fmt.Sprintf("Topic %v does not exists in config file", topicName)
		log.Print(msg)
		return errors.New(msg)
	}
	result := topic.Publish(s.Ctx, &pubsub.Message{Data: data.Value})
	_, err = result.Get(s.Ctx)
	if err != nil {
		return err
	}
	return nil
}

type TopicsMeta struct {
	Names         []string
	OriginalNames []string
	NamePrefix    string
	Count         int
	ConfigString  string
}

func (tm *TopicsMeta) addNamePrefix(name string) string {
	return tm.NamePrefix + name
}
func NewTopicsMeta(configTopics string, prefix string) (*TopicsMeta, error) {
	tm := &TopicsMeta{
		ConfigString: configTopics,
		NamePrefix:   prefix,
	}
	configNames := strings.Split(configTopics, ",")
	if len(configNames) == 0 {
		return &TopicsMeta{}, errors.New("no configName found")
	}
	names := []string{}
	orgNames := []string{}
	for _, name := range configNames {
		names = append(names, tm.addNamePrefix(name))
		orgNames = append(orgNames, name)
	}
	tm.Names = names
	tm.OriginalNames = orgNames
	tm.Count = len(names)
	return tm, nil
}
func connectionHandler(conn net.Conn, buf_func func([]byte) error, bufferSize uint64) {
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
			err = buf_func(buf[:n])
			if err != nil {
				log.Printf("buf_func err: %v", err)
				log.Printf("err type:%v", reflect.TypeOf(err).String())
				if reflect.TypeOf(err).String() == "*grpc.rpcError" {
					log.Fatal("*grpc.rpcError")
				}
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
	topicsMeta, err := NewTopicsMeta(os.Getenv("GOPUB_TOPICS"), os.Getenv("GOPUB_TOPIC_NAME_PREFIX"))
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
	service, err := NewPubService(topicsMeta, projectID)
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
		connectionHandler(conn, service.publishHandler, bufferSize)
	}
}
