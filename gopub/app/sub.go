// Sample pubsub-quickstart creates a Google Cloud Pub/Sub topic.
package main

import (
	"fmt"
	"log"
	"os"
	"os/signal"
	//"net"
	//"reflect"
	"time"

	// Imports the Google Cloud Pub/Sub client package.
	"cloud.google.com/go/iam"
	"cloud.google.com/go/pubsub"
	"golang.org/x/net/context"
	"google.golang.org/api/iterator"
)

func main() {
	ctx := context.Background()
	// Sets your Google Cloud Platform project ID.

	projectID := os.Getenv("PROJECT_ID")
	fmt.Println("projectID", projectID)
	// Creates a client.
	p_client, err := pubsub.NewClient(ctx, projectID)
	if err != nil {
		log.Fatalf("Failed to create client: %v", err)
	}
	//log.Print(reflect.TypeOf(p_client))
	//log.Print(reflect.TypeOf(ctx))
	topic := createTopicIfNotExists(p_client)
	subscription_name := os.Getenv("GOPUB_SUBSCRIPTION_NAME")
	//defer deleteSub(p_client, subscription_name)
	sub := p_client.Subscription(subscription_name)
	sub_exists, _ := sub.Exists(ctx)
	log.Print(sub_exists)
	log.Print(sub)
	if err != nil {
		log.Print("sub.Exists Error")
		return
	}
	if sub_exists == false {
		sub, err = p_client.CreateSubscription(ctx, subscription_name, topic, time.Second*10, nil)
		if err != nil {
			log.Printf("Failed to create client: %v", err)
			return
		}
	}

	//log.Print(sub)
	subMsgs(p_client, subscription_name, topic)
}

func deleteSub(p_client *pubsub.Client, subscription_name string) {
	// capture ctrl+c and stop CPU profiler
	c := make(chan os.Signal, 1)
	signal.Notify(c, os.Interrupt)
	go func() {
		for sig := range c {
			log.Printf("captured %v, stopping profiler and exiting..", sig)
			delete(p_client, subscription_name)
			os.Exit(1)
		}
	}()
}

func list(client *pubsub.Client) ([]*pubsub.Subscription, error) {
	ctx := context.Background()
	// [START get_all_subscriptions]
	var subs []*pubsub.Subscription
	it := client.Subscriptions(ctx)
	for {
		s, err := it.Next()
		if err == iterator.Done {
			break
		}
		if err != nil {
			return nil, err
		}
		subs = append(subs, s)
	}
	// [END get_all_subscriptions]
	return subs, nil
}

func subMsgs(client *pubsub.Client, name string, topic *pubsub.Topic) error {
	fmt.Printf("subMsgs Start")
	ctx := context.Background()
	log.Printf("name: %v", name)
	sub := client.Subscription(name)
	sub.Receive(ctx, func(ctx context.Context, m *pubsub.Message) {
		// TODO: Handle message.
		// NOTE: May be called concurrently; synchronize access to shared memory.
		log.Printf("ID:%v Data: %v", m.ID, string(m.Data))
		m.Ack()
	})
	return nil

}
func create(client *pubsub.Client, name string, topic *pubsub.Topic) error {
	ctx := context.Background()
	// [START create_subscription]
	sub, err := client.CreateSubscription(ctx, name, topic, 20*time.Second, nil)
	if err != nil {
		return err
	}
	fmt.Printf("Created subscription: %v\n", sub)
	// [END create_subscription]
	return nil
}

func delete(client *pubsub.Client, name string) error {
	ctx := context.Background()
	// [START delete_subscription]
	sub := client.Subscription(name)
	if err := sub.Delete(ctx); err != nil {
		return err
	}
	fmt.Println("Subscription deleted.")
	// [END delete_subscription]
	return nil
}

func createTopicIfNotExists(c *pubsub.Client) *pubsub.Topic {
	ctx := context.Background()
	topicName := os.Getenv("GOPUB_TOPIC_NAME")
	fmt.Println("topicName", topicName)
	// Create a topic to subscribe to.
	t := c.Topic(topicName)
	ok, err := t.Exists(ctx)
	if err != nil {
		log.Fatal(err)
	}
	if ok {
		return t
	}

	t, err = c.CreateTopic(ctx, topicName)
	if err != nil {
		log.Fatalf("Failed to create the topic: %v", err)
	}
	return t
}

func getPolicy(c *pubsub.Client, subName string) *iam.Policy {
	ctx := context.Background()

	// [START pubsub_get_subscription_policy]
	policy, err := c.Subscription(subName).IAM().Policy(ctx)
	if err != nil {
		log.Fatal(err)
	}
	for _, role := range policy.Roles() {
		log.Printf("%q: %q", role, policy.Members(role))
	}
	// [END pubsub_get_subscription_policy]
	return policy
}

func addUsers(c *pubsub.Client, subName string) {
	ctx := context.Background()

	// [START pubsub_set_subscription_policy]
	sub := c.Subscription(subName)
	policy, err := sub.IAM().Policy(ctx)
	if err != nil {
		log.Fatalf("GetPolicy: %v", err)
	}
	// Other valid prefixes are "serviceAccount:", "user:"
	// See the documentation for more values.
	policy.Add(iam.AllUsers, iam.Viewer)
	policy.Add("group:cloud-logs@google.com", iam.Editor)
	if err := sub.IAM().SetPolicy(ctx, policy); err != nil {
		log.Fatalf("SetUser: %v", err)
	}
	// NOTE: It may be necessary to retry this operation if IAM policies are
	// being modified concurrently. SetPolicy will return an error if the policy
	// was modified since it was retrieved.
	// [END pubsub_set_subscription_policy]
}

func testPermissions(c *pubsub.Client, subName string) []string {
	ctx := context.Background()

	// [START pubsub_test_subscription_permissions]
	sub := c.Subscription(subName)
	perms, err := sub.IAM().TestPermissions(ctx, []string{
		"pubsub.subscriptions.consume",
		"pubsub.subscriptions.update",
	})
	if err != nil {
		log.Fatal(err)
	}
	for _, perm := range perms {
		log.Printf("Allowed: %v", perm)
	}
	// [END pubsub_test_subscription_permissions]
	return perms
}
