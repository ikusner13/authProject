L = {
  "c1": "discount 20%",
  "c2": "Credit score 780",
  "c3": "Alex.kent.edu",
  "c4": "ID81023456"
}

class Peers:
  def __init__(self,name):
    self.name = name
    self.policy = {
      "c1": ['c2','c3'],
      "c2":True,
      "c3":["c4"],
      "c4":True
    }
    self.credentials_recieved = []
    self.holders = {
      "c1": 'rs',
      'c2': 'as_1',
      'c3': 'as_2',
      'c4': 'client'
    }

  def findSender(self, messages,return_list):
      resources = []
      for m in messages:
        for r in m['resource']:
          resources.append(r['resource'])
        if set(resources) == set(return_list):
          return m['sender']
  
  def resolver(self,message,Mrec,Msent):
    if(message['type'] == 'request'):
      return_messages = []

      req_resources = [r['resource'] for r in message['resource'] ]

      my_recieved = [request for request in Mrec if request['reciever'] == self.name and request['type'] == 'request']
      print('request my_recieved', my_recieved)
      print('req res', req_resources)
      print('credentilas', self.credentials_recieved)
      for requests in message['resource']:
        resource = requests['resource'] 
        # if reciever is the issuer of the resource 
        if(requests['issuer'] == self.name):
          unlocked = self.policy[resource]
          if(unlocked == True):
            if resource in req_resources:
              req_resources.pop(req_resources.index(resource))
            if(set(self.credentials_recieved) == set(req_resources) or len(req_resources) == 0):
              return_messages.append({'type': 'offer', 'sender': self.name, 'reciever': message['sender'], 'resource': resource})
          else:
            arr = []
            for r in unlocked:
              arr.append({'resource': r, 'issuer': self.holders[r]})
            return_messages.append({'type': 'request', 'sender': self.name, 'reciever': message['sender'], 'resource': arr })
        else:
            return_messages.append({'type': 'request', 'sender': self.name, 'reciever': self.holders[resource], 'resource': [{'resource': resource, 'issuer': self.holders[resource]}]})
      return return_messages


    if(message['type'] == 'offer'):
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
      print('Msent: ', *Msent, sep='\n')
      rec = []
      test = []

      for m in my_recieved:
        sender = m['sender']
        for r in m['resource']:
          for o in offers_sent:
            if o['reciever'] == sender and o['resource'] == r['resource']:
              my_recieved.pop(my_recieved.index(m))
              print('sent resource', o['resource'])

      
      print('requested resources', rec)

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
      print(my_creds)
      '''for key in self.policy:
         if isinstance(self.policy[key],list):
           intersect = list( set(self.policy[key]) & set(self.credentials_recieved)) #self.credentials_recieved
           print('intersect', intersect, key)
           #print('intersection of sets', list(set(intersect).intersection(set(rec))))
           if set(intersect) == set(self.policy[key]):
             if(self.holders[key] == self.name):
                return_list.append(key)
             else:
              #if(set(intersect).intersection(set(rec)) == set(rec)):
              return_list.extend(self.policy[key])'''
      for r in rec:
        if(set(my_creds).intersection(set(r)) == set(r)):
          return_list.extend(list(set(my_creds).intersection(set(r))))
          print('intersection to send ',set(my_creds).intersection(set(r)))
      print('return ', return_list)
      print('\n')
      sender = self.findSender(my_recieved,return_list)
      
      print('sender',sender)
      if len(return_list) == 1:
        return [{'type':'offer', 'sender': self.name, 'reciever': sender, 'resource': return_list[0]}]
      elif len(return_list) > 1:
        return [{'type':'offer', 'sender': self.name, 'reciever': sender, 'resource': return_list}]

        
if __name__ == "__main__":
    client = Peers(name='client')
    rs = Peers(name='rs')
    as_1 = Peers(name='as_1')
    as_2 = Peers(name='as_2')

    message = {'type': 'request', 'sender': 'client', 'reciever': 'rs', 'resource': [{'resource': 'c1', 'issuer': 'rs'}]}
    queue = [message]

    Mrec = []
    Msent = []

    def processMessage(m):
      Mrec.append(m)
      sent = {}
      if m['reciever'] == 'client':
        sent = client.resolver(m,Mrec,Msent)
      elif m['reciever'] == 'rs':
        sent = rs.resolver(m,Mrec,Msent)
      elif m['reciever'] == 'as_1':
        sent = as_1.resolver(m,Mrec,Msent)
      elif m['reciever'] == 'as_2':
        sent = as_2.resolver(m,Mrec,Msent)
      if sent != None:
        Msent.append(m)
        for s in sent:
          queue.append(s)
    while(queue != []):
      m = queue.pop(0)
      if isinstance(m,dict):
        processMessage(m)
      else:
        Mrec.append(m)
        print(m)
    print(*Mrec, sep='\n')
