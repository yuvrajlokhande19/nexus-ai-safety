import logging
import networkx as nx
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from ..models import NetworkGraph, NetworkEdge, Message, PersonaState, Relationship, RelationshipType

logger = logging.getLogger(__name__)


class NetworkEngine:
    """Manages social network dynamics between personas including relationships"""
    
    def __init__(self):
        self.graph = NetworkGraph()
        self.nx_graph = nx.Graph()
    
    def initialize(self, personas: Dict[str, PersonaState]):
        """Initialize network with personas"""
        self.graph.nodes = {pid: p for pid, p in personas.items()}
        self.graph.edges = {}
        self.nx_graph.clear()
        self.nx_graph.add_nodes_from(personas.keys())
        logger.info(f"Network initialized with {len(personas)} nodes")
    
    def add_interaction(
        self,
        source: str,
        target: str,
        sentiment: float,
        agreement: float,
        message_type: str = "chat",
        was_supportive: bool = False,
        was_betrayal: bool = False
    ):
        """Record an interaction and update edge weights + relationships"""
        # Update network edge
        self.graph.add_interaction(source, target, sentiment, agreement)
        
        # Update relationship on edge
        edge_key = self.graph.get_edge_key(source, target)
        edge = self.graph.edges[edge_key]
        
        # Update networkx graph for analytics
        if source in self.nx_graph and target in self.nx_graph:
            self.nx_graph.add_edge(source, target, weight=edge.weight, agreement=edge.agreement_score)
        
        # Update persona relationships
        source_persona = self.graph.nodes.get(source)
        target_persona = self.graph.nodes.get(target)
        
        if source_persona and target_persona:
            # Update source's relationship to target
            self._update_relationship(source_persona, target_persona, sentiment, agreement, was_supportive, was_betrayal)
            # Update target's relationship to source (reciprocal but asymmetric)
            self._update_relationship(target_persona, source_persona, sentiment, agreement, was_supportive, was_betrayal)
            
            # Sync edge with relationship data
            rel = source_persona.relationships.get(target)
            if rel:
                edge.relationship_type = rel.relationship_type.value
                edge.affinity = rel.affinity
                edge.trust = rel.trust
                edge.intimacy = rel.intimacy
    
    def _update_relationship(
        self,
        source_persona: PersonaState,
        target_persona: PersonaState,
        sentiment: float,
        agreement: float,
        was_supportive: bool,
        was_betrayal: bool
    ):
        """Update a persona's relationship with another"""
        target_id = target_persona.profile.id
        
        if target_id not in source_persona.relationships:
            source_persona.relationships[target_id] = Relationship(
                target_id=target_id,
                target_name=target_persona.profile.name
            )
        
        rel = source_persona.relationships[target_id]
        rel.update_from_interaction(sentiment, agreement, was_supportive, was_betrayal)
        
        # Update cognitive trust level
        source_persona.cognitive.trust_levels[target_id] = rel.trust
    
    def process_message(self, message: Message, all_personas: Dict[str, PersonaState]):
        """Process a message and update network based on recipients"""
        sender = message.sender_id
        
        # Determine targets
        if message.target_ids:
            targets = message.target_ids
        else:
            # Broadcast to all other active personas
            targets = [pid for pid, p in all_personas.items() if pid != sender and p.is_active]
        
        sender_persona = all_personas.get(sender)
        
        for target in targets:
            target_persona = all_personas.get(target)
            if not target_persona:
                continue
            
            # Calculate agreement based on beliefs
            agreement = self._calculate_agreement(sender_persona, target_persona, message)
            
            # Determine if supportive or betrayal
            was_supportive = self._is_supportive(message, sender_persona, target_persona)
            was_betrayal = self._is_betrayal(message, sender_persona, target_persona)
            
            self.add_interaction(
                sender, target, 
                message.sentiment or 0.0, 
                agreement,
                message.type.value,
                was_supportive,
                was_betrayal
            )
    
    def _calculate_agreement(self, sender: PersonaState, target: PersonaState, message: Message) -> float:
        """Calculate agreement between sender and target on message topic"""
        if not sender or not target:
            return 0.5
        
        # Extract topic from message (simplified)
        topic = self._extract_topic(message.content)
        
        sender_belief = sender.cognitive.current_beliefs.get(topic, 0.0)
        target_belief = target.cognitive.current_beliefs.get(topic, 0.0)
        
        # Agreement = 1 - normalized difference
        return 1.0 - abs(sender_belief - target_belief) / 2.0
    
    def _extract_topic(self, content: str) -> str:
        """Extract topic from message content (simplified)"""
        # In a real implementation, this would use NLP
        # For now, use a simple keyword extraction
        keywords = ['ai', 'climate', 'politics', 'technology', 'science', 'art', 'music', 'games', 'school', 'friends', 'family', 'future', 'ethics', 'safety', 'alignment']
        content_lower = content.lower()
        for kw in keywords:
            if kw in content_lower:
                return kw
        return 'general'
    
    def _is_supportive(self, message: Message, sender: PersonaState, target: PersonaState) -> bool:
        """Determine if message was supportive"""
        if not sender or not target:
            return False
        
        # Supportive if positive sentiment and high agreement
        if (message.sentiment or 0) > 0.3:
            topic = self._extract_topic(message.content)
            target_belief = target.cognitive.current_beliefs.get(topic, 0.0)
            # Agreeing with target's belief
            if abs(message.sentiment - target_belief) < 0.3:
                return True
        
        # Explicitly supportive language
        supportive_words = ['agree', 'support', 'yes', 'exactly', 'totally', 'same', 'me too', 'understand', 'here for you']
        content_lower = message.content.lower()
        return any(word in content_lower for word in supportive_words)
    
    def _is_betrayal(self, message: Message, sender: PersonaState, target: PersonaState) -> bool:
        """Determine if message was a betrayal"""
        if not sender or not target:
            return False
        
        # Betrayal if high trust but negative sentiment/opposition
        trust = sender.cognitive.trust_levels.get(target.profile.id, 0.5)
        if trust > 0.7 and (message.sentiment or 0) < -0.3:
            return True
        
        # Sharing private info (would need tracking)
        betrayal_words = ['betray', 'lie', 'fake', 'pretend', 'manipulate', 'used me']
        content_lower = message.content.lower()
        return any(word in content_lower for word in betrayal_words)
    
    def get_network_data(self) -> Dict[str, Any]:
        """Get network data for visualization including relationships"""
        nodes = []
        for pid, persona in self.graph.nodes.items():
            # Get relationship summary
            relationships = {}
            for target_id, rel in persona.relationships.items():
                relationships[target_id] = {
                    "type": rel.relationship_type.value,
                    "affinity": rel.affinity,
                    "trust": rel.trust,
                    "intimacy": rel.intimacy,
                    "label": rel.get_relationship_label()
                }
            
            nodes.append({
                "id": pid,
                "name": persona.profile.name,
                "gender": persona.profile.gender.value,
                "avatar_seed": persona.profile.avatar_seed,
                "message_count": persona.message_count,
                "emotional_valence": persona.cognitive.emotional_valence,
                "arousal": persona.cognitive.arousal,
                "assigned_model": persona.profile.assigned_model,
                "traits": persona.profile.ocean_traits.model_dump(),
                "relationships": relationships,
                "autonomy": persona.cognitive.autonomy_level,
                "social_battery": persona.cognitive.social_battery,
                "goals": persona.cognitive.current_goals
            })
        
        edges = []
        for edge_key, edge in self.graph.edges.items():
            edges.append({
                "source": edge.source,
                "target": edge.target,
                "weight": edge.weight,
                "interaction_count": edge.interaction_count,
                "avg_sentiment": edge.avg_sentiment,
                "agreement_score": edge.agreement_score,
                "last_interaction": edge.last_interaction.isoformat(),
                "relationship_type": edge.relationship_type,
                "affinity": edge.affinity,
                "trust": edge.trust,
                "intimacy": edge.intimacy
            })
        
        return {"nodes": nodes, "edges": edges}
    
    def compute_centrality(self) -> Dict[str, Dict[str, float]]:
        """Compute various centrality measures"""
        if self.nx_graph.number_of_nodes() == 0:
            return {}
        
        try:
            centrality = {}
            deg = nx.degree_centrality(self.nx_graph)
            bet = nx.betweenness_centrality(self.nx_graph, weight='weight')
            try:
                eig = nx.eigenvector_centrality(self.nx_graph, weight='weight', max_iter=1000)
            except:
                eig = {n: 0.0 for n in self.nx_graph.nodes()}
            pr = nx.pagerank(self.nx_graph, weight='weight')
            
            for node in self.nx_graph.nodes():
                centrality[node] = {
                    "degree": deg.get(node, 0),
                    "betweenness": bet.get(node, 0),
                    "eigenvector": eig.get(node, 0),
                    "pagerank": pr.get(node, 0)
                }
            return centrality
        except Exception as e:
            logger.error(f"Centrality computation failed: {e}")
            return {}
    
    def detect_communities(self) -> Dict[str, int]:
        """Detect communities using Louvain method"""
        try:
            import community as community_louvain
            partition = community_louvain.best_partition(self.nx_graph, weight='weight')
            return partition
        except ImportError:
            try:
                components = list(nx.connected_components(self.nx_graph))
                partition = {}
                for i, comp in enumerate(components):
                    for node in comp:
                        partition[node] = i
                return partition
            except:
                return {}
        except Exception as e:
            logger.error(f"Community detection failed: {e}")
            return {}
    
    def get_relationship_network(self) -> Dict[str, Dict[str, Dict]]:
        """Get full relationship network"""
        network = {}
        for pid, persona in self.graph.nodes.items():
            network[pid] = {}
            for target_id, rel in persona.relationships.items():
                network[pid][target_id] = {
                    "type": rel.relationship_type.value,
                    "affinity": rel.affinity,
                    "trust": rel.trust,
                    "respect": rel.respect,
                    "intimacy": rel.intimacy,
                    "shared_experiences": rel.shared_experiences,
                    "support_count": rel.support_count,
                    "betrayal_count": rel.betrayal_count,
                    "label": rel.get_relationship_label()
                }
        return network
    
    def get_influence_network(self) -> Dict[str, List[Dict]]:
        """Get directed influence edges (who influences whom)"""
        influence = {}
        for edge_key, edge in self.graph.edges.items():
            # Influence flows from higher agreement + more interactions + trust
            influence_score = edge.agreement_score * edge.trust * (1 - 1/(edge.interaction_count + 1))
            
            if edge.source not in influence:
                influence[edge.source] = []
            influence[edge.source].append({
                "target": edge.target,
                "influence": influence_score,
                "interactions": edge.interaction_count,
                "trust": edge.trust
            })
            
            if edge.target not in influence:
                influence[edge.target] = []
            influence[edge.target].append({
                "source": edge.source,
                "influence": influence_score,
                "interactions": edge.interaction_count,
                "trust": edge.trust
            })
        
        return influence
    
    def get_polarization_index(self) -> float:
        """Calculate network polarization (0 = consensus, 1 = fully polarized)"""
        if self.nx_graph.number_of_nodes() < 2:
            return 0.0
        
        try:
            communities = self.detect_communities()
            if not communities:
                return 0.0
            
            modularity = nx.algorithms.community.modularity(
                self.nx_graph, 
                [set(n for n, c in communities.items() if c == i) for i in set(communities.values())],
                weight='weight'
            )
            return min(1.0, max(0.0, modularity * 2))
        except:
            return 0.0
    
    def get_network_stats(self) -> Dict[str, Any]:
        """Get comprehensive network statistics"""
        n_nodes = self.nx_graph.number_of_nodes()
        n_edges = self.nx_graph.number_of_edges()
        
        if n_nodes == 0:
            return {}
        
        density = nx.density(self.nx_graph)
        avg_clustering = nx.average_clustering(self.nx_graph, weight='weight') if n_edges > 0 else 0
        
        # Relationship stats
        total_relationships = 0
        avg_affinity = 0
        relationship_types = {}
        
        for persona in self.graph.nodes.values():
            for rel in persona.relationships.values():
                total_relationships += 1
                avg_affinity += rel.affinity
                rel_type = rel.relationship_type.value
                relationship_types[rel_type] = relationship_types.get(rel_type, 0) + 1
        
        avg_affinity = avg_affinity / total_relationships if total_relationships > 0 else 0
        
        return {
            "nodes": n_nodes,
            "edges": n_edges,
            "density": density,
            "avg_clustering": avg_clustering,
            "polarization": self.get_polarization_index(),
            "components": nx.number_connected_components(self.nx_graph),
            "centrality": self.compute_centrality(),
            "communities": self.detect_communities(),
            "relationships": {
                "total": total_relationships,
                "avg_affinity": avg_affinity,
                "types": relationship_types
            }
        }


network_engine = NetworkEngine()