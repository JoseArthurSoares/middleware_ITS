from middleware.mex import Amot
from middleware.classes.MessageStorage import MessageStorage
from middleware.classes.SubscriptionsManager import SubscriptionsManager


class BrokerEngine():
    def __init__(self):
        super().__init__()
        self.message_storage = MessageStorage()
        self.subscription_manager = SubscriptionsManager()

    def run(self, invArg):
        # invArg é o dicionário recebido contendo a operação e os dados

        # 1. Operação de Publicação
        if invArg['OP'] == 'Publish':
            for topic in invArg['TOPICS']:
                # Armazena a mensagem
                self.message_storage.add_message(topic, invArg['MSG'])

                # Distribui a mensagem para as filas dos assinantes
                message = self.message_storage.get_message_by_topic(topic).popleft()
                subscriptions = self.subscription_manager.get_subscriptions()
                for subscriber_id in subscriptions.keys():
                    if topic in subscriptions[subscriber_id].keys():
                        subscriptions[subscriber_id][topic].append(message)

        # 2. Operação de Assinatura
        elif invArg['OP'] == 'Subscribe':
            for topic in invArg['TOPICS']:
                self.subscription_manager.insert_subscription(topic, invArg['THING_ID'], invArg['MSG'])

        # 3. Operação de Checagem de Mensagens
        elif invArg['OP'] == 'CheckMsg':
            msg = {}
            thing_id = invArg['THING_ID']
            topics = invArg['TOPICS']

            # Verifica se há mensagens para este assinante nos tópicos solicitados
            if thing_id in self.subscription_manager.get_subscriptions().keys():
                for topic in topics:
                    subs = self.subscription_manager.get_subscriptions()[thing_id]
                    if topic in subs.keys() and subs[topic]:
                        msg[topic] = subs[topic].popleft()

            # Retorna a resposta para o cliente
            reply = {'OP': '', 'THING_ID': thing_id, 'TOPICS': '', 'MSG': msg}
            return reply

        else:
            print('Operação não implementada')