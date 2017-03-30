package pubservice

import (
	"bytes"
	"errors"
	"fmt"
	"log"
	"reflect"
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
	if len(fields) < 2 {
		return d, errors.New("Received bytes is empty")
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
	ps.Topics, err = ps.GetTopics(tm)
	ps.TopicNamePrefix = tm.NamePrefix
	if err != nil {
		return ps, err
	}
	return ps, nil
}
func (s *PubService) GetTopics(tm *TopicsMeta) (map[string]*pubsub.Topic, error) {
	topics := make(map[string]*pubsub.Topic)
	if len(tm.Names) == 0 {
		return topics, errors.New("Names is empty")
	}
	for _, name := range tm.Names {
		topics[name] = s.CreateTopicIfNotExists(name)
		log.Printf("topic %v loaded\n", name)
	}
	return topics, nil
}
func (s *PubService) CreateTopicIfNotExists(topicName string) *pubsub.Topic {
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
func (s *PubService) PublishHandler(buf []byte) error {
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
		msg := fmt.Sprintf("Topic %v does not exists in configs", topicName)
		log.Print(msg)
		return errors.New(msg)
	}
	result := topic.Publish(s.Ctx, &pubsub.Message{Data: data.Value})
	_, err = result.Get(s.Ctx)
	if err != nil {
		if reflect.TypeOf(err).String() == "*grpc.rpcError" {
			log.Fatal("*grpc.rpcError! exit")
		}
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
func NewTopicsMeta(configString string, prefix string) (*TopicsMeta, error) {
	tm := &TopicsMeta{
		ConfigString: configString,
		NamePrefix:   prefix,
	}
	configNames := strings.Split(configString, ",")
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
