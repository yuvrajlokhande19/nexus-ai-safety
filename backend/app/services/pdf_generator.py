import logging
import os
from typing import Dict, Any, List, Optional
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.linecharts import HorizontalLineChart
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.piecharts import Pie
from io import BytesIO
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import networkx as nx
from ..models import ExperimentState, ExperimentMetrics, PersonaState

logger = logging.getLogger(__name__)


class PDFGenerator:
    """Generates comprehensive PDF reports for experiments"""
    
    def __init__(self):
        self.colors = {
            'primary': HexColor('#2563EB'),
            'secondary': HexColor('#7C3AED'),
            'success': HexColor('#10B981'),
            'warning': HexColor('#F59E0B'),
            'danger': HexColor('#EF4444'),
            'dark': HexColor('#1F2937'),
            'light': HexColor('#F9FAFB'),
            'gray': HexColor('#9CA3AF')
        }
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        self.styles.add(ParagraphStyle(
            'CustomTitle', parent=self.styles['Title'],
            fontSize=24, textColor=self.colors['dark'],
            spaceAfter=6, alignment=TA_CENTER
        ))
        self.styles.add(ParagraphStyle(
            'CustomHeading1', parent=self.styles['Heading1'],
            fontSize=18, textColor=self.colors['primary'],
            spaceBefore=16, spaceAfter=8
        ))
        self.styles.add(ParagraphStyle(
            'CustomHeading2', parent=self.styles['Heading2'],
            fontSize=14, textColor=self.colors['secondary'],
            spaceBefore=12, spaceAfter=6
        ))
        self.styles.add(ParagraphStyle(
            'CustomBody', parent=self.styles['Normal'],
            fontSize=10, leading=14, alignment=TA_JUSTIFY,
            spaceAfter=6
        ))
        self.styles.add(ParagraphStyle(
            'CustomCode', parent=self.styles['Code'],
            fontSize=8, leading=10, fontName='Courier'
        ))
    
    def generate_report(self, experiment: ExperimentState, output_path: str) -> str:
        """Generate full PDF report"""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=72, leftMargin=72,
            topMargin=72, bottomMargin=72
        )
        
        story = []
        
        # Cover page
        story.extend(self._build_cover_page(experiment))
        story.append(PageBreak())
        
        # Table of contents (manual)
        story.extend(self._build_toc())
        story.append(PageBreak())
        
        # Experiment configuration
        story.extend(self._build_config_section(experiment))
        story.append(PageBreak())
        
        # Persona profiles
        story.extend(self._build_persona_section(experiment))
        story.append(PageBreak())
        
        # Interaction timeline
        story.extend(self._build_timeline_section(experiment))
        story.append(PageBreak())
        
        # Network analysis
        story.extend(self._build_network_section(experiment))
        story.append(PageBreak())
        
        # Metrics and charts
        story.extend(self._build_metrics_section(experiment))
        story.append(PageBreak())
        
        # Deception/Alignment analysis
        story.extend(self._build_alignment_section(experiment))
        story.append(PageBreak())
        
        # Conclusions
        story.extend(self._build_conclusions_section(experiment))
        
        doc.build(story)
        logger.info(f"PDF report generated: {output_path}")
        return output_path
    
    def _build_cover_page(self, experiment: ExperimentState) -> List:
        story = []
        story.append(Spacer(1, 2*inch))
        story.append(Paragraph("NEXUS", self.styles['CustomTitle']))
        story.append(Paragraph("AI Safety Research Platform", self.styles['Heading2']))
        story.append(Spacer(1, 0.5*inch))
        story.append(Paragraph(experiment.config.name, self.styles['Heading1']))
        story.append(Spacer(1, 0.3*inch))
        story.append(Paragraph(experiment.config.description, self.styles['CustomBody']))
        story.append(Spacer(1, 1*inch))
        
        meta_data = [
            ['Experiment ID:', experiment.config.id[:8]],
            ['Date:', experiment.started_at.strftime('%Y-%m-%d %H:%M') if experiment.started_at else 'N/A'],
            ['Status:', experiment.status.capitalize()],
            ['Personas:', str(len(experiment.config.personas))],
            ['Rounds Completed:', f"{experiment.current_round}/{experiment.config.rounds}"],
            ['Total Messages:', str(len(experiment.messages))],
        ]
        meta_table = Table(meta_data, colWidths=[2*inch, 3*inch])
        meta_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('TEXTCOLOR', (0, 0), (-1, -1), self.colors['dark']),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(meta_table)
        story.append(Spacer(1, 1*inch))
        story.append(Paragraph("CONFIDENTIAL - RESEARCH USE ONLY", ParagraphStyle(
            'Confidential', parent=self.styles['Normal'],
            fontSize=10, textColor=self.colors['gray'], alignment=TA_CENTER
        )))
        return story
    
    def _build_toc(self) -> List:
        story = [Paragraph("Table of Contents", self.styles['CustomHeading1'])]
        toc_items = [
            "1. Experiment Configuration",
            "2. Persona Profiles",
            "3. Interaction Timeline",
            "4. Network Analysis",
            "5. Metrics & Visualizations",
            "6. Deception & Alignment Analysis",
            "7. Conclusions & Recommendations",
        ]
        for item in toc_items:
            story.append(Paragraph(item, ParagraphStyle(
                'TOCItem', parent=self.styles['Normal'],
                fontSize=12, leading=20, leftIndent=20
            )))
        return story
    
    def _build_config_section(self, experiment: ExperimentState) -> List:
        story = [Paragraph("1. Experiment Configuration", self.styles['CustomHeading1'])]
        
        config = experiment.config
        data = [
            ['Parameter', 'Value'],
            ['Name', config.name],
            ['Description', config.description],
            ['Topic', config.topic],
            ['Rounds', str(config.rounds)],
            ['Max Messages/Round', str(config.max_messages_per_round)],
            ['Metrics Tracked', ', '.join(config.metrics)],
            ['Initial Resources', str(len(config.initial_resources))],
        ]
        table = Table(data, colWidths=[2*inch, 4*inch])
        table.setStyle(self._default_table_style())
        story.append(table)
        return story
    
    def _build_persona_section(self, experiment: ExperimentState) -> List:
        story = [Paragraph("2. Persona Profiles", self.styles['CustomHeading1'])]
        
        for persona in experiment.config.personas:
            story.append(Paragraph(persona.name, self.styles['CustomHeading2']))
            
            profile_data = [
                ['Attribute', 'Value'],
                ['Age', str(persona.age)],
                ['Gender', persona.gender.value.capitalize()],
                ['Assigned Model', persona.assigned_model.capitalize()],
                ['Background', persona.background[:100] + '...' if len(persona.background) > 100 else persona.background],
                ['Speaking Style', persona.speaking_style],
                ['Values', ', '.join(persona.values)],
                ['Biases', '; '.join(persona.biases)],
            ]
            
            # OCEAN traits
            traits = persona.ocean_traits
            profile_data.extend([
                ['Openness', f"{traits.openness:.2f}"],
                ['Conscientiousness', f"{traits.conscientiousness:.2f}"],
                ['Extraversion', f"{traits.extraversion:.2f}"],
                ['Agreeableness', f"{traits.agreeableness:.2f}"],
                ['Neuroticism', f"{traits.neuroticism:.2f}"],
            ])
            
            table = Table(profile_data, colWidths=[1.5*inch, 4.5*inch])
            table.setStyle(self._default_table_style())
            story.append(table)
            story.append(Spacer(1, 0.2*inch))
        
        return story
    
    def _build_timeline_section(self, experiment: ExperimentState) -> List:
        story = [Paragraph("3. Interaction Timeline", self.styles['CustomHeading1'])]
        
        # Group messages by round
        chat_messages = [m for m in experiment.messages if m.type.value == 'chat']
        
        if not chat_messages:
            story.append(Paragraph("No chat messages recorded.", self.styles['CustomBody']))
            return story
        
        # Sample key messages (first, middle, last of each round)
        story.append(Paragraph(f"Total messages: {len(chat_messages)}", self.styles['CustomBody']))
        story.append(Spacer(1, 0.1*inch))
        
        # Show message flow summary
        by_sender = {}
        for msg in chat_messages:
            by_sender[msg.sender_name] = by_sender.get(msg.sender_name, 0) + 1
        
        data = [['Persona', 'Messages Sent']]
        for name, count in sorted(by_sender.items(), key=lambda x: -x[1]):
            data.append([name, str(count)])
        
        table = Table(data, colWidths=[3*inch, 1*inch])
        table.setStyle(self._default_table_style())
        story.append(table)
        
        return story
    
    def _build_network_section(self, experiment: ExperimentState) -> List:
        story = [Paragraph("4. Network Analysis", self.styles['CustomHeading1'])]
        
        # Network stats
        if hasattr(experiment, 'network') and experiment.network:
            stats = self._calculate_network_stats(experiment.network)
            
            story.append(Paragraph("4.1 Network Statistics", self.styles['CustomHeading2']))
            data = [['Metric', 'Value']]
            for key, value in stats.items():
                data.append([key.replace('_', ' ').title(), f"{value:.3f}" if isinstance(value, float) else str(value)])
            table = Table(data, colWidths=[3*inch, 1*inch])
            table.setStyle(self._default_table_style())
            story.append(table)
            
            # Centrality
            story.append(Paragraph("4.2 Centrality Measures", self.styles['CustomHeading2']))
            centrality = self._calculate_centrality(experiment.network)
            if centrality:
                data = [['Persona', 'Degree', 'Betweenness', 'PageRank']]
                for pid, vals in centrality.items():
                    persona = experiment.network.nodes.get(pid)
                    if persona:
                        data.append([
                            persona.profile.name,
                            f"{vals.get('degree', 0):.3f}",
                            f"{vals.get('betweenness', 0):.3f}",
                            f"{vals.get('pagerank', 0):.3f}"
                        ])
                table = Table(data, colWidths=[2*inch, 1.3*inch, 1.3*inch, 1.3*inch])
                table.setStyle(self._default_table_style())
                story.append(table)
            
            # Network visualization
            story.append(Paragraph("4.3 Network Visualization", self.styles['CustomHeading2']))
            img_path = self._generate_network_image(experiment.network)
            if img_path:
                story.append(Image(img_path, width=5*inch, height=3.5*inch))
        
        return story
    
    def _build_metrics_section(self, experiment: ExperimentState) -> List:
        story = [Paragraph("5. Metrics & Visualizations", self.styles['CustomHeading1'])]
        
        if experiment.metrics_history:
            story.append(Paragraph("5.1 Metrics Over Time", self.styles['CustomHeading2']))
            
            # Generate charts for key metrics
            metrics_to_plot = ['polarization_index', 'network_modularity', 'avg_trust', 'message_count']
            for metric in metrics_to_plot:
                if any(metric in m for m in experiment.metrics_history):
                    img_path = self._generate_metric_chart(experiment.metrics_history, metric)
                    if img_path:
                        story.append(Paragraph(f"{metric.replace('_', ' ').title()}", self.styles['CustomHeading2']))
                        story.append(Image(img_path, width=5*inch, height=2.5*inch))
                        story.append(Spacer(1, 0.1*inch))
        
        return story
    
    def _build_alignment_section(self, experiment: ExperimentState) -> List:
        story = [Paragraph("6. Deception & Alignment Analysis", self.styles['CustomHeading1'])]
        
        story.append(Paragraph("6.1 Belief Tracking", self.styles['CustomHeading2']))
        story.append(Paragraph(
            "This section analyzes the alignment between personas' private beliefs and public statements, "
            "which is a key indicator of deceptive or sycophantic behavior.",
            self.styles['CustomBody']
        ))
        
        if experiment.network and experiment.network.nodes:
            data = [['Persona', 'Topic', 'Private Belief', 'Public Stance', 'Alignment']]
            for pid, persona in experiment.network.nodes.items():
                for topic, belief in persona.cognitive.current_beliefs.items():
                    alignment = "Aligned" if abs(belief) > 0.3 else "Uncertain"
                    data.append([persona.profile.name, topic, f"{belief:.2f}", "N/A", alignment])
            
            if len(data) > 1:
                table = Table(data, colWidths=[1.2*inch, 1.2*inch, 1*inch, 1*inch, 1*inch])
                table.setStyle(self._default_table_style())
                story.append(table)
        
        story.append(Paragraph("6.2 Sycophancy Indicators", self.styles['CustomHeading2']))
        story.append(Paragraph(
            "Sycophancy detected when a persona's public agreement significantly exceeds "
            "their private belief alignment with the majority view.",
            self.styles['CustomBody']
        ))
        
        story.append(Paragraph("6.3 Power-Seeking Behavior", self.styles['CustomHeading2']))
        story.append(Paragraph(
            "Measured by network centrality combined with resource accumulation and influence over others' beliefs.",
            self.styles['CustomBody']
        ))
        
        # NEW: Relationship Analysis
        story.append(Paragraph("6.4 Relationship Dynamics", self.styles['CustomHeading2']))
        story.append(Paragraph(
            "Analysis of how relationships evolved during the experiment, including "
            "friendship formation, rivalries, and trust networks.",
            self.styles['CustomBody']
        ))
        
        if experiment.network and experiment.network.nodes:
            # Relationship distribution
            rel_types = {}
            total_rels = 0
            for persona in experiment.network.nodes.values():
                for target_id, rel in persona.relationships.items():
                    rel_type = rel.relationship_type.value
                    rel_types[rel_type] = rel_types.get(rel_type, 0) + 1
                    total_rels += 1
            
            if total_rels > 0:
                story.append(Paragraph("Relationship Type Distribution:", self.styles['CustomBody']))
                data = [['Relationship Type', 'Count', 'Percentage']]
                for rel_type, count in sorted(rel_types.items(), key=lambda x: -x[1]):
                    pct = (count / total_rels) * 100
                    data.append([rel_type.replace('_', ' ').title(), str(count), f"{pct:.1f}%"])
                
                table = Table(data, colWidths=[2*inch, 1*inch, 1.5*inch])
                table.setStyle(self._default_table_style())
                story.append(table)
                story.append(Spacer(1, 0.2*inch))
            
            # Top relationships
            story.append(Paragraph("Strongest Relationships:", self.styles['CustomBody']))
            all_rels = []
            for pid, persona in experiment.network.nodes.items():
                for target_id, rel in persona.relationships.items():
                    all_rels.append((persona.profile.name, rel.target_name, rel.get_relationship_label(), rel.affinity, rel.trust))
            
            if all_rels:
                all_rels.sort(key=lambda x: -x[3])  # Sort by affinity
                data = [['Persona A', 'Persona B', 'Type', 'Affinity', 'Trust']]
                for a, b, label, affinity, trust in all_rels[:10]:
                    data.append([a, b, label, f"{affinity:.2f}", f"{trust:.2f}"])
                
                table = Table(data, colWidths=[1.3*inch, 1.3*inch, 1.2*inch, 1*inch, 1*inch])
                table.setStyle(self._default_table_style())
                story.append(table)
        
        return story
    
    def _build_conclusions_section(self, experiment: ExperimentState) -> List:
        story = [Paragraph("7. Conclusions & Recommendations", self.styles['CustomHeading1'])]
        
        conclusions = [
            f"The experiment '{experiment.config.name}' completed {experiment.current_round} rounds "
            f"with {len(experiment.config.personas)} personas.",
            f"Total of {len(experiment.messages)} messages exchanged.",
            "Key findings will be populated based on metric analysis.",
            "",
            "Recommendations for future experiments:",
            "• Increase persona diversity for more robust emergence",
            "• Add more granular belief tracking",
            "• Implement human-in-the-loop intervention points",
            "• Extend experiment duration for longitudinal effects",
        ]
        
        for c in conclusions:
            if c.startswith("•"):
                story.append(Paragraph(c, ParagraphStyle('Bullet', parent=self.styles['Normal'], leftIndent=20)))
            else:
                story.append(Paragraph(c, self.styles['CustomBody']))
        
        return story
    
    def _default_table_style(self) -> TableStyle:
        return TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.colors['primary']),
            ('TEXTCOLOR', (0, 0), (-1, 0), HexColor('#FFFFFF')),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('GRID', (0, 0), (-1, -1), 0.5, self.colors['gray']),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [HexColor('#FFFFFF'), HexColor('#F3F4F6')]),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ])
    
    def _calculate_network_stats(self, network) -> Dict[str, float]:
        """Calculate network statistics"""
        import networkx as nx
        G = nx.Graph()
        for pid in network.nodes:
            G.add_node(pid)
        for edge in network.edges.values():
            G.add_edge(edge.source, edge.target, weight=edge.weight)
        
        if G.number_of_nodes() == 0:
            return {}
        
        return {
            'density': nx.density(G),
            'avg_clustering': nx.average_clustering(G, weight='weight') if G.number_of_edges() > 0 else 0,
            'avg_path_length': nx.average_shortest_path_length(G, weight='weight') if nx.is_connected(G) else 0,
            'modularity': self._calculate_modularity(G),
        }
    
    def _calculate_modularity(self, G) -> float:
        try:
            import community as community_louvain
            partition = community_louvain.best_partition(G, weight='weight')
            communities = [set(n for n, c in partition.items() if c == i) for i in set(partition.values())]
            return nx.algorithms.community.modularity(G, communities, weight='weight')
        except:
            return 0.0
    
    def _calculate_centrality(self, network) -> Dict[str, Dict[str, float]]:
        import networkx as nx
        G = nx.Graph()
        for pid in network.nodes:
            G.add_node(pid)
        for edge in network.edges.values():
            G.add_edge(edge.source, edge.target, weight=edge.weight)
        
        if G.number_of_nodes() == 0:
            return {}
        
        centrality = {}
        deg = nx.degree_centrality(G)
        bet = nx.betweenness_centrality(G, weight='weight')
        pr = nx.pagerank(G, weight='weight')
        
        for node in G.nodes():
            centrality[node] = {
                'degree': deg.get(node, 0),
                'betweenness': bet.get(node, 0),
                'pagerank': pr.get(node, 0)
            }
        return centrality
    
    def _generate_network_image(self, network) -> Optional[str]:
        """Generate network visualization as image"""
        try:
            import networkx as nx
            G = nx.Graph()
            for pid, persona in network.nodes.items():
                G.add_node(pid, name=persona.profile.name, gender=persona.profile.gender.value)
            for edge in network.edges.values():
                G.add_edge(edge.source, edge.target, weight=edge.weight)
            
            if G.number_of_nodes() == 0:
                return None
            
            plt.figure(figsize=(8, 6))
            pos = nx.spring_layout(G, k=2, iterations=50)
            
            # Node colors by gender
            node_colors = []
            for node in G.nodes():
                persona = network.nodes.get(node)
                if persona:
                    node_colors.append('#EC4899' if persona.profile.gender.value == 'female' else '#3B82F6')
                else:
                    node_colors.append('#9CA3AF')
            
            # Edge weights
            edge_weights = [G[u][v]['weight'] * 3 for u, v in G.edges()]
            
            nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=500, alpha=0.9)
            nx.draw_networkx_edges(G, pos, width=edge_weights, alpha=0.5, edge_color='#9CA3AF')
            nx.draw_networkx_labels(G, pos, {n: network.nodes[n].profile.name[:8] for n in G.nodes()}, font_size=8)
            
            plt.title("Persona Interaction Network")
            plt.axis('off')
            plt.tight_layout()
            
            img_path = "/tmp/network_viz.png"
            plt.savefig(img_path, dpi=150, bbox_inches='tight')
            plt.close()
            return img_path
        except Exception as e:
            logger.error(f"Network visualization failed: {e}")
            return None
    
    def _generate_metric_chart(self, metrics_history: List[Dict], metric: str) -> Optional[str]:
        """Generate metric over time chart"""
        try:
            rounds = [m.get('round_number', i) for i, m in enumerate(metrics_history)]
            values = [m.get(metric, 0) for m in metrics_history]
            
            if not any(v != 0 for v in values):
                return None
            
            plt.figure(figsize=(8, 4))
            plt.plot(rounds, values, marker='o', linewidth=2, markersize=6, color='#2563EB')
            plt.fill_between(rounds, values, alpha=0.1, color='#2563EB')
            plt.title(metric.replace('_', ' ').title())
            plt.xlabel('Round')
            plt.ylabel('Value')
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            
            img_path = f"/tmp/metric_{metric}.png"
            plt.savefig(img_path, dpi=150, bbox_inches='tight')
            plt.close()
            return img_path
        except Exception as e:
            logger.error(f"Metric chart generation failed: {e}")
            return None


pdf_generator = PDFGenerator()