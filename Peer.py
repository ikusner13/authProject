# Each peer is set up knowing the policy of the resource exhanges, along with knowing know holds each resource 

''' 

### MESSAGE FORMAT ###

message format is {type: String, sender: String, reciever: String, resource: List[] or String}

request is a List if type is 'request'. request can be a String if type is 'offer'



inside request is {request: List or String, issuer: String} if type is 'request'. {request: List or String} if type is 'offer'
if only one credential is requested, then request should be String, not List. If multiple use List


### PEER ###

Peer is set up so each peer will hold the policy of the exchange system (locks or unlocks of resources)

Peer will hold the credentials that it recieves as offers from other resources 

Peer will also be initialized knowing which peer holds what resource 


### POLICY ###

Policy format is {resource: resources required or True(no additional resources required)}

if resources are required, resources must be in array 
ex. 'c1':['c2','c3'] , 'c3': ['c4']

if no additional resources are required, format is { 'resource': True }



### OUTPUT ###

program will output a success message if the initial request was able to be completed

program will out an error message if there was an error with the initial request (lik requesting an invalid resource)

Change 'showMessages' flag below to show/hide the message chain of the authorization
'''
showMessages = True

class Peers:
  def __init__(self,name):
    self.name = name # name of Peer (client, rs, as_1, as_2)
    self.policy = {
      'c1': ['c2','c3'],
      'c2': True,
      'c3': ['c4'],
      'c4': True
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
      for m in messages:
        resources = []
        for r in m['resource']:
          if(isinstance(r['resource'],list)):
            resources.extend(r['resource'])
          else:
            resources.append(r['resource'])
        if set(resources) == set(return_list):
          return m['sender']


  # checks if any resources in the list are unlocked(able to be sent back) or locked(not able to be)
  def isResourceUnlocked(self,resources,credentials):
      valid = True
      for item in resources:
        for r in item:
          if(isinstance(r,list)):
            for c in r:
              if(self.holders[c] == self.name):
               if(isinstance(self.policy[c],list)):
                if(set(self.policy[c]).intersection(set(credentials)) == set(self.policy[c])):
                  pass
                else:
                  valid = False

          else:
            if(self.holders[r] == self.name):
              if(isinstance(self.policy[r],list)):
                if(set(self.policy[r]).intersection(set(credentials)) == set(self.policy[r])):
                  pass
                else:
                  valid = False
      return valid
  
  def requestError(self,message):
      error = False
      for resources in message['resource']:
        if(isinstance(resources['resource'],list)):
          for r in resources['resource']:
            if(r not in self.policy):
              error = True
        else:  
          if(resources['resource'] not in self.policy):
            error = True
      return error
          

  

  def resolver(self,message,Mrec):
    if(message['type'] == 'request'):

      #if request to resource that doesn't exist, then return error message
      if(self.requestError(message)):
        return [{'type':'error', 'content':'INVALID REQUEST ERROR for {}'.format(message['resource'])}]

      return_messages = []

      # all requested resources 
      req_resources = [r['resource'] for r in message['resource']]

      # if request is for list of credentials make req_resources a list instead of a list of list made above 
      if(len(req_resources) == 1 and isinstance(req_resources[0],list)):
        req_resources = req_resources[0]
        


      my_recieved = [request for request in Mrec if request['reciever'] == self.name and request['type'] == 'request']
      to_offer = []


      for requests in message['resource']:
        resource = requests['resource']

        held = [h for h in self.holders if self.holders[h] == self.name]
        have = self.credentials_recieved + held

        # make resource a list if it is not
        if not isinstance(resource,list):
          resource = [resource]

        # if reciever is the issuer of the resource 
        # or the peer has the requested resources necessary to make an offer 
        if(requests['issuer'] == self.name or set(have).intersection(req_resources) == set(req_resources)):
          for r in resource:
            needed_resources = self.policy[r]
            # if resource is unlocked by default and the peer can make an offer
            if(needed_resources == True and set(have).intersection(req_resources) == set(req_resources)):
              if r in req_resources:
                to_offer.append(r)
            elif(needed_resources != True):
              test = []

              # list of resources needed to be requested sorted by sender
              for n in needed_resources:
                issuer = self.holders[n]
                test.append({'resource': n, 'issuer': issuer})
              newList = sorted(test, key=lambda k: k['issuer'])

              # group all credentials of one issuer into one list
              # after, will have list of list of grouped credentials by issuer
              temp1 = []
              temp2 = []
              issuer = newList[0]['issuer']
              for i in newList:
                if i['issuer'] == issuer:
                  temp2.append(i)
                else:
                  temp1.append(temp2)
                  temp2 = [i]
                issuer = i['issuer']
              temp1.append(temp2)

              # make 'resource' part of message to send back to another peer to handle the requests
              arr_rec = []
              for t in temp1:
                to_send = []
                send_to = t[0]['issuer']
                for j in t:
                  to_send.append(j['resource'])
                if len(to_send) == 1:
                  arr_rec.append({'resource': to_send[0], 'issuer': send_to})
                else:
                  arr_rec.append({'resource': to_send, 'issuer':send_to })

              return_messages.append({'type': 'request', 'sender': self.name, 'reciever': message['sender'], 'resource': arr_rec})

        # credentials not unlocked and not held by peer, so make requests for them
        else:
            for r in resource:
              return_messages.append({'type': 'request', 'sender': self.name, 'reciever': self.holders[r], 'resource': [{'resource': r, 'issuer': self.holders[r]}]})

      if len(to_offer) > 0:
        if len(to_offer) == 1:
          return_messages.append({'type': 'offer', 'sender': self.name, 'reciever': message['sender'], 'resource': to_offer[0]})
        else:
          return_messages.append({'type': 'offer', 'sender': self.name, 'reciever': message['sender'], 'resource': to_offer})
      
      # list of messages being sent back
      return return_messages


    if(message['type'] == 'offer'):

      #if offer is of resource initially requested then the auth has successfully completed 
      for r in Mrec[0]['resource']:
        if(set(r['resource']) == set(message['resource'])):
          return [{'type':'success','content': 'resource {} was succesfully recieved'.format(message['resource']) }]

      # add offer of resource to peers recieved credentials 
      if isinstance(message['resource'],list):
        for creds in message['resource']:
          self.credentials_recieved.append(creds)
      else:
        self.credentials_recieved.append(message['resource'])

      # requests to peer 
      my_recieved = [request for request in Mrec if request['reciever'] == self.name and request['type'] == 'request']

      # offers that peer has sent 
      offers_sent = [request for request in Mrec if request['sender'] == self.name and request['type'] == 'offer']

      rec = []
      unsent = []

      # finds which requests that the peer has already sent offers for 
      #print('my_recieved',*my_recieved,sep='\n')
      for m in my_recieved:
        sender = m['sender']
        rrecieved = []
        for r in m['resource']:
          if(isinstance(r['resource'],list)):
            for c in r['resource']:
              rrecieved.append(c)
          else:
            rrecieved.append(r['resource'])
        for o in offers_sent:
          offers = set()
          if not isinstance(o['resource'],list):
            offers.add(o['resource'])
          else:
            offers = set(o['resource'])
          
         #print('offers',offers)
         # print('rrecieved',rrecieved)
          if(offers == set(rrecieved) and o['reciever'] == sender):
            unsent.append(m)
        
      # remove requests that have already been offered 
      for messages in unsent:
        my_recieved.pop(my_recieved.index(messages))

      # make list of resources by request that still need to be offered by the peer 
      for r in my_recieved:
        temp = []
        for res in r['resource']:
          if(isinstance(res['resource'],list)):
            temp.extend(res['resource'])
          else:
            temp.append(res['resource'])
        rec.append(temp)

      return_list = []

      # make list of all credentials that the peer has ( resources it's the holder of, and resources it recieved from other peers )
      held = [h for h in self.holders if self.holders[h] == self.name]
      my_creds = held + self.credentials_recieved

      # check if resources that still need to be offered are unlocked 
      valid = self.isResourceUnlocked(rec,my_creds)

      # offer is able to be made from request 
      if(valid):
        for r in rec:
          # if peer has all the credentials needed to complete the request 
          if(set(my_creds).intersection(set(r)) == set(r)):
              return_list.extend(list(set(my_creds).intersection(set(r))))
        # based on resources being offered, find sender of request for all those resources
        sender = self.findSender(my_recieved,return_list)
        if(sender == None and len(return_list) > 0):
          return [{'type':'error', 'content': 'error completing request'}]
        
        # either send one resource as an offer, or send a list of resources as an offer
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

    # send message to appropriate reciever
    def processMessage(m):
      Mrec.append(m)
      sent = []
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

    while(queue != [] ):
      m = queue.pop(0)
      if m['type'] == 'success' or m['type'] == 'error':
        print(m['content'])
        print('\n')
        break;
      else:
        processMessage(m)

    #if last offer isnt for first response then auth failed
    initialMessage = Mrec[0]['resource'][0]['resource']

    lastOffer = ''
    if(Mrec[-1]['type'] == 'offer'):
      lastOffer = Mrec[-1]['resource']
    if(initialMessage != lastOffer):
      print('Could not complete request for {}'.format(initialMessage))


    if(showMessages):
      print(*Mrec, sep='\n')
