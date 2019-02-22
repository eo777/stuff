import math
class PowerTrust():


  """
  network = networkX network
  alpha = weight of powernodes (see PowerTrust paper)
  epsilon = error threshold for convergance (see PowerTrust paper)
  powernode ratio = ratio of powernodes to other nodes (0.01 in PowerTrust paper)
  """

  def __init__(self,network=None,alpha=0.15,epsilon=0.0001,powernode_ratio=0.01):
    self.powernodes = []
    self.network = network
    self.num_powernodes = 0
    self.powernode_ratio = powernode_ratio

    self.epsilon = epsilon #error threshold
    self.alpha = alpha #weight of powernodes
    self.global_reputation_vector = {} #global reputation vector

    self.initial_aggregation = True #initial aggregation works differently
    self.initialize_network()


  """
  Initializes the network
  """
  def initialize_network(self):
    nodes = self.network.nodes
    for n in nodes:
      self.initialize_node(n)



  """
  Initializes the nodes to hold some of the required data
  """
  def initialize_node(self,n,use_weights=False):
    self.network.nodes[n]['global_reputation'] = 1.0/len(self.network.nodes)
    self.global_reputation_vector[n] = 1.0/len(self.network.nodes)
    self.network.nodes[n]['powernode'] = False




  def get_top_m_nodes(self,m):
    sorted_nodes = sorted(list(self.network.nodes(data=True)), key=lambda x: x[1]['global_reputation'],reverse=True)
    return [x[0] for x in sorted_nodes[:m]]


  """
  Gets the powernodes from the top M nodes
  """
  def get_powernodes(self):

    m = int(math.ceil(self.powernode_ratio * len(self.network.nodes)))
    sorted_nodes = sorted(list(self.network.nodes(data=True)), key=lambda x: x[1]['global_reputation'],reverse=True)
    self.powernodes = [x[0] for x in sorted_nodes[:m]]

    for k in self.network.nodes:
      if k in self.powernodes:
        self.network.nodes[k]['powernode'] = True
      else:
        self.network.nodes[k]['powernode'] = False

    return self.powernodes
  """
  Adds a transaction, where node j is rating node k
  j = node rating k
  k = being rated by j
  was_satisfied = whether j was satisfied by the transaction (True/False)
  """
  def add_transaction(self,j,k,was_satisfied):
    if j not in self.network.nodes:
      self.network.add_node(j)
      self.initialize_node(j)
    if k not in self.network.nodes:
      self.network.add_node(k)
      self.initialize_node(k)


    if k not in self.network.successors(j):
        if was_satisfied:
          self.network.add_edge(j,k,weight=1.0,trust=1.0,distrust=0.0)
        else:
          self.network.add_edge(j,k,weight=1.0,trust=0.0,distrust=1.0)
        return

    self.network[j][k]['weight'] = self.network[j][k]['weight'] + 1.0

    if was_satisfied:
      self.network[j][k]['trust'] += 1.0
    else:
      self.network[j][k]['distrust'] += 1.0



  def remove_negative_edges(self):
    for edge in self.network.edges(data=True):
      if edge[2]['weight_n'] < 0:
        self.network.remove_edge(edge[0],edge[1])


  """
  Gets node j's opinion of node K
  """
  def get_peer_rating(self,j,k,method='sum'):

    if k not in self.network.successors(j):
      return 0.0

    if method=='avg':
      return self.network[j][k]['trust']/(self.network[j][k]['trust']+self.network[j][k]['distrust'])

    return self.network[j][k]['trust']

  """
  Gets the normalized local reputation score from node j to node k
  """
  def normalized_local_reputation(self,j,k):

    #if j is unaware of k return 0
    if k not in self.network.successors(j):
      return 0.0

    local_trust_sum = sum([self.get_peer_rating(j,t) for t in self.network.successors(j)])

    if local_trust_sum > 0.0:
      peer_trust = self.get_peer_rating(j,k)
      self.network[j][k]['normalized_trust'] = float(peer_trust)/local_trust_sum
    else:
      self.network[j][k]['normalized_trust'] = 0.0

    self.network[j][k]['weight'] = self.network[j][k]['normalized_trust']

    return self.network[j][k]['normalized_trust']


  """
  Aggregates the global reputation vector for the entire network
  """
  def aggregate_global_reputation(self):

    global_reputation_vector = {}

    if self.initial_aggregation:
      self.initialize_network()
    else:
      self.get_powernodes()

    for i in self.network.nodes():
      global_reputation = self.node_global_reputation(i)
      self.network.nodes[i]['global_reputation'] = global_reputation
      global_reputation_vector[i] = global_reputation

    #The initial aggregation works slightly differently (Algorithm 2 in the PowerTrust paper)
    #this re-aggregates to get the first actual rankings
    if self.initial_aggregation:
      self.initial_aggregation = False
      global_reputation_vector = self.aggregate_global_reputation()

    self.global_reputation_vector = global_reputation_vector
    return global_reputation_vector

  """
  Provides the ratings matrix r_ij,the normalized trust matrix c_ij, and the node names
  """
  def get_normalized_trust_matrix(self):
    nodes = list(self.network.nodes)
    normalized_matrix = [[0 for x in range(len(nodes))] for y in range(len(nodes))]
    matrix = [[0 for x in range(len(nodes))] for y in range(len(nodes))]

    print len(nodes)
    for i in range(0,len(nodes)):
      for k in range(0,len(nodes)):

        node_i = nodes[i]
        node_k = nodes[k]

        #if node_i != node_k:
        normalized_matrix[i][k] = self.normalized_local_reputation(node_i,node_k)
        matrix[i][k] = self.get_peer_rating(node_i,node_k)
         #matrix[i][k] = local_trust

    return matrix,normalized_matrix,nodes


  """
  Gets the global reputation score for node i
  (Algorithm 3 in the PowerTrust paper)
  """
  def node_global_reputation(self,i):
    nodes = self.network.nodes
    epsilon = self.epsilon
    vk = nodes[i]['global_reputation']
    pre = vk;
    sigma = 1.0

    while (sigma > epsilon):
      pre = vk;
      total = 0.0;
      for j in self.network.predecessors(i):

            vj = self.global_reputation_vector[j]
            rji = self.normalized_local_reputation(j,i)
            total += vj * rji

      if self.initial_aggregation:
        vk = total

      else:
        alpha = self.alpha
        m = self.powernode_ratio
        if self.network.nodes[i]['powernode']:
            vk = (1.0 - alpha)*total + (m/alpha);
        else:
            vk = (1.0 - alpha)*total;

      sigma = abs(vk-pre)

    return vk
