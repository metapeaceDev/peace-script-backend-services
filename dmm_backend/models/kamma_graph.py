"""
Kamma-Vipāka Graph Models

Data models for representing kamma-vipāka relationships as a graph structure.
Used by Kamma-Vipāka Explorer visualization feature.

Author: PeaceScript Team
Date: 6 November 2024
Version: 1.0
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Literal
from datetime import datetime
from uuid import uuid4


class KammaNode(BaseModel):
    """
    Node ในกราฟกรรม-วิบาก แทนเหตุการณ์กรรมหรือวิบากหนึ่งเหตุการณ์
    
    Attributes:
        id: Unique identifier (auto-generated if not provided)
        type: ประเภท node
            - "kamma": กรรม (เหตุ)
            - "vipaka": วิบาก (ผล)
            - "neutral": เหตุการณ์กลางๆ (ไม่ใช่กรรมที่แรง)
        label: ชื่อเหตุการณ์ (ไทย/อังกฤษ) สั้นๆ กระชับ
        life_index: ชีวิตที่เกิดเหตุการณ์
            - 0 = ชีวิตปัจจุบัน
            - -1 = ชีวิตที่แล้ว
            - -12 = 12 ชาติก่อน
        date: วันที่เกิดเหตุการณ์
        realm: ภพภูมิที่เกิดเหตุการณ์ (มนุษย์, เทวดา, อสูร, เปรต, สัตว์นรก, สัตว์เดรัจฉาน)
        weight: น้ำหนักความสำคัญ/ความแรง (0.0 - 1.0)
            - 0.0 - 0.3: เบา
            - 0.3 - 0.6: ปานกลาง
            - 0.6 - 0.8: หนัก
            - 0.8 - 1.0: หนักมาก (มหันตกรรม)
        tags: Tags สำหรับ categorization เช่น ["kusala", "generosity"], ["akusala", "anger"]
        kamma_record_id: Link ไปยัง KammaRecord ถ้า node นี้ถูกสร้างจากมัน
        metadata: ข้อมูลเพิ่มเติม (emotion, description, context, etc.)
    
    Examples:
        >>> node = KammaNode(
        ...     type="kamma",
        ...     label="ช่วยเหลือคนแปลกหน้า",
        ...     life_index=-2,
        ...     date=datetime.now(),
        ...     realm="มนุษย์",
        ...     weight=0.7,
        ...     tags=["kusala", "generosity", "compassion"]
        ... )
    """
    
    id: str = Field(
        default_factory=lambda: f"node_{uuid4().hex[:8]}",
        description="Unique node identifier",
        examples=["node_a1b2c3d4", "node_xyz789"]
    )
    
    type: Literal["kamma", "vipaka", "neutral", "kusala", "akusala"] = Field(
        ...,
        alias="node_type",
        serialization_alias="node_type",
        description="Node type: kamma (cause), vipaka (result), neutral, kusala, akusala"
    )
    
    label: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Event label (Thai/English)",
        examples=["Betrayed ally's trust for gain", "ทรยศต่อพันธมิตรเพื่อผลประโยชน์"]
    )
    
    life_index: int = Field(
        ...,
        ge=-12,
        le=0,
        description="Life index: -12 (12 lives ago) to 0 (present)"
    )
    
    date: datetime = Field(
        ...,
        description="Event date (can be approximate for past lives)"
    )
    
    realm: str = Field(
        ...,
        description="Realm where event occurred",
        examples=["มนุษย์", "เทวดา", "อสูร", "เปรต", "สัตว์นรก", "สัตว์เดรัจฉาน"]
    )
    
    weight: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Weight/importance/intensity (0.0 - 1.0)"
    )
    
    tags: List[str] = Field(
        default_factory=list,
        description="Tags for categorization",
        examples=[["kusala", "generosity"], ["akusala", "anger", "violence"]]
    )
    
    kamma_record_id: Optional[str] = Field(
        None,
        description="Link to KammaRecord if this node was created from it"
    )
    
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata (emotion, description, context, etc.)"
    )
    
    class Config:
        populate_by_name = True  # Allow both 'type' and 'node_type'
        json_schema_extra = {
            "example": {
                "id": "node_a1b2c3d4",
                "type": "kamma",
                "label": "Betrayed ally's trust for gain",
                "life_index": -3,
                "date": "2024-03-15T10:30:00Z",
                "realm": "มนุษย์",
                "weight": 0.85,
                "tags": ["akusala", "betrayal", "greed"],
                "kamma_record_id": "record_xyz789",
                "metadata": {
                    "emotion": "guilt",
                    "kamma_type": "akusala",
                    "strength": "heavy",
                    "description": "ในสงครามกษัตริย์ ทรยศต่อพันธมิตรเพื่อได้ดินแดน",
                    "context": "war"
                }
            }
        }


class KammaEdge(BaseModel):
    """
    Edge ระหว่าง nodes แสดงความสัมพันธ์เหตุ-ผล
    
    Attributes:
        id: Unique identifier
        from_node: Source node ID (เหตุ)
        to_node: Target node ID (ผล)
        kind: ประเภทความสัมพันธ์
            - "cause": A เป็นเหตุของ B (กรรม → วิบาก)
            - "result": A เป็นผลของ B (วิบาก ← กรรม)
            - "support": A สนับสนุน/เสริมแรง B (กรรมเกื้อกูลกัน)
            - "obstruct": A ขัดขวาง/ลดทอน B (กรรมตัดกัน)
        strength: ความแข็งแกร่งของความสัมพันธ์ (0.0 - 1.0)
            - 0.0 - 0.3: อ่อน (weak causal link)
            - 0.3 - 0.7: ปานกลาง (moderate)
            - 0.7 - 1.0: แข็งแรง (strong direct causality)
        metadata: ข้อมูลเพิ่มเติม (description, timing, etc.)
    
    Examples:
        >>> edge = KammaEdge(
        ...     from_node="node_a1b2c3d4",
        ...     to_node="node_e5f6g7h8",
        ...     kind="cause",
        ...     strength=0.9,
        ...     metadata={"description": "กรรมทรยศ → วิบากสูญเสียความเชื่อถือ"}
        ... )
    """
    
    id: str = Field(
        default_factory=lambda: f"edge_{uuid4().hex[:8]}",
        description="Unique edge identifier",
        examples=["edge_m9n0p1q2", "edge_abc123"]
    )
    
    from_node: str = Field(
        ...,
        description="Source node ID (เหตุ)",
        examples=["node_a1b2c3d4"]
    )
    
    to_node: str = Field(
        ...,
        description="Target node ID (ผล)",
        examples=["node_e5f6g7h8"]
    )
    
    kind: Literal["cause", "result", "support", "obstruct"] = Field(
        ...,
        description="Relationship type"
    )
    
    strength: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Relationship strength (0.0 - 1.0)"
    )
    
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "edge_m9n0p1q2",
                "from_node": "node_a1b2c3d4",
                "to_node": "node_e5f6g7h8",
                "kind": "cause",
                "strength": 0.9,
                "metadata": {
                    "description": "กรรมทรยศ → วิบากสูญเสียความเชื่อถือ",
                    "timing": "immediate",
                    "certainty": "high"
                }
            }
        }


class KammaGraph(BaseModel):
    """
    Complete graph structure containing nodes and edges
    
    Attributes:
        model_id: Digital Mind Model ID ที่เป็นเจ้าของกราฟนี้
        nodes: List of all nodes in graph
        edges: List of all edges in graph
        summary: Graph statistics และข้อมูลสรุป
        created_at: Graph creation timestamp
        updated_at: Last update timestamp
    
    Examples:
        >>> graph = KammaGraph(
        ...     model_id="model_abc123",
        ...     nodes=[node1, node2, node3],
        ...     edges=[edge1, edge2],
        ...     summary={
        ...         "total_nodes": 150,
        ...         "kusala_count": 90,
        ...         "akusala_count": 60
        ...     }
        ... )
    """
    
    model_id: str = Field(
        ...,
        description="Digital Mind Model ID",
        examples=["model_abc123", "dmm_xyz789"]
    )
    
    nodes: List[KammaNode] = Field(
        default_factory=list,
        description="List of nodes in the graph"
    )
    
    edges: List[KammaEdge] = Field(
        default_factory=list,
        description="List of edges in the graph"
    )
    
    summary: Dict[str, Any] = Field(
        default_factory=dict,
        description="Graph statistics and summary information"
    )
    
    created_at: datetime = Field(
        default_factory=datetime.now,
        description="Graph creation timestamp"
    )
    
    updated_at: datetime = Field(
        default_factory=datetime.now,
        description="Last update timestamp"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "model_id": "model_abc123",
                "nodes": [],  # See KammaNode example
                "edges": [],  # See KammaEdge example
                "summary": {
                    "total_nodes": 150,
                    "total_edges": 180,
                    "kusala_count": 90,
                    "akusala_count": 60,
                    "karma_balance": 30,
                    "life_range": [-12, 0],
                    "realms": ["มนุษย์", "เทวดา", "อสูร"],
                    "heaviest_kamma": {
                        "node_id": "node_xyz",
                        "weight": 0.95,
                        "label": "มหันตกรรม: ฆ่าพ่อแม่"
                    },
                    "most_connected_node": {
                        "node_id": "node_abc",
                        "connections": 25,
                        "label": "จุดเริ่มต้นลูกโซ่กรรม"
                    }
                },
                "created_at": "2024-11-06T10:00:00Z",
                "updated_at": "2024-11-06T10:00:00Z"
            }
        }
    
    def get_node_by_id(self, node_id: str) -> Optional[KammaNode]:
        """
        Get node by ID
        
        Args:
            node_id: Node ID to search for
            
        Returns:
            KammaNode if found, None otherwise
        """
        for node in self.nodes:
            if node.id == node_id:
                return node
        return None
    
    def get_edges_for_node(self, node_id: str) -> List[KammaEdge]:
        """
        Get all edges connected to a node
        
        Args:
            node_id: Node ID
            
        Returns:
            List of edges where node is either source or target
        """
        return [
            edge for edge in self.edges
            if edge.from_node == node_id or edge.to_node == node_id
        ]
    
    def get_predecessors(self, node_id: str) -> List[str]:
        """
        Get all predecessor nodes (nodes that point TO this node)
        
        Args:
            node_id: Node ID
            
        Returns:
            List of predecessor node IDs
        """
        return [
            edge.from_node for edge in self.edges
            if edge.to_node == node_id
        ]
    
    def get_successors(self, node_id: str) -> List[str]:
        """
        Get all successor nodes (nodes that this node points TO)
        
        Args:
            node_id: Node ID
            
        Returns:
            List of successor node IDs
        """
        return [
            edge.to_node for edge in self.edges
            if edge.from_node == node_id
        ]
    
    def update_summary(self) -> None:
        """
        Recalculate and update graph summary statistics
        """
        kusala_nodes = [
            n for n in self.nodes
            if n.type == "kamma" and any(
                tag.lower() == "kusala" or tag.lower().startswith("kusala-") or tag.lower().startswith("kusala_")
                for tag in n.tags
            )
        ]
        akusala_nodes = [
            n for n in self.nodes
            if n.type == "kamma" and any(
                tag.lower() == "akusala" or tag.lower().startswith("akusala-") or tag.lower().startswith("akusala_")
                for tag in n.tags
            )
        ]
        
        life_indices = [n.life_index for n in self.nodes] if self.nodes else [0]
        
        self.summary = {
            "total_nodes": len(self.nodes),
            "total_edges": len(self.edges),
            "kusala_count": len(kusala_nodes),
            "akusala_count": len(akusala_nodes),
            "karma_balance": len(kusala_nodes) - len(akusala_nodes),
            "life_range": [min(life_indices), max(life_indices)],
            "realms": list(set(n.realm for n in self.nodes)),
            "avg_weight": sum(n.weight for n in self.nodes) / len(self.nodes) if self.nodes else 0.0
        }
        
        # Find heaviest kamma
        if self.nodes:
            heaviest = max(self.nodes, key=lambda n: n.weight)
            self.summary["heaviest_kamma"] = {
                "node_id": heaviest.id,
                "weight": heaviest.weight,
                "label": heaviest.label
            }
        
        # Find most connected node
        if self.nodes:
            node_connections = {
                node.id: len(self.get_edges_for_node(node.id))
                for node in self.nodes
            }
            most_connected_id = max(node_connections, key=lambda k: node_connections[k])
            most_connected_node = self.get_node_by_id(most_connected_id)
            
            if most_connected_node:
                self.summary["most_connected_node"] = {
                    "node_id": most_connected_id,
                    "connections": node_connections[most_connected_id],
                    "label": most_connected_node.label
                }
        
        self.updated_at = datetime.now()


# Export all models
__all__ = ["KammaNode", "KammaEdge", "KammaGraph"]
