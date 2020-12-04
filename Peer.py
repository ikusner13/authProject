# Each peer is set up knowing the policy of the resource exhanges, along with knowing know holds each resource 

''' READ

### MESSAGE FORMAT ###

message format is {type: String, sender: String, reciever: String, request: List[] or String}

request is a List if type is 'request'. request can be a String if type is 'offer'

inside request is {request: List or String, issuer: String} if type is 'request'. {request: List or String} if type is 'offer'

request is a List if multipe requests/offers to/for a resource are being made


### PEER ###

Peer is set up so each peer will hold the policy of the exchange system (locks or unlocks of resources)

Peer will hold the credentials that it recieves as offers from other resources 

Peer will also be initialized knowing which peer holds what resource 

'''
class Peers:
  def __init__(self,name):
    self.name = name # name of Peer (client, rs, as_1, as_2)
    self.policy = {
      'c1': ['c2','c3'],
      'c2': True,
      'c3':['c4'],
      'c4':True
    }
    self.credentials_recieved = []
    self.holders = {
      "c1": 'rs',
      'c2': 'as_1',
      'c3': 'as_2',
      'c4': 'client'
    }


  # given unresolved messsages and list of resources that correspond to an unresolved message, find which sender to return to
  def findSender(self,messages,return_list):
      resources = []
      for m in messages:
        for r in m['resource']:
          resources.append(r['resource'])
        if set(resources) == set(return_list):
          return m['sender']


  # checks if any resources in the list are unlocked(able to be sent back) or locked(not able to be)
  def isResourceUnlocked(self,resources,credentials):
      valid = True
      for item in resources:
        for r in item:
          #print('m',m)
          #print('holder', self.holders[r], self.name)
          if(self.holders[r] == self.name):
            if(isinstance(self.policy[r],list)):
              if(set(self.policy[r]).intersection(set(credentials)) == set(self.policy[r])):
                #print('HAS VALID CREDENTIALS FOR',r)
                pass
              else:
                valid = False
                #print("DOES NOT HAVE VALID CREDENTIAL FOR", r)
      return valid
  
  def requestError(self,message):
      for resources in message['resource']:
          print('resources',resources)
          if(resources['resource'] not in self.policy):
            return True
      
      return False
          

  

  def resolver(self,message,Mrec):
    print('message',message)
    print('message resource',message['resource'])
    print('input message', message)

    if(message['type'] == 'request'):

      if(self.requestError(message)):
        return ['INVALID REQUEST ERROR']

      return_messages = []

      req_resources = [r['resource'] for r in message['resource']]
      if(len(req_resources) == 1 and isinstance(req_resources[0],list)):
        req_resources = req_resources[0]
        

      my_recieved = [request for request in Mrec if request['reciever'] == self.name and request['type'] == 'request']
      #print('request my_recieved', my_recieved)
      print('req res', req_resources)
      #print('credentilas', self.credentials_recieved)
      #print('\n')
      to_offer = []
      for requests in message['resource']:
        resource = requests['resource']

        held = [h for h in self.holders if self.holders[h] == self.name]
        print('held',held)

        print('resource', resource)
        have = self.credentials_recieved + held
        print('have',have)
        if not isinstance(resource,list):
          resource = [resource]
        # if reciever is the issuer of the resource 
        if(requests['issuer'] == self.name or set(have).intersection(req_resources) == set(req_resources)):
         # print('issuer is self')
          #print('before loop',resource)
          for r in resource:
            needed_resources = self.policy[r]
            print('needed_resources', needed_resources)
            print('req_resour',req_resources)
            print('inter',set(have).intersection(req_resources))
            if(needed_resources == True and set(have).intersection(req_resources) == set(req_resources)):
              print('resource is unlocked')
              if r in req_resources:
               # print(r,'in',req_resources)
                #req_resources.pop(req_resources.index(r))
               # print('after pop',req_resources)
              #if(set(self.credentials_recieved) == set(req_resources) or len(req_resources) == 0):
               # print('offer',r)
                to_offer.append(r)
            elif(needed_resources != True):
              #print('resource not unlocked')
              test = []
              print('needed resources',needed_resources)
              for n in needed_resources:
                issuer = self.holders[n]
                test.append({'resource': n, 'issuer': issuer})
              newList = sorted(test, key=lambda k: k['issuer'])
              #print('newList',newList)
              temp1 = []
              temp2 = []
              issuer = newList[0]['issuer']
              for i in newList:
                #issuer = i['issuer']
                #print('issuer',issuer)
                if i['issuer'] == issuer:
                  temp2.append(i)
                else:
                  temp1.append(temp2)
                  temp2 = [i]
                issuer = i['issuer']
              temp1.append(temp2)
              #print('issuers temp', temp1)
              arr_rec = []
              for t in temp1:
                to_send = []
                send_to = t[0]['issuer']
                for j in t:
                  to_send.append(j['resource'])
                #print('SEND', to_send, send_to)
                if len(to_send) == 1:
                  arr_rec.append({'resource': to_send[0], 'issuer': send_to})
                else:
                  arr_rec.append({'resource': to_send, 'issuer':send_to })
              return_messages.append({'type': 'request', 'sender': self.name, 'reciever': message['sender'], 'resource': arr_rec})

        else:
            #print('self does not have resource',requests)
            #print('resource',resource)
            for r in resource:
              return_messages.append({'type': 'request', 'sender': self.name, 'reciever': self.holders[r], 'resource': [{'resource': r, 'issuer': self.holders[r]}]})

      if len(to_offer) > 0:
        #print('to_offer',to_offer)
        if len(to_offer) == 1:
          return_messages.append({'type': 'offer', 'sender': self.name, 'reciever': message['sender'], 'resource': to_offer[0]})
        else:
          return_messages.append({'type': 'offer', 'sender': self.name, 'reciever': message['sender'], 'resource': to_offer})
      print('return messges', return_messages)
      #print('\n')
      return return_messages


    if(message['type'] == 'offer'):
      print('\n')
      for r in Mrec[0]['resource']:
        if(r['resource'] == message['resource']):
          return ["DONE"]

      print('message',message)
      if isinstance(message['resource'],list):
        for creds in message['resource']:
          self.credentials_recieved.append(creds)
      else:
        self.credentials_recieved.append(message['resource'])

      my_recieved = [request for request in Mrec if request['reciever'] == self.name and request['type'] == 'request']
      offers_sent = [request for request in Mrec if request['sender'] == self.name and request['type'] == 'offer']
      print('my recieved: ', *my_recieved,sep='\n')
      print('offers sent: ', *offers_sent, sep='\n')
      rec = []
      unsent = []
      my_reciever_iterate = my_recieved
      for m in my_recieved:
        print('MMMM',m)
        sender = m['sender']
        rrecieved = []
        for r in m['resource']:
          rrecieved.append(r['resource'])
        for o in offers_sent:
          offers = set()
          if not isinstance(o['resource'],list):
            offers.add(o['resource'])
          else:
            offers = set(o['resource'])
          print('offers',offers)
          print('rreciev', set(rrecieved))
          print('sender',sender)
          if(offers == set(rrecieved) and o['reciever'] == sender):
            print('my_recieved',my_recieved)
            print('pop', my_recieved.index(m))
            unsent.append(m)
            #my_recieved.pop(my_recieved.index(m))
            print('sent resource', o['resource'])
        
      for messages in unsent:
        my_recieved.pop(my_recieved.index(messages))
      print('TEST', *my_reciever_iterate,sep='\n')
      print('MY REC', *my_recieved,sep='\n')
      print('UNSENT',*unsent, sep='\n')
         



      for r in my_recieved:
        temp = []
        for res in r['resource']:
          temp.append(res['resource'])
        rec.append(temp)

      return_list = []

      print('creds ', self.credentials_recieved)
      held = [h for h in self.holders if self.holders[h] == self.name]
      print('held', held)
      print('credentilas_received',self.credentials_recieved)
      my_creds = held + self.credentials_recieved
      print('my_creds',my_creds)

      print('REC',rec)

      valid = self.isResourceUnlocked(rec,my_creds)

      if(valid):
        for r in rec:
          print('r',r)
          if(set(my_creds).intersection(set(r)) == set(r)):
              return_list.extend(list(set(my_creds).intersection(set(r))))
              print('intersection to send ',set(my_creds).intersection(set(r)))
        print('return ', return_list)
        #print('\n')
        sender = self.findSender(my_recieved,return_list)
        
        print('sender',sender)
        if len(return_list) == 1:
          return [{'type':'offer', 'sender': self.name, 'reciever': sender, 'resource': return_list[0]}]
        elif len(return_list) > 1:
          return [{'type':'offer', 'sender': self.name, 'reciever': sender, 'resource': return_list}]
        print('\n')

        
if __name__ == "__main__":
    client = Peers(name='client')
    rs = Peers(name='rs')
    as_1 = Peers(name='as_1')
    as_2 = Peers(name='as_2')

    message = {'type': 'request', 'sender': 'client', 'reciever': 'rs', 'resource': [{'resource': 'c1', 'issuer': 'rs'}]}
    queue = [message]

    Mrec = []

    # send message to appropriate reciever
    def processMessage(m):
      Mrec.append(m)
      sent = {}
      if m['reciever'] == 'client':
        sent = client.resolver(m,Mrec)
      elif m['reciever'] == 'rs':
        sent = rs.resolver(m,Mrec)
      elif m['reciever'] == 'as_1':
        sent = as_1.resolver(m,Mrec)
      elif m['reciever'] == 'as_2':
        sent = as_2.resolver(m,Mrec)
      if sent != None:
        for s in sent:
          queue.append(s)

    while(queue != [] and len(Mrec) < 20):
      m = queue.pop(0)
      if isinstance(m,dict):
        processMessage(m)
      else:
        Mrec.append(m)
        print(m)
    print(*Mrec, sep='\n')
