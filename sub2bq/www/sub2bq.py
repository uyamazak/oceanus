import time
import base64
import utils
import os
import json
from pprint import pformat,pprint
from bigquery import get_client
from datetime import datetime
# Falcon follows the REST architectural style, meaning (among
# other things) that you think in terms of resources and state
# transitions, which map to HTTP verbs.

DATA_SET = 'oceanus_test'
JSON_KEY_FILE = 'Oceanus-dev-784c5c9ec4b7.json'
SESSION_KEY = 'oceanus_sid'
TABLE_PREFIX = 'oceanus'
PROJECT_ID = os.environ['PROJECT_ID']
PUBSUB_TOPIC = os.environ['PUBSUB_TOPIC']
NUM_RETRIES = 3

class sub2bqResource(object):

    def create_oid(self):
        source_str = '0123456789abcdef'
        return "".join([random.choice(source_str) for x in range(16)])

    def conect_bigquery(self):
        json_key = JSON_KEY_FILE
        client = get_client(json_key_file=json_key, readonly=False)
        return client

    def create_table_name(self):
        return TABLE_PREFIX + datetime.now().strftime('_%Y%m%d')

    def prepare_table(self, client):
        exists = client.check_table(DATA_SET, self.table_name)
        created = False
        if not exists:
            schema = [
                {'name': 'dt',  'type': 'STRING', 'mode': 'REQUIRED'},
                {'name': 'oid', 'type': 'STRING', 'mode': 'REQUIRED'},
                {'name': 'sid', 'type': 'STRING', 'mode': 'REQUIRED'},
                {'name': 'rad', 'type': 'STRING', 'mode': 'REQUIRED'},
                {'name': 'tit', 'type': 'STRING', 'mode': 'nullable'},
                {'name': 'url', 'type': 'STRING', 'mode': 'nullable'},
                {'name': 'evt', 'type': 'STRING', 'mode': 'nullable'},
                {'name': 'ua',  'type': 'STRING', 'mode': 'nullable'},
                {'name': 'enc', 'type': 'STRING', 'mode': 'nullable'},
                {'name': 'scr', 'type': 'STRING', 'mode': 'nullable'},
                {'name': 'vie', 'type': 'STRING', 'mode': 'nullable'},
                {'name': 'iid', 'type': 'STRING', 'mode': 'REQUIRED'},
            ]
            created = client.create_table(DATA_SET, self.table_name, schema)
        return created


    def fqrn(self, resource_type, project, resource):
        """Returns a fully qualified resource name for Cloud Pub/Sub."""
        return "projects/{}/{}/{}".format(project, resource_type, resource)


    def create_subscription(self, client, project_name, sub_name):
        """Creates a new subscription to a given topic."""
        print("using pubsub topic: %s" % PUBSUB_TOPIC)
        name = self.get_full_subscription_name(project_name, sub_name)
        body = {'topic': PUBSUB_TOPIC}
        subscription = client.projects().subscriptions().create(
                name=name, body=body).execute(num_retries=NUM_RETRIES)
        print('Subscription {} was created.'.format(subscription['name']))


    def get_full_subscription_name(self, project, subscription):
        """Returns a fully qualified subscription name."""
        return self.fqrn('subscriptions', project, subscription)


    def pull_messages(self, client, project_name, sub_name):
        """Pulls messages from a given subscription."""
        BATCH_SIZE = 50
        tweets = []
        subscription = self.get_full_subscription_name(project_name, sub_name)
        body = {
                'returnImmediately': False,
                'maxMessages': BATCH_SIZE
        }
        try:
            resp = client.projects().subscriptions().pull(
                    subscription=subscription, body=body).execute(
                            num_retries=NUM_RETRIES)
        except Exception as e:
            print("Exception: %s" % e)
            time.sleep(0.5)
            return
        receivedMessages = resp.get('receivedMessages')
        if receivedMessages is not None:
            ack_ids = []
            for receivedMessage in receivedMessages:
                    message = receivedMessage.get('message')
                    if message:
                            tweets.append(
                                base64.urlsafe_b64decode(str(message.get('data'))))
                            ack_ids.append(receivedMessage.get('ackId'))
            ack_body = {'ackIds': ack_ids}
            client.projects().subscriptions().acknowledge(
                    subscription=subscription, body=ack_body).execute(
                            num_retries=NUM_RETRIES)
        pprint(type(tweets))
        return tweets


    def write_to_bq(self, pubsub, sub_name, bigquery):
        """Write the data to BigQuery in small chunks."""
        tweets = []
        CHUNK = 50  # The size of the BigQuery insertion batch.
        # If no data on the subscription, the time to sleep in seconds
        # before checking again.
        WAIT = 2
        tweet = None
        mtweet = None
        count = 0
        count_max = 50000
        while count < count_max:
            while len(tweets) < CHUNK:
                twmessages = self.pull_messages(pubsub, PROJECT_ID, sub_name)
                twmessages = twmessages
                print(twmessages)

                if twmessages:
                    for res in twmessages:
                        try:
                            tweet = json.loads(res.decode('utf-8'))
                        except Exception as bqe:
                            print(bqe)
                        # First do some massaging of the raw data
                        mtweet = utils.cleanup(tweet)
                        # We only want to write tweets to BigQuery; we'll skip
                        # 'delete' and 'limit' information.
                        #if 'delete' in mtweet:
                        #    continue
                        #if 'limit' in mtweet:
                        #    continue
                        tweets.append(mtweet)
                else:
                    # pause before checking again
                    print('sleeping...')
                    time.sleep(WAIT)

            response = None
            #response = utils.bq_data_insert(bigquery, PROJECT_ID, os.environ['BQ_DATASET'],
            #                         os.environ['BQ_TABLE'], tweets)
            tweets = []
            count += 1
            if count % 25 == 0:
                print ("processing count: %s of %s at %s: %s" %
                       (count, count_max, datetime.datetime.now(), response))


    def on_get(self, req, resp):
        topic_info = PUBSUB_TOPIC.split('/')
        topic_name = topic_info[-1]
        sub_name = "tweets-%s" % topic_name
        print("starting write to BigQuery....")
        credentials = utils.get_credentials()
        bigquery = utils.create_bigquery_client(credentials)
        pubsub = utils.create_pubsub_client(credentials)
        try:
            # TODO: check if subscription exists first
            subscription = self.create_subscription(pubsub, PROJECT_ID, sub_name)
        except Exception as e:
            print(e)
        self.write_to_bq(pubsub, sub_name, bigquery)
        print('exited write loop')

if __name__ == '__main__':
    resourse = sub2bqResource()
    topic_info = PUBSUB_TOPIC.split('/')
    topic_name = topic_info[-1]
    sub_name = "tweets-%s" % topic_name
    print("starting write to BigQuery....")
    credentials = utils.get_credentials()
    bigquery = utils.create_bigquery_client(credentials)
    pubsub = utils.create_pubsub_client(credentials)
    try:
        # TODO: check if subscription exists first
        subscription = resourse.create_subscription(pubsub, PROJECT_ID, sub_name)
    except Exception as e:
        print(e)
    resourse.write_to_bq(pubsub, sub_name, bigquery)
    print('exited write loop')






